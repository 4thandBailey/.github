import requests
import json
from datetime import datetime, timezone
from dateutil import parser as dateparser

def fetch_cisa_kev():
    """Fetch the 5 most recently added CISA Known Exploited Vulnerabilities."""
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        vulns = data.get("vulnerabilities", [])
        # Sort by dateAdded descending and take top 5
        sorted_vulns = sorted(vulns, key=lambda x: x.get("dateAdded", ""), reverse=True)
        return sorted_vulns[:5]
    except Exception as e:
        print(f"Error fetching CISA KEV: {e}")
        return []

def build_threat_section(vulns):
    """Build the Markdown section for the README."""
    now = datetime.now(timezone.utc).strftime("%B %d, %Y at %H:%M UTC")

    if not vulns:
        return f"""
## 🔐 Live Threat Intelligence — CISA Known Exploited Vulnerabilities

> ⚠️ Feed temporarily unavailable. Check back shortly.
> *Last attempted: {now}*
"""

    lines = [
        "",
        "## 🔐 Live Threat Intelligence",
        "",
        "**CISA Known Exploited Vulnerabilities — Recently Added**",
        "",
        "These vulnerabilities are actively being exploited in the wild.",
        "Source: [CISA KEV Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)",
        "",
        "| CVE ID | Vendor / Product | Vulnerability | Due Date |",
        "|---|---|---|---|",
    ]

    for v in vulns:
        cve_id    = v.get("cveID", "N/A")
        vendor    = v.get("vendorProject", "N/A")
        product   = v.get("product", "N/A")
        vuln_name = v.get("vulnerabilityName", "N/A")
        due_date  = v.get("dueDate", "N/A")
        cve_link  = f"[{cve_id}](https://nvd.nist.gov/vuln/detail/{cve_id})"
        lines.append(f"| {cve_link} | {vendor} / {product} | {vuln_name} | {due_date} |")

    lines += [
        "",
        f"> *Updated automatically every 24 hours. Last update: {now}*",
        ">",
        "> 💡 **Is your organization exposed?** "
        "[Start with a Security Posture Review →](https://www.4thandbailey.com/contact)",
        "",
    ]

    return "\n".join(lines)

def update_readme(new_section):
    """Replace the threat intel section in README.md."""
    # Organization .github repository — README is at root, not profile/README.md
    readme_path = "README.md"

    with open(readme_path, "r") as f:
        content = f.read()

    start_marker = "<!-- THREAT_INTEL_START -->"
    end_marker   = "<!-- THREAT_INTEL_END -->"

    new_block = f"{start_marker}\n{new_section}\n{end_marker}"

    if start_marker in content and end_marker in content:
        # Replace existing section
        start_idx = content.index(start_marker)
        end_idx   = content.index(end_marker) + len(end_marker)
        updated   = content[:start_idx] + new_block + content[end_idx:]
    else:
        # Append to end of file
        updated = content.rstrip() + "\n\n" + new_block + "\n"

    with open(readme_path, "w") as f:
        f.write(updated)

    print(f"README.md updated successfully.")

if __name__ == "__main__":
    print("Fetching CISA Known Exploited Vulnerabilities...")
    vulns   = fetch_cisa_kev()
    section = build_threat_section(vulns)
    update_readme(new_section=section)
    print("Done.")
