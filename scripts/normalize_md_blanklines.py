from pathlib import Path

files = [
    r"c:\Users\suman\Documents\NRSH\workingExp.md",
    r"c:\Users\suman\Documents\NRSH\WEBSOCKETS_FIX_SUMMARY.md",
    r"c:\Users\suman\Documents\NRSH\SUPABASE_SETUP.md",
    r"c:\Users\suman\Documents\NRSH\SETUP.md",
    r"c:\Users\suman\Documents\NRSH\QUICK_START.md",
    r"c:\Users\suman\Documents\NRSH\README.md",
    r"c:\Users\suman\Documents\NRSH\PYTHON313_COMPATIBILITY_FIXES.md",
    r"c:\Users\suman\Documents\NRSH\IMPORT_VERIFICATION_REPORT.md",
    r"c:\Users\suman\Documents\NRSH\DIAGNOSTICS.md",
    r"c:\Users\suman\Documents\NRSH\FIXES_APPLIED.md",
    r"c:\Users\suman\Documents\NRSH\DEBUG_REPORT.md",
    r"c:\Users\suman\Documents\NRSH\CHANGES_SUMMARY.md",
    r"c:\Users\suman\Documents\NRSH\database\SCHEMA_FIXES.md",
    r"c:\Users\suman\Documents\NRSH\database\README.md",
    r"c:\Users\suman\Documents\NRSH\samples\README.md",
    r"c:\Users\suman\Documents\NRSH\SoftwareDocumentCode\README.md",
    r"c:\Users\suman\Documents\NRSH\SoftwareDocumentCode\database\README.md",
]

changed = []
for f in files:
    p = Path(f)
    if not p.exists():
        print("MISSING", f)
        continue
    text = p.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    out_lines = []
    blank_run = 0
    for ln in lines:
        stripped_ln = ln.rstrip()
        if stripped_ln.strip() == "":
            blank_run += 1
        else:
            if blank_run > 0:
                out_lines.append("")
                blank_run = 0
            out_lines.append(stripped_ln)
    out_text = newline.join(out_lines).rstrip() + newline
    if out_text != text:
        p.write_text(out_text, encoding="utf-8")
        changed.append(str(p))

print("Modified files:", len(changed))
for c in changed:
    print("-", c)
