#!/usr/bin/env python3
"""
Fast SEO Broken Link & HTTP Status Auditor
Scans website links and identifies 404, 500 errors and redirects.
"""
import argparse, csv, sys, urllib.parse, requests
from bs4 import BeautifulSoup

def check_links(url, max_links=25):
    print(f"[*] Crawling: {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        links = [a["href"] for a in soup.find_all("a", href=True) if not a["href"].startswith(("#", "javascript:", "mailto:"))]
    except Exception as e:
        print(f"[!] Failed to fetch {url}: {e}")
        return []

    results = []
    seen = set()
    for raw in links:
        if len(results) >= max_links: break
        full_url = urllib.parse.urljoin(url, raw)
        if full_url in seen: continue
        seen.add(full_url)
        try:
            r = requests.head(full_url, headers=headers, timeout=5, allow_redirects=True)
            status = r.status_code
        except Exception:
            status = "TIMEOUT/ERROR"

        results.append({
            "Source URL": url,
            "Target Link": full_url,
            "Status Code": status,
            "Health": "OK" if status == 200 else "BROKEN / REDIRECT"
        })
        print(f"   [{status}] {full_url}")

    return results

def main():
    parser = argparse.ArgumentParser(description="Broken Link Checker CLI")
    parser.add_argument("--url", "-u", default="https://example.com", help="Target URL")
    parser.add_argument("--output", "-o", default="broken_links_report.csv", help="Output CSV")
    args = parser.parse_args()

    data = check_links(args.url)
    if data:
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)
        print(f"
[✓] Audit report saved: {args.output}")

if __name__ == "__main__":
    main()
