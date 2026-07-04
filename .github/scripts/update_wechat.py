#!/usr/bin/env python3
from __future__ import annotations

import ipaddress
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "WeChat.txt"

SOURCE_URLS = [
    "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Surge/WeChat/WeChat.list",
    "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/Ruleset/Wechat.list",
    "https://raw.githubusercontent.com/ConnersHua/RuleGo/master/Surge/Ruleset/Extra/WeChat.list",
]

SUPPORTED_TYPES = {
    "DOMAIN",
    "DOMAIN-SUFFIX",
    "IP-CIDR",
    "IP-CIDR6",
    "USER-AGENT",
}

DOMAIN_RE = re.compile(r"^(?:[a-z0-9_*~-]+\.)*[a-z0-9_*~-]+$", re.I)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Rongwuyou-Surge-Updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_comment(line: str) -> str:
    line = line.strip().lstrip("\ufeff")
    if not line or line.startswith(("#", "//", ";")):
        return ""
    for mark in (" //", " #"):
        if mark in line:
            line = line.split(mark, 1)[0].strip()
    return line


def normalize_rule(line: str) -> str | None:
    line = strip_comment(line)
    if not line:
        return None

    parts = [part.strip() for part in line.split(",")]
    if len(parts) < 2:
        return None

    rule_type = parts[0].upper()
    if rule_type not in SUPPORTED_TYPES:
        return None

    value = parts[1].strip()
    if not value:
        return None

    if rule_type in {"DOMAIN", "DOMAIN-SUFFIX"}:
        value = value.lower().rstrip(".")
        if not DOMAIN_RE.match(value):
            return None
        return f"{rule_type},{value}"

    if rule_type == "USER-AGENT":
        return f"{rule_type},{value}"

    if rule_type in {"IP-CIDR", "IP-CIDR6"}:
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            return None
        if rule_type == "IP-CIDR" and network.version != 4:
            return None
        if rule_type == "IP-CIDR6" and network.version != 6:
            return None
        return f"{rule_type},{network},no-resolve"

    return None


def collect_rules(text: str) -> set[str]:
    rules: set[str] = set()
    for raw_line in text.splitlines():
        rule = normalize_rule(raw_line)
        if rule:
            rules.add(rule)
    return rules


def sort_key(rule: str):
    rule_type, value, *_ = rule.split(",")
    order = {
        "DOMAIN": 0,
        "DOMAIN-SUFFIX": 1,
        "IP-CIDR": 2,
        "IP-CIDR6": 3,
        "USER-AGENT": 4,
    }[rule_type]
    if rule_type in {"IP-CIDR", "IP-CIDR6"}:
        net = ipaddress.ip_network(value, strict=False)
        return (order, net.version, int(net.network_address), net.prefixlen)
    return (order, value.lower())


def render(rules: set[str]) -> str:
    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    body = "\n".join(sorted(rules, key=sort_key))
    return (
        "# > WeChat\n"
        f"# UpdateTime: {now}\n"
        f"# RuleCount: {len(rules)}\n"
        "# AutoUpdate: weekly by GitHub Actions; exact IP rules preserved; broad IP-ASN and DOMAIN-KEYWORD skipped\n"
        "\n"
        f"{body}\n"
    )


def existing_body(text: str) -> list[str]:
    return sorted(collect_rules(text), key=sort_key)


def main() -> int:
    if not TARGET.exists():
        raise SystemExit("WeChat.txt not found")

    current_text = TARGET.read_text(encoding="utf-8")
    rules = collect_rules(current_text)

    fetched_count = 0
    for url in SOURCE_URLS:
        try:
            text = fetch_text(url)
        except Exception as exc:
            print(f"skip source: {url} ({exc})", file=sys.stderr)
            continue
        fetched_count += 1
        rules |= collect_rules(text)

    if fetched_count == 0:
        raise SystemExit("all upstream WeChat sources failed")

    if sorted(rules, key=sort_key) == existing_body(current_text):
        print("No rule changes.")
        return 0

    TARGET.write_text(render(rules), encoding="utf-8", newline="\n")
    print(f"Updated WeChat.txt with {len(rules)} rules from {fetched_count} upstream sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
