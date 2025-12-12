from pathlib import Path

ROOT = Path(__file__).parent.parent

# Files to format (explicit + directories)
explicit = [
    ROOT / "README.md",
    ROOT / "SETUP.md",
    ROOT / "QUICK_START.md",
    ROOT / "SUPABASE_SETUP.md",
    ROOT / "workingExp.md",
]

md_paths = list(explicit)
md_paths += list((ROOT / "database").rglob("*.md"))
md_paths += list((ROOT / "samples").rglob("*.md"))

changed = []

def is_heading(line: str) -> bool:
    return line.startswith("#") and len(line.strip()) > 1

for p in md_paths:
    if not p.exists():
        continue
    text = p.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    out_lines = []
    blank_run = 0
    prev_was_heading = False
    for i, ln in enumerate(lines):
        # Trim trailing whitespace
        ln = ln.rstrip()
        # Convert ~~~ fences to ```
        if ln.strip().startswith("~~~"):
            ln = ln.replace("~", "`")

        # Normalize ATX headings: ensure a single space after hashes
        if ln.lstrip().startswith("#"):
            parts = ln.lstrip().split(None, 1)
            if parts:
                hashes = parts[0]
                rest = parts[1] if len(parts) > 1 else ""
                ln = f"{hashes} {rest.strip()}".rstrip()

        # Normalize list bullets: use '- ' with single space
        if ln.lstrip().startswith(('-', '*', '+')):
            stripped = ln.lstrip()
            # remove leading marker and whitespace then re-add '- '
            content = stripped[1:].lstrip()
            ln = (" " * (len(ln) - len(stripped))) + "- " + content

        # Handle blank runs
        if ln.strip() == "":
            blank_run += 1
            continue
        else:
            # Insert single blank line if there was a run
            if blank_run > 0:
                out_lines.append("")
                blank_run = 0

        # Ensure one blank line after a heading
        if out_lines and out_lines[-1].lstrip().startswith("#") and not ln.strip() == "":
            if out_lines[-1] != "":
                # ensure a blank line between heading and content
                if len(out_lines) >= 1 and out_lines[-1] != "":
                    # if previous wasn't already followed by a blank, insert
                    if len(out_lines) == 0 or out_lines[-1] != "":
                        out_lines.append("")

        out_lines.append(ln)

    new_text = newline.join(out_lines).rstrip() + newline
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        changed.append(str(p.relative_to(ROOT)))

print("Formatted markdown files:", len(changed))
for c in changed:
    print("-", c)

## Update .gitattributes for markdown line endings (LF)
gitattributes = ROOT / ".gitattributes"
lines = []
if gitattributes.exists():
    lines = gitattributes.read_text(encoding="utf-8").splitlines()

added = False
entry = "*.md text eol=lf"
if entry not in lines:
    lines.append(entry)
    added = True

py_entry = "*.py text eol=lf"
if py_entry not in lines:
    lines.append(py_entry)
    added = True

if added:
    gitattributes.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print("Updated .gitattributes")
