#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scrape and store the Wiktionary page for each verb in a CSV list.
Saves raw HTML as "<verb>.html" (or into --outdir if provided).

Usage:
  python scrape_wiktionary_verbs.py \
      --csv /path/to/3000-russian-verbs-by-class.csv \
      --lemma-col lemma \
      --outdir wiktionary_html \
      --delay 1.5 \
      --force
"""

import argparse
import csv
import os
import re
import time
import unicodedata
from typing import Iterable, Set, Optional

import requests
from urllib.parse import quote

WIKTIONARY_BASE = "https://en.wiktionary.org/wiki/"

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scrape Wiktionary pages for verbs and save raw HTML.")
    p.add_argument("--csv", required=True, help="Path to CSV file containing verbs.")
    p.add_argument("--lemma-col", default="lemma",
                   help="Column name in the CSV that contains the verb (default: lemma).")
    p.add_argument("--outdir", default="wiktionary_html",
                   help="Directory to save .html files (default: wiktionary_html).")
    p.add_argument("--delay", type=float, default=1.5,
                   help="Delay (seconds) between requests to be polite (default: 1.5).")
    p.add_argument("--force", action="store_true",
                   help="Re-download and overwrite existing .html files.")
    p.add_argument("--timeout", type=float, default=20.0,
                   help="HTTP timeout in seconds (default: 20).")
    p.add_argument("--max-retries", type=int, default=3,
                   help="Max per-verb retries on network errors (default: 3).")
    return p.parse_args()

def read_verbs_from_csv(path: str, lemma_col: str) -> Iterable[str]:
    # Stream CSV to support big files; auto-detect delimiter
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        # sniff delimiter
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample)
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(f, dialect=dialect)
        if lemma_col not in (reader.fieldnames or []):
            raise ValueError(f"Column '{lemma_col}' not found. Available: {reader.fieldnames}")
        for row in reader:
            lemma = (row.get(lemma_col) or "").strip()
            if lemma:
                yield lemma

def unique_ordered(seq: Iterable[str]) -> Iterable[str]:
    seen: Set[str] = set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            yield x

def sanitize_filename(name: str) -> str:
    """
    Keep the verb as the filename, but strip forbidden characters on most filesystems.
    Cyrillic is allowed; remove slashes and control chars, collapse whitespace.
    """
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)   # Windows-forbidden
    name = re.sub(r"\s+", " ", name).strip()
    return name

def build_url(verb: str) -> str:
    # Wiktionary page titles are UTF-8; URL-encode the whole title
    return WIKTIONARY_BASE + quote(verb, safe="")

def fetch_html(session: requests.Session, url: str, timeout: float) -> requests.Response:
    # Follow redirects (e.g., capitalization or normalization)
    resp = session.get(url, timeout=timeout, allow_redirects=True)
    return resp

def write_html(outdir: str, verb: str, content: bytes) -> str:
    fname = sanitize_filename(verb) + ".html"
    path = os.path.join(outdir, fname)
    with open(path, "wb") as f:
        f.write(content)
    return path

def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    # Prepare an HTTP session with a polite User-Agent
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0.0.0 Safari/537.36 "
            "(research script for Wiktionary; contact: example@example.com)"
        )
    })

    verbs = list(unique_ordered(read_verbs_from_csv(args.csv, args.lemma_col)))
    total = len(verbs)

    print(f"Verbs to fetch: {total}")
    print(f"Output directory: {args.outdir}")
    print(f"Delay between requests: {args.delay}s\n")

    successes = 0
    failures = 0
    skipped = 0

    for i, verb in enumerate(verbs, 1):
        out_path = os.path.join(args.outdir, sanitize_filename(verb) + ".html")
        if os.path.exists(out_path) and not args.force:
            skipped += 1
            print(f"[{i}/{total}] SKIP  {verb}  (exists)")
            continue

        url = build_url(verb)

        # Retry with backoff for transient errors
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = fetch_html(session, url, timeout=args.timeout)
                if resp.status_code == 200:
                    write_html(args.outdir, verb, resp.content)
                    successes += 1
                    print(f"[{i}/{total}] OK    {verb}  → {resp.url}")
                    break
                elif resp.status_code == 404:
                    failures += 1
                    print(f"[{i}/{total}] 404   {verb}  (not found at {resp.url})")
                    # Write a small placeholder HTML for traceability
                    write_html(args.outdir, verb, f"<!-- 404 for {verb} at {resp.url} -->".encode("utf-8"))
                    break
                elif resp.status_code == 429:
                    # Too many requests — back off a bit more
                    wait = max(args.delay * 2, 5.0)
                    print(f"[{i}/{total}] 429   {verb}  (rate-limited). Sleeping {wait:.1f}s and retrying...")
                    time.sleep(wait)
                else:
                    # Other HTTP codes: retry a few times
                    if attempt < args.max_retries:
                        wait = args.delay * attempt
                        print(f"[{i}/{total}] HTTP {resp.status_code} {verb}. Retrying in {wait:.1f}s...")
                        time.sleep(wait)
                        continue
                    failures += 1
                    print(f"[{i}/{total}] FAIL  {verb}  (HTTP {resp.status_code} after {attempt} attempts)")
                    break
            except requests.RequestException as e:
                if attempt < args.max_retries:
                    wait = args.delay * attempt
                    print(f"[{i}/{total}] NET   {verb}: {e}. Retrying in {wait:.1f}s...")
                    time.sleep(wait)
                    continue
                failures += 1
                print(f"[{i}/{total}] FAIL  {verb}: {e}")
                break

        # Be polite to the server
        time.sleep(args.delay)

    print("\nDone.")
    print(f"Fetched:  {successes}")
    print(f"Skipped:  {skipped}  (already exists)")
    print(f"Failed:   {failures}")
    print(f"Saved to: {os.path.abspath(args.outdir)}")

if __name__ == "__main__":
    main()
