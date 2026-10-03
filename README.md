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

## Don't want to run it yourself?

SiteAuditor is free and always will be. But the report is only half of the work —
the other half is knowing which of those findings actually costs you traffic and
what to change.

That's what I do for €49: I run the audit on your site, read the results, and send
you a PDF with the problems ranked by impact and the exact fix for each one. Report
within 24 hours. No subscription, nothing to install.

[**Get your site audited — €49**](https://danyblitz.gumroad.com/l/jsuyla)

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

SiteAuditor is free and open source. Like it?

- [Get your site audited — €49](https://danyblitz.gumroad.com/l/jsuyla) — I run the audit and send you the fixes
- [Get your site audited — €49](https://danyblitz.gumroad.com/l/jsuyla) — I run the audit and send you the fixes
- [Buy me a coffee](https://danyblitz.gumroad.com/l/hrvpiu) — one-time support

## Report a bug

Found a bug or something weird? Run:

```bash
python -m tools.site-auditor https://your-site.com --report
```

This opens a pre-filled email with your audit data. Send it and I'll get notified automatically.

You can also email **danyblitz@googlemail.com** directly. Use the subject format:

```
[TOOL-REPORT] site-auditor <what happened>
```

Attach the log or error output if you have one.

## License

MIT