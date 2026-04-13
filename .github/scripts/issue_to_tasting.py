#!/usr/bin/env python3
"""Parse a closed tasting issue and write a markdown file to tastings/."""

import os
import re
import sys

SECTION_ORDER = [
    "形式",
    "提供元",
    "メニュー名",
    "URL",
    "Ice or Hot",
    "甘み(Sweetness)",
    "苦み(Bitterness)",
    "酸味(Acidity)",
    "コク(Body)",
    "質感(Texture)",
    "香り(Aroma)",
    "総合評価(Overall)",
]

REQUIRED_SECTIONS = {"形式", "提供元", "メニュー名"}


def parse_issue_body(body):
    """Return a dict mapping section name -> first matched value."""
    sections = {}
    current_section = None

    for raw_line in body.splitlines():
        line = raw_line.rstrip("\r")

        if line.startswith("## "):
            current_section = line[3:].strip()
            sections.setdefault(current_section, [])
        elif current_section is not None:
            checked = re.match(r"^- \[x\] (.+)", line, re.IGNORECASE)
            if checked:
                sections[current_section].append(checked.group(1).strip())
            elif line.strip() and not re.match(r"^- \[ \] ", line):
                sections[current_section].append(line.strip())

    return {k: v[0] if v else "" for k, v in sections.items()}


def main():
    title = os.environ.get("ISSUE_TITLE", "")
    body = os.environ.get("ISSUE_BODY", "")

    if not title or not body:
        print("ISSUE_TITLE and ISSUE_BODY environment variables are required", file=sys.stderr)
        sys.exit(1)

    sections = parse_issue_body(body)

    if not REQUIRED_SECTIONS.issubset(sections.keys()):
        print("Not a tasting issue – skipping.")
        sys.exit(0)

    lines = [f"# {title}", ""]
    for section in SECTION_ORDER:
        lines.append(f"- {section}: {sections.get(section, '')}")

    content = "\n".join(lines) + "\n"

    output_dir = "./tastings"
    safe_title = title.replace("/", "_").replace("\\", "_")
    filepath = os.path.realpath(os.path.join(output_dir, f"{safe_title}.md"))
    real_output_dir = os.path.realpath(output_dir)
    if not filepath.startswith(real_output_dir + os.sep):
        print("Security error: resolved output path is outside the tastings directory", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Created: {filepath}")


if __name__ == "__main__":
    main()
