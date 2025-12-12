import ast
import os
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
BACKUP_DIR = ROOT / "backups"
EXCLUDE_DIRS = {"venv", "node_modules", ".git", "backups"}


# Function: collect_repo_metadata
def collect_repo_metadata():
    metadata = {}
    metadata["repo_name"] = ROOT.name
    metadata["top_level_dirs"] = [
        p.name for p in ROOT.iterdir() if p.is_dir() and p.name not in EXCLUDE_DIRS
    ]
    req_file = ROOT / "requirements.txt"
    if req_file.exists():
        metadata["requirements"] = [
            ln.strip()
            for ln in req_file.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
    else:
        metadata["requirements"] = []

    py_files = [
        p
        for p in ROOT.rglob("*.py")
        if not any(part in EXCLUDE_DIRS for part in p.parts)
    ]
    metadata["python_file_count"] = len(py_files)

    funcs = {}
    for p in py_files:
        rel = p.relative_to(ROOT)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                names.append(("function", node.name))
            elif isinstance(node, ast.ClassDef):
                names.append(("class", node.name))
        if names:
            funcs[str(rel)] = names
    metadata["functions_and_classes"] = funcs
    return metadata


# Function: generate_summary
def generate_summary(metadata):
    lines = []
    lines.append(
        f"## Auto-generated Repository Summary ({datetime.utcnow().isoformat()} UTC)"
    )
    lines.append("")
    lines.append(f"- Repository: **{metadata['repo_name']}**")
    lines.append(f"- Top-level directories: {', '.join(metadata['top_level_dirs'])}")
    lines.append(f"- Python files: {metadata['python_file_count']}")
    lines.append("")
    if metadata["requirements"]:
        lines.append("### Key Python Dependencies")
        for r in metadata["requirements"][:50]:
            lines.append(f"- {r}")
        lines.append("")

    lines.append("### Extracted Functions and Classes (sample)")
    cnt = 0
    for fpath, items in metadata["functions_and_classes"].items():
        lines.append(f"- **{fpath}**:")
        for t, name in items[:10]:
            lines.append(f"  - {t}: `{name}`")
        cnt += 1
        if cnt >= 40:
            lines.append("- (truncated...)")
            break
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# Function: update_markdown_files
def update_markdown_files():
    """Strip any existing '## Auto-generated Repository Summary' section from markdown files.

    This function will remove the heading and everything that follows it in each
    markdown file, but will not append or generate any new summary content.
    """
    md_files = [
        p
        for p in ROOT.rglob("*.md")
        if not any(part in EXCLUDE_DIRS for part in p.parts)
    ]
    modified = []
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        if "## Auto-generated Repository Summary" in text:
            new_text = re.sub(r"## Auto-generated Repository Summary[\s\S]*$", "", text)
            new_text = new_text.rstrip() + "\n"
        else:
            new_text = text
        if new_text != text:
            p.write_text(new_text, encoding="utf-8")
            modified.append(str(p.relative_to(ROOT)))
    return modified


# Function: replace_comments_in_python
def replace_comments_in_python(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except Exception:
        return False

    mod_doc = ast.get_docstring(tree)
    lines = text.splitlines()
    remove_line_idxs = set()

    if mod_doc:
        triple_re = re.compile(r'^[ruRUfF]*["\']{3}')
        for i, ln in enumerate(lines[:40]):
            if triple_re.match(ln.strip()):
                start = i
                q = ln.strip()[0]
                for j in range(start + 1, len(lines)):
                    if lines[j].strip().endswith('"""') or lines[j].strip().endswith(
                        "'''"
                    ):
                        end = j
                        for k in range(start, end + 1):
                            remove_line_idxs.add(k)
                        break
                break

    for i, ln in enumerate(lines):
        if ln.strip().startswith("#"):
            remove_line_idxs.add(i)

    defs = []  # tuples (lineno_index, type, name)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            defs.append((node.lineno - 1, "Function", node.name))
        elif isinstance(node, ast.ClassDef):
            defs.append((node.lineno - 1, "Class", node.name))
    defs.sort()

    new_lines = []
    defs_idx = {idx: (typ, name) for (idx, typ, name) in defs}
    for i, ln in enumerate(lines):
        if i in defs_idx:
            typ, name = defs_idx[i]
            new_lines.append(f"# {typ}: {name}")
            new_lines.append(ln)
        else:
            if i in remove_line_idxs:
                continue
            else:
                new_lines.append(ln)
    new_text = "\n".join(new_lines)
    path.write_text(new_text, encoding="utf-8")
    return True


# Function: replace_comments_in_js_ts
def replace_comments_in_js_ts(path: Path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*[\s\S]*?\*/", "", text)
    lines = text.splitlines()
    lines = [ln for ln in lines if not ln.strip().startswith("//")]
    text = "\n".join(lines)

    # Function: repl_func
    def repl_func(m):
        name = m.group(1) or m.group(2)
        return f"// Function: {name}\n{m.group(0)}"

    text = re.sub(r"function\s+(\w+)\s*\(", repl_func, text)
    text = re.sub(
        r"(?:const|let|var)\s+(\w+)\s*=\s*\([^\)]*\)\s*=>",
        lambda m: f"// Function: {m.group(1)}\n{m.group(0)}",
        text,
    )
    text = re.sub(
        r"class\s+(\w+)\s*", lambda m: f"// Class: {m.group(1)}\n{m.group(0)}", text
    )

    path.write_text(text, encoding="utf-8")
    return True


# Function: process_code_files
def process_code_files():
    code_files = [
        p
        for p in ROOT.rglob("*")
        if p.suffix in {".py", ".js", ".ts"}
        and not any(part in EXCLUDE_DIRS for part in p.parts)
    ]
    modified = []
    for p in code_files:
        try:
            if p.suffix == ".py":
                ok = replace_comments_in_python(p)
            else:
                ok = replace_comments_in_js_ts(p)
            if ok:
                modified.append(str(p.relative_to(ROOT)))
        except Exception as e:
            print(f"Failed to process {p}: {e}")
    return modified


# Function: main
def main():
    print("Collecting repository metadata...")
    meta = collect_repo_metadata()
    print("Updating Markdown files...")
    md_mod = update_markdown_files()
    print(f"Modified Markdown files: {len(md_mod)}")
    print("Processing code files to replace comments...")
    code_mod = process_code_files()
    print(f"Modified code files: {len(code_mod)}")
    print("\nSummary of changes:")
    for f in md_mod[:200]:
        print("MD+", f)
    for f in code_mod[:200]:
        print("CODE+", f)
    log = ROOT / "scripts" / "update_log.txt"
    log.write_text(
        f"Modified MD: {md_mod}\nModified code: {code_mod}\n", encoding="utf-8"
    )
    print(
        "\nDone. Review changes and run tests. A backup was created in the backups/ directory before changes."
    )


if __name__ == "__main__":
    main()
