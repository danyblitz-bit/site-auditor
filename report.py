"""Report formatting — print, CSV export, JSON export."""
import csv
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


def print_report(result: dict):
    console = Console()

    score = result["score"]
    color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "D" if score >= 60 else "F"

    header = Text()
    header.append("  SiteAudit Report\n", style="bold")
    header.append(f"  {result['url']}\n\n", style="dim")
    header.append(f"  Score: {score}/100 ", style=f"bold {color}")
    header.append(f"(Grade {grade})\n", style=f"bold {color}")

    resp = result["response"]
    if resp:
        header.append(f"\n  Status: {resp.get('status', '?')}  |  Time: {resp.get('time_ms', '?')}ms  |  Size: {resp.get('size_bytes', 0) // 1024} KB\n", style="dim")

    console.print(Panel(header, border_style=color))

    if result["issues"]:
        t = Table(title="Issues", show_header=False, padding=(0, 1))
        t.add_column(style="red bold")
        for issue in result["issues"]:
            t.add_row(f"  X  {issue}")
        console.print(t)

    if result["warnings"]:
        t = Table(title="Warnings", show_header=False, padding=(0, 1))
        t.add_column(style="yellow")
        for w in result["warnings"]:
            t.add_row(f"  !  {w}")
        console.print(t)

    if result["info"]:
        for info in result["info"]:
            console.print(f"  i  {info}", style="dim")

    seo = result.get("seo", {})
    if seo:
        t = Table(title="SEO", show_header=False, padding=(0, 1))
        t.add_column(style="cyan", width=20)
        t.add_column()
        t.add_row("Title", seo.get("title", "(empty)") or "(empty)")
        t.add_row("Description", (seo.get("description", "") or "(empty)")[:80])
        t.add_row("H1 tags", str(seo.get("h1_count", 0)))
        t.add_row("Images", f"{seo.get('total_images', 0)} total, {seo.get('images_missing_alt', 0)} missing alt")
        t.add_row("Open Graph", "Yes" if seo.get("open_graph") else "No")
        t.add_row("Viewport", "Yes" if seo.get("has_viewport") else "No")
        t.add_row("Canonical", "Yes" if seo.get("has_canonical") else "No")
        console.print(t)

    perf = result.get("performance", {})
    if perf:
        t = Table(title="Performance", show_header=False, padding=(0, 1))
        t.add_column(style="cyan", width=20)
        t.add_column()
        t.add_row("Page size", f"{perf.get('page_size_kb', 0)} KB")
        t.add_row("Scripts", str(perf.get("total_scripts", 0)))
        t.add_row("Stylesheets", str(perf.get("total_stylesheets", 0)))
        t.add_row("Gzip", "Yes" if perf.get("gzip_enabled") else "No")
        t.add_row("Caching", "Yes" if perf.get("caching") else "No")
        t.add_row("HSTS", "Yes" if perf.get("hsts") else "No")
        t.add_row("CSP", "Yes" if perf.get("csp") else "No")
        console.print(t)

    links = result.get("links", {})
    if links.get("checked", 0) > 0:
        t = Table(title="Links", show_header=False, padding=(0, 1))
        t.add_column(style="cyan", width=20)
        t.add_column()
        t.add_row("Checked", str(links["checked"]))
        t.add_row("Broken", f"{links['broken']} found" if links["broken"] else "None")
        t.add_row("Broken URLs", ", ".join(d["url"][:60] for d in links.get("details", [])[:5]) or "N/A")
        console.print(t)


def export_csv(result: dict, path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Category", "Check", "Value", "Severity", "Score Impact"])
        w.writerow(["General", "URL", result["url"], "info", ""])
        w.writerow(["General", "Score", result["score"], "info", ""])
        resp = result.get("response", {})
        w.writerow(["Response", "Status", resp.get("status", ""), "info", ""])
        w.writerow(["Response", "Time (ms)", resp.get("time_ms", ""), "info", ""])
        for issue in result["issues"]:
            w.writerow(["Issue", issue, "", "critical", "-"])
        for warn in result["warnings"]:
            w.writerow(["Warning", warn, "", "warning", "-"])
        seo = result.get("seo", {})
        for k, v in seo.items():
            w.writerow(["SEO", k, str(v), "info", ""])
        perf = result.get("performance", {})
        for k, v in perf.items():
            if k != "headers":
                w.writerow(["Performance", k, str(v), "info", ""])
        links = result.get("links", {})
        w.writerow(["Links", "Checked", links.get("checked", 0), "info", ""])
        w.writerow(["Links", "Broken", links.get("broken", 0), "warning" if links.get("broken", 0) > 0 else "info", ""])
        for d in links.get("details", []):
            w.writerow(["Broken Link", d["url"], d["status"], "critical", "-"])


def export_json(result: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
