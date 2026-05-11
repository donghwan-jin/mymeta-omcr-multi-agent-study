"""Verify that academic citations exist and match their claimed metadata.

Hits CrossRef for DOI/metadata, OpenAlex for the abstract. Reports mismatches
against a BibTeX file, a single DOI, or a single citekey. Optionally writes the
verification verdict into a CSV summary table (the project's literature
spreadsheet) without clobbering human-curated columns.

Stdlib-only (urllib, json, csv, re). No external dependencies.

Usage:
    python3 verify_citation.py --doi 10.1038/s41586-XXXXX
    python3 verify_citation.py --bib references.bib --key smith2023connectome
    python3 verify_citation.py --bib references.bib
    python3 verify_citation.py --bib references.bib --summary-csv references.csv

Exit codes:
    0 = all PASS
    1 = at least one MISMATCH / NOT_FOUND
    2 = script error (missing file, malformed BibTeX, persistent network failure)
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

CROSSREF_BASE = "https://api.crossref.org/works"
OPENALEX_BASE = "https://api.openalex.org/works"

DEFAULT_BIB = os.environ.get("BIB_FILE", "references.bib")
DEFAULT_SUMMARY = os.environ.get("SUMMARY_FILE", "references.csv")
EMAIL = os.environ.get("CITATION_VERIFY_EMAIL", "").strip()
TIMEOUT = float(os.environ.get("CITATION_VERIFY_TIMEOUT", "15"))

SUMMARY_COLUMNS = [
    "citekey", "authors", "year", "title", "venue", "doi",
    "bucket", "our_use", "paper_says", "cited_sections",
    "verified_on", "verify_status",
]

CURATOR_ONLY_COLUMNS = {"bucket", "our_use", "paper_says", "cited_sections"}


# ---------------------------------------------------------------------------
# BibTeX parsing (minimal — handles @type{key, field = {value}, ...})
# ---------------------------------------------------------------------------

@dataclass
class BibEntry:
    citekey: str
    entrytype: str
    fields: dict = field(default_factory=dict)

    @property
    def doi(self) -> Optional[str]:
        v = (self.fields.get("doi") or "").strip()
        if not v:
            return None
        return re.sub(r"^https?://(dx\.)?doi\.org/", "", v).strip()

    @property
    def title(self) -> str:
        return (self.fields.get("title") or "").strip()

    @property
    def year(self) -> Optional[str]:
        raw = self.fields.get("year") or self.fields.get("date") or ""
        m = re.search(r"\d{4}", raw)
        return m.group(0) if m else None

    @property
    def venue(self) -> str:
        for k in ("journal", "booktitle", "publisher", "howpublished"):
            v = self.fields.get(k)
            if v:
                return v.strip()
        return ""

    @property
    def authors(self) -> list[str]:
        raw = (self.fields.get("author") or "").strip()
        if not raw:
            return []
        parts = [a.strip() for a in re.split(r"\s+and\s+", raw)]
        return [_normalize_author(a) for a in parts if a]


def _normalize_author(a: str) -> str:
    # "Last, First M." -> "First Last"; "First Last" stays as-is.
    if "," in a:
        last, first = [s.strip() for s in a.split(",", 1)]
        return f"{first} {last}".strip()
    return a


def parse_bib(path: str) -> list[BibEntry]:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    entries: list[BibEntry] = []
    i = 0
    pat = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", re.DOTALL)
    while True:
        m = pat.search(text, i)
        if not m:
            break
        entrytype = m.group(1).lower()
        citekey = m.group(2).strip()
        if entrytype in ("comment", "preamble", "string"):
            i = m.end()
            continue
        body_start = m.end()
        depth = 1
        j = body_start
        while j < len(text) and depth > 0:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        body = text[body_start:j - 1]
        fields = _parse_fields(body)
        entries.append(BibEntry(citekey=citekey, entrytype=entrytype, fields=fields))
        i = j
    return entries


def _parse_fields(body: str) -> dict:
    out: dict = {}
    i = 0
    n = len(body)
    while i < n:
        m = re.search(r"(\w+)\s*=\s*", body[i:])
        if not m:
            break
        key = m.group(1).lower()
        i += m.end()
        if i >= n:
            break
        ch = body[i]
        if ch == "{":
            depth = 1
            j = i + 1
            while j < n and depth > 0:
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                j += 1
            value = body[i + 1:j - 1]
            i = j
        elif ch == '"':
            j = i + 1
            while j < n and body[j] != '"':
                j += 1
            value = body[i + 1:j]
            i = j + 1
        else:
            j = i
            while j < n and body[j] not in ",\n":
                j += 1
            value = body[i:j].strip()
            i = j
        while i < n and body[i] in ", \n\t":
            i += 1
        out[key] = _clean_value(value)
    return out


def _clean_value(s: str) -> str:
    s = re.sub(r"[{}]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------------------------------------------------------------------------
# HTTP (stdlib only, with one retry on transient failure)
# ---------------------------------------------------------------------------

class NetworkError(RuntimeError):
    pass


def _http_get_json(url: str) -> Optional[dict]:
    ua = f"verify-citation/0.1 (mailto:{EMAIL})" if EMAIL else "verify-citation/0.1"
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "application/json"})
    last_exc: Optional[Exception] = None
    for _attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                if resp.status == 404:
                    return None
                if resp.status != 200:
                    return None
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            last_exc = e
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_exc = e
    raise NetworkError(str(last_exc)) from last_exc


def crossref_by_doi(doi: str) -> Optional[dict]:
    url = f"{CROSSREF_BASE}/{urllib.parse.quote(doi, safe='/')}"
    return _http_get_json(url)


def crossref_search(title: str, year: Optional[str], author_surname: Optional[str]) -> Optional[dict]:
    params = {"query.title": title, "rows": "3"}
    if author_surname:
        params["query.author"] = author_surname
    if year:
        params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"
    url = f"{CROSSREF_BASE}?{urllib.parse.urlencode(params)}"
    data = _http_get_json(url)
    if not data:
        return None
    items = data.get("message", {}).get("items") or []
    return items[0] if items else None


def openalex_abstract(doi: str) -> Optional[str]:
    url = f"{OPENALEX_BASE}/doi:{urllib.parse.quote(doi, safe='/')}"
    try:
        data = _http_get_json(url)
    except NetworkError:
        return None
    if not data:
        return None
    inv = data.get("abstract_inverted_index")
    if not inv:
        return None
    positions: dict[int, str] = {}
    for word, idxs in inv.items():
        for idx in idxs:
            positions[idx] = word
    return " ".join(positions[i] for i in sorted(positions))


# ---------------------------------------------------------------------------
# Comparison helpers
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    s = re.sub(r"[^\w\s]", "", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def _titles_match(a: str, b: str) -> bool:
    return _norm(a) == _norm(b) if a and b else False


def _authors_match(bib_authors: list[str], cr_authors: list[dict]) -> tuple[Optional[bool], str]:
    cr_list = [
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in cr_authors
    ]
    if not bib_authors:
        return None, "no bib authors to compare"
    if not cr_list:
        return False, "crossref returned no authors"
    bib_first = bib_authors[0].split()[-1].lower()
    cr_first = cr_list[0].split()[-1].lower() if cr_list else ""
    first_match = bib_first == cr_first
    count_match = abs(len(bib_authors) - len(cr_list)) <= 1
    if first_match and count_match:
        return True, "ok"
    if first_match:
        return False, f"author count differs (bib={len(bib_authors)} crossref={len(cr_list)})"
    return False, f"first author differs (bib='{bib_authors[0]}' crossref='{cr_list[0] if cr_list else ''}')"


# ---------------------------------------------------------------------------
# Verification core
# ---------------------------------------------------------------------------

def verify_entry(entry: BibEntry, claim: Optional[str] = None) -> dict:
    report: dict = {
        "citekey": entry.citekey,
        "status": "NOT_FOUND",
        "doi": entry.doi,
        "claim": claim,
        "notes": [],
    }
    cr_msg = None
    try:
        if entry.doi:
            cr = crossref_by_doi(entry.doi)
            if cr is None:
                report["notes"].append("DOI did not resolve at CrossRef")
            else:
                cr_msg = cr.get("message", cr)
        if cr_msg is None and entry.title:
            surname = entry.authors[0].split()[-1] if entry.authors else None
            cr_search = crossref_search(entry.title, entry.year, surname)
            if cr_search:
                cr_msg = cr_search
                report["notes"].append("matched via title search (no DOI in BibTeX or DOI failed)")
    except NetworkError as e:
        report["status"] = "NOT_VERIFIED"
        report["notes"].append(f"network error: {e}")
        return report

    if cr_msg is None:
        return report

    cr_title = (cr_msg.get("title") or [""])[0] if isinstance(cr_msg.get("title"), list) else (cr_msg.get("title") or "")
    cr_year = None
    for k in ("published-print", "published-online", "issued", "created"):
        parts = (cr_msg.get(k) or {}).get("date-parts")
        if parts:
            cr_year = str(parts[0][0])
            break
    cr_authors = cr_msg.get("author") or []
    cr_doi = (cr_msg.get("DOI") or entry.doi or "").lower()
    cr_venue = ""
    for k in ("container-title", "publisher"):
        v = cr_msg.get(k)
        if isinstance(v, list):
            v = v[0] if v else ""
        if v:
            cr_venue = v
            break

    title_ok = _titles_match(entry.title, cr_title) if entry.title else None
    authors_ok, auth_note = _authors_match(entry.authors, cr_authors)
    year_ok = (entry.year == cr_year) if (entry.year and cr_year) else None

    report["crossref"] = {
        "doi": cr_doi,
        "title": cr_title,
        "year": cr_year,
        "venue": cr_venue,
        "first_author": (
            f"{cr_authors[0].get('given', '')} {cr_authors[0].get('family', '')}".strip()
            if cr_authors else ""
        ),
        "n_authors": len(cr_authors),
    }
    report["match"] = {"title": title_ok, "authors": authors_ok, "year": year_ok}
    if authors_ok is False:
        report["notes"].append(auth_note)

    abstract = None
    if cr_doi:
        try:
            abstract = openalex_abstract(cr_doi)
        except NetworkError:
            report["notes"].append("OpenAlex unreachable; abstract not retrieved")
    if abstract:
        report["abstract"] = abstract[:1500]
    else:
        report["notes"].append("abstract unavailable from OpenAlex")

    all_match = (
        title_ok is not False
        and authors_ok is not False
        and year_ok is not False
    )
    report["status"] = "PASS" if all_match else "MISMATCH"
    return report


def verify_doi(doi: str, claim: Optional[str] = None) -> dict:
    pseudo = BibEntry(citekey=f"doi:{doi}", entrytype="article", fields={"doi": doi})
    return verify_entry(pseudo, claim=claim)


# ---------------------------------------------------------------------------
# Summary-table I/O
# ---------------------------------------------------------------------------

def read_summary(path: str) -> tuple[list[str], list[dict]]:
    """Return (columns_in_file, rows). If the file does not exist, return the
    canonical schema and an empty list."""
    if not os.path.exists(path):
        return list(SUMMARY_COLUMNS), []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames or SUMMARY_COLUMNS)
        rows = [dict(r) for r in reader]
    # Ensure every canonical column exists in the in-memory representation.
    for c in SUMMARY_COLUMNS:
        if c not in cols:
            cols.append(c)
            for r in rows:
                r.setdefault(c, "")
    return cols, rows


def write_summary(path: str, cols: list[str], rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in cols})


def update_summary(path: str, reports: list[dict], entries_by_key: dict[str, BibEntry]) -> None:
    cols, rows = read_summary(path)
    by_key = {r.get("citekey", ""): r for r in rows}
    today = _dt.date.today().isoformat()
    for rep in reports:
        ck = rep.get("citekey", "")
        if not ck or ck.startswith("doi:"):
            continue  # DOI-only verification does not have a citekey row
        row = by_key.get(ck)
        if row is None:
            row = {c: "" for c in cols}
            row["citekey"] = ck
            rows.append(row)
            by_key[ck] = row
        # Curator-only columns are never overwritten by this skill.
        # Bibliographic columns are filled (only if blank) from BibTeX / CrossRef
        # so that a fresh CSV row gets useful defaults the curator can refine.
        bib_entry = entries_by_key.get(ck)
        cr = rep.get("crossref") or {}
        defaults = {
            "authors": _short_authors_from_bib(bib_entry) if bib_entry else "",
            "year": (bib_entry.year if bib_entry else "") or cr.get("year", "") or "",
            "title": (bib_entry.title if bib_entry else "") or cr.get("title", "") or "",
            "venue": (bib_entry.venue if bib_entry else "") or cr.get("venue", "") or "",
            "doi": (bib_entry.doi if bib_entry else "") or cr.get("doi", "") or "",
        }
        for col, val in defaults.items():
            if not row.get(col):
                row[col] = val
        row["verified_on"] = today
        row["verify_status"] = rep.get("status", "NOT_VERIFIED")
    write_summary(path, cols, rows)


def _short_authors_from_bib(entry: BibEntry) -> str:
    a = entry.authors
    if not a:
        return ""
    if len(a) > 3:
        return f"{a[0].split()[-1]} et al."
    return ", ".join(s.split()[-1] for s in a)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def format_human(report: dict) -> str:
    out = [f"[{report['status']}] {report['citekey']}"]
    if report.get("doi"):
        out.append(f"  DOI:        {report['doi']}")
    if "crossref" in report:
        cr = report["crossref"]
        m = report.get("match") or {}
        out.append(f"  Title:      crossref={cr['title']!r}  match={m.get('title')}")
        more = f" (+{cr['n_authors']-1} more)" if cr.get("n_authors", 0) > 1 else ""
        out.append(f"  Author:     crossref={cr['first_author']!r}{more}  match={m.get('authors')}")
        out.append(f"  Year:       crossref={cr['year']}  match={m.get('year')}")
        if cr.get("venue"):
            out.append(f"  Venue:      crossref={cr['venue']!r}")
    if report.get("abstract"):
        abstract = report["abstract"][:500]
        out.append("  Abstract (first 500 chars):")
        out.append(f"    {abstract}")
    if report.get("claim"):
        out.append(f"  Claim:      {report['claim']}")
        out.append("  → Read abstract above and confirm whether it supports the claim.")
    for n in report.get("notes") or []:
        out.append(f"  Note:       {n}")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--doi", help="Verify a single DOI")
    src.add_argument("--bib", help="Path to BibTeX file")
    ap.add_argument("--key", help="With --bib: verify only this citekey (default: all entries)")
    ap.add_argument("--claim", help="Optional one-line claim the citation is meant to support")
    ap.add_argument("--summary-csv", default=None,
                    help=f"Project summary table to update with verified_on/verify_status (default off; "
                         f"set or use SUMMARY_FILE env var = {DEFAULT_SUMMARY!r})")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of the human report")
    args = ap.parse_args(argv)

    summary_path = args.summary_csv
    if summary_path is None and os.environ.get("SUMMARY_FILE"):
        summary_path = os.environ["SUMMARY_FILE"]

    reports: list[dict] = []
    entries_by_key: dict[str, BibEntry] = {}

    if args.doi:
        reports.append(verify_doi(args.doi, claim=args.claim))
    else:
        if not os.path.exists(args.bib):
            sys.stderr.write(f"ERROR: BibTeX file not found: {args.bib}\n")
            return 2
        try:
            entries = parse_bib(args.bib)
        except Exception as e:
            sys.stderr.write(f"ERROR: failed to parse BibTeX: {e}\n")
            return 2
        if args.key:
            entries = [e for e in entries if e.citekey == args.key]
            if not entries:
                sys.stderr.write(f"ERROR: citekey not found: {args.key}\n")
                return 2
        for e in entries:
            entries_by_key[e.citekey] = e
            reports.append(verify_entry(e, claim=args.claim))

    if summary_path and not args.doi:
        try:
            update_summary(summary_path, reports, entries_by_key)
        except OSError as e:
            sys.stderr.write(f"WARN: could not update summary CSV at {summary_path}: {e}\n")

    if args.json:
        print(json.dumps(reports, indent=2, ensure_ascii=False))
    else:
        for r in reports:
            print(format_human(r))
            print()

    failed = sum(1 for r in reports if r["status"] not in ("PASS",))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
