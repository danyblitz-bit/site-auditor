"""SiteAuditor — analyze a website's health: SEO, performance, broken links."""
import sys
import argparse
from .checker import audit_site
from .report import print_report, export_csv, export_json


def main():
    parser = argparse.ArgumentParser(
        prog="site-auditor",
        description="Audit a website for SEO, performance, and broken links.",
    )
    parser.add_argument("url", help="Target URL to audit")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds (default: 15)")
    parser.add_argument("--max-links", type=int, default=50, help="Max internal links to check (default: 50)")
    parser.add_argument("--csv", metavar="FILE", help="Export results to CSV")
    parser.add_argument("--json", metavar="FILE", help="Export results to JSON")
    parser.add_argument("--user-agent", default="SiteAuditor/1.0", help="Custom User-Agent string")
    args = parser.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = audit_site(url, timeout=args.timeout, max_links=args.max_links, user_agent=args.user_agent)
    print_report(result)

    if args.csv:
        export_csv(result, args.csv)
        print(f"\n  CSV exported to {args.csv}")
    if args.json:
        export_json(result, args.json)
        print(f"\n  JSON exported to {args.json}")

    sys.exit(0 if result["score"] >= 70 else 1)


if __name__ == "__main__":
    main()
