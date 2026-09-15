# SiteAuditor

A lightweight website health checker that audits SEO, performance, and broken links — right from your terminal.

![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Why SiteAuditor?

Most audit tools are slow web apps behind registration walls. SiteAuditor is a single command that gives you a complete audit report in seconds, no account required.

## Features

- **SEO Audit** — title, meta description, H1, Open Graph, viewport, canonical, alt text
- **Performance Check** — response time, page size, gzip, caching headers, HSTS, CSP
- **Broken Link Detection** — crawl internal links and flag 404s and failures
- **Exit Code Scoring** — `0` if score >= 70, `1` if the site needs work (perfect for CI)
- **CSV & JSON Export** — feed results to your own tooling

## Install & Run

```bash
pip install -r requirements.txt

python -m tools.site-auditor https://your-site.com
python -m tools.site-auditor https://your-site.com --json report.json --csv report.csv
```

Need a standalone `.exe`? Get the [releases](../../releases/latest) build.

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--timeout` | Request timeout in seconds | `15` |
| `--max-links` | Max internal links to check | `50` |
| `--csv FILE` | Export results to CSV | - |
| `--json FILE` | Export results to JSON | - |
| `--user-agent` | Custom User-Agent | `SiteAuditor/1.0` |

## Example Output

```
  SiteAudit Report
  https://example.com
  Score: 75/100 (Grade C)
```

## Support the Project

SiteAuditor is free and open source. Like it? Support development with a [pay-what-you-want contribution](https://danyblitz.gumroad.com), or grab the [standalone .exe](https://danyblitz.gumroad.com) if you'd rather not install Python.

## License

MIT