from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_URL = "https://static-file-global.353355.xyz/rules/cn-additional-list.txt"
OUTPUT_PATH = Path("CN-Additional.list")


def fetch_source() -> str:
    request = Request(
        SOURCE_URL,
        headers={"User-Agent": "Rongwuyou-Surge-Rules/1.0"},
    )
    with urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8-sig")


def convert(text: str) -> tuple[list[str], str | None]:
    domains: list[str] = []
    seen: set[str] = set()
    source_updated: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if "Updated:" in line:
                source_updated = line.split("Updated:", 1)[1].strip()
            continue

        domain = line.lstrip(".").lower()
        if domain in seen:
            continue
        seen.add(domain)
        domains.append(domain)

    return domains, source_updated


def render(domains: list[str], source_updated: str | None) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    header = [
        "# CN Additional Rules for Surge",
        f"# Source: {SOURCE_URL}",
        f"# Source Updated: {source_updated or 'unknown'}",
        f"# Generated: {generated_at}",
        f"# Total Rules: {len(domains)}",
        "",
    ]
    rules = [f"DOMAIN-SUFFIX,{domain}" for domain in domains]
    return "\n".join(header + rules) + "\n"


def main() -> None:
    source = fetch_source()
    domains, source_updated = convert(source)
    if not domains:
        raise RuntimeError("Source list is empty after conversion")

    output = render(domains, source_updated)
    OUTPUT_PATH.write_text(output, encoding="utf-8", newline="\n")
    print(f"Wrote {len(domains)} rules to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
