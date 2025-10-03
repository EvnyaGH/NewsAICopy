# test_arXiv.py
# End-to-end script to fetch arXiv Atom feed, normalize entries, and persist them.
# It supports field mapping via config.yaml and performs atomic, idempotent upserts.

import os
import sys
import time
import yaml
import json
import shutil
import tempfile
import requests
import xmltodict
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
# ========== Utilities: config and low-level helpers ==========

def load_config(path: str) -> Dict[str, Any]:
    """
    Load YAML configuration.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str):
    """
    Create the directory if it does not exist.
    """
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def arxiv_query_url(base_url: str, query: str, start: int, max_results: int) -> str:
    """
    Build arXiv Atom feed query URL.
    """
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
    }
    return f"{base_url}?{urlencode(params)}"


def http_get(url: str, timeout: int = 30) -> str:
    """
    Simple HTTP GET wrapper returning text content.
    Raises on HTTP errors.
    """
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "ai-engine/0.1"})
    resp.raise_for_status()
    return resp.text


def parse_xml(xml_text: str) -> Dict[str, Any]:
    """
    Parse Atom XML string into a dict using xmltodict.
    """
    return xmltodict.parse(xml_text, attr_prefix='@', cdata_key="#text")


def ensure_list(x):
    """
    Ensure the input is a list. Wrap scalars as single-element lists.
    """
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


# ========== Field extraction helpers ==========

def get_value_from_path(entry: Dict[str, Any], path_expr: Optional[str]) -> Any:
    """
    Resolve a "path expression" over a nested dict produced by xmltodict.
    - Dot segments navigate nested maps.
    - Use "@attr" to access attributes.
    - If any segment does not exist, return None.
    """
    if not path_expr:
        return None
    cur = entry
    for seg in path_expr.split("."):
        if cur is None:
            return None
        if isinstance(cur, list):
            # If a list is encountered, prefer the first element to continue.
            cur = cur[0] if cur else None
        if isinstance(cur, dict):
            cur = cur.get(seg)
        else:
            return None
    return cur


def extract_pdf_url(entry: Dict[str, Any]) -> Optional[str]:
    """
    Fallback extractor for PDF link when not available via extract_all_links().
    Looks for any link with type 'application/pdf'.
    """
    links = ensure_list(entry.get("link"))
    for link in links:
        if isinstance(link, dict) and link.get("@type") == "application/pdf":
            return link.get("@href")
    return None


def extract_pdf_text(pdf_url: Optional[str], tmp_dir: Optional[str] = None) -> Optional[str]:
    """
    Placeholder for PDF text extraction. Disabled by default (config.arxiv.extract_text=false).
    If you enable this, you can download the PDF to tmp_dir and run a PDF parser.
    """
    # TODO: Implement PDF fetching + text extraction if needed.
    # Returning None to keep this fast and dependency-light by default.
    return None


# ========== Normalization helpers (authors, affiliations, categories, links) ==========

def extract_authors_and_affiliations(entry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Return authors (list of {name, affiliation}) and a deduplicated list of affiliations.
    arXiv Atom uses "author": [{"name": "...", "arxiv:affiliation": "..."}]
    """
    authors = ensure_list(entry.get("author"))
    out = []
    aff_set = set()

    for a in authors:
        if not isinstance(a, dict):
            continue
        name = a.get("name")
        aff = None
        for k in ["arxiv:affiliation", "affiliation"]:
            if k in a:
                aff = a.get(k)
                break
        if aff:
            aff_set.add(aff)
        out.append({"name": name, "affiliation": aff})

    return out, sorted(list(aff_set))


def extract_all_categories(entry: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
    """
    Return (primary_category, all_categories).
    - primary comes from "arxiv:primary_category.@term"
    - all categories are gathered from "category" list items' "@term".
    """
    cats = ensure_list(entry.get("category"))
    terms = []
    for c in cats:
        if isinstance(c, dict) and "@term" in c:
            terms.append(c["@term"])

    primary = None
    pc = entry.get("arxiv:primary_category")
    if isinstance(pc, dict):
        primary = pc.get("@term")
    if primary and primary not in terms:
        terms.insert(0, primary)

    return primary, terms


def extract_all_links(entry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Optional[str], Optional[str]]:
    """
    Return (links, abs_url, pdf_url).
    Links are list of dicts with fields {rel, type, href}.
    Also extract 'abs_url' (alternate without type) and 'pdf_url' (related + application/pdf).
    """
    links = ensure_list(entry.get("link"))
    out = []
    abs_url = None
    pdf_url = None

    for link in links:
        if not isinstance(link, dict):
            continue
        rel = link.get("@rel")
        typ = link.get("@type")
        href = link.get("@href")
        if href:
            out.append({"rel": rel, "type": typ, "href": href})
        if rel == "alternate" and not typ and href and "arxiv.org/abs/" in href:
            abs_url = href
        if rel == "related" and typ == "application/pdf":
            pdf_url = href

    return out, abs_url, pdf_url


# ========== Transform one entry to our normalized record ==========

def transform_entry(entry: Dict[str, Any], config: Dict[str, Any], tmp_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Normalize a single xmltodict entry into our canonical dict expected by save_papers().
    """
    mapping = config.get("field_mapping", {})
    result: Dict[str, Any] = {}

    # 1) Map configured fields
    for db_field, path_expr in mapping.items():
        if db_field == "pdf_url":
            # Defer to extract_all_links first, then fallback
            _, _, explicit_pdf = extract_all_links(entry)
            result[db_field] = explicit_pdf or extract_pdf_url(entry)
        else:
            result[db_field] = get_value_from_path(entry, path_expr)

    # 2) Authors / affiliations
    authors, affiliations = extract_authors_and_affiliations(entry)
    result["authors"] = authors
    result["affiliations"] = affiliations

    # 3) Categories (primary + all)
    primary_cat, all_cats = extract_all_categories(entry)
    result["primary_category"] = primary_cat or result.get("primary_category")
    result["categories"] = all_cats

    # 4) Links (abs + pdf)
    links, abs_url, pdf_from_links = extract_all_links(entry)
    result["links"] = links
    result["abs_url"] = abs_url
    result["pdf_url"] = result.get("pdf_url") or pdf_from_links

    # 5) Optional: extracted text or file path
    result["file_path"] = None
    if config.get("arxiv", {}).get("extract_text", False):
        pdf_url = result.get("pdf_url")
        result["extracted_text"] = extract_pdf_text(pdf_url, tmp_dir=tmp_dir)
    else:
        result["extracted_text"] = None

    return result


# ========== Main pipeline ==========

def fetch_and_parse(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetch the arXiv feed and parse into a list of 'entry' dicts.
    """
    base_url = config["arxiv"]["base_url"]
    query = config["arxiv"]["search_query"]
    start = int(config["arxiv"].get("start", 0))
    max_results = int(config["arxiv"].get("max_results", 50))

    url = arxiv_query_url(base_url, query, start, max_results)
    xml_text = http_get(url)
    data = parse_xml(xml_text)

    # Atom has structure: feed.entry[]
    feed = data.get("feed") or {}
    entries = ensure_list(feed.get("entry"))
    return entries


def normalize_entries(entries: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Transform raw entries into the target records list.
    """
    tmp_dir = (config.get("runtime", {}) or {}).get("tmp_dir")
    ensure_dir(tmp_dir)
    out = []
    for e in entries:
        try:
            norm = transform_entry(e, config, tmp_dir=tmp_dir)
            out.append(norm)
        except Exception as ex:
            # Do not crash the whole batch; log and continue
            print(f"[WARN] Entry transform failed: {ex}", file=sys.stderr)
    return out


def persist_records(records: List[Dict[str, Any]], config: Dict[str, Any]):
    """
    Persist records using the idempotent upsert behavior.
    """
    from utils.persistence import save_papers
    pg_url = config.get("database", {}).get("postgres_url") or os.getenv(
        "POSTGRES_URL",
        "postgresql+psycopg2://airflow:airflow@localhost:5432/airflow"
    )
    save_papers(pg_url, records)


def parse_arxiv_xml(xml_content: str, field_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Parse arXiv API XML response into list of dicts based on field_mapping.

    Args:
        xml_content: Raw XML string returned by arXiv API
        field_mapping: Mapping of output keys to XML paths 
                       (defined in config/arXiv_postgre_config.yaml)

    Returns:
        List of dictionaries, each representing one arXiv paper
    """
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }

    root = ET.fromstring(xml_content)
    entries = []

    for entry in root.findall("atom:entry", ns):
        record = {}
        for key, path in field_mapping.items():
            value = None

            # Handle attributes like category.@term
            if "@" in path:
                parts = path.split("@")
                tag = parts[0].rstrip(".")
                attr = parts[1]
                el = entry.find(tag, ns)
                if el is not None and attr.startswith("."):
                    attr = attr[1:]
                if el is not None and el.get(attr):
                    value = el.get(attr)

            # Handle authors (special case: multiple values)
            elif path == "author.name":
                authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
                value = ", ".join(authors)

            # Handle link[@type='application/pdf']
            elif path.startswith("link["):
                for link in entry.findall("atom:link", ns):
                    if link.attrib.get("type") == "application/pdf":
                        value = link.attrib.get("href")
                        break

            else:
                el = entry.find(path, ns)
                if el is not None and el.text:
                    value = el.text

            record[key] = value

        entries.append(record)

    return entries

def main():
    """
    Orchestrate: load config -> fetch -> normalize -> persist.
    """
    cfg_path = os.getenv("CONFIG_PATH", "config.yaml")
    config = load_config(cfg_path)

    print("[INFO] Fetching arXiv feed...")
    entries = fetch_and_parse(config)
    print(f"[INFO] Fetched {len(entries)} entries")

    print("[INFO] Normalizing entries...")
    records = normalize_entries(entries, config)
    print(f"[INFO] Normalized {len(records)} records")

    if not records:
        print("[INFO] Nothing to save.")
        return

    print("[INFO] Persisting records...")
    persist_records(records, config)
    print(f"[INFO] Saved {len(records)} records into arxiv_papers")


if __name__ == "__main__":
    main()
