"""Integridade estrutural da documentação pública."""
from collections import Counter
from pathlib import Path
import re
from urllib.parse import unquote

import pytest

pytestmark = pytest.mark.regression
ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
PRIVATE = {
    ".agents", ".claude", ".codex", "agents.md", "claude.md",
    "project.md", "artefatos_local",
}
PROMPT_TITLES = {"chain of thought", "self-consistency", "task breakdown"}


def markdown_files():
    paths = [ROOT / "README.md", ROOT / "tests" / "README.md"]
    for directory in ("docs", "ocde", "mgi"):
        paths.extend((ROOT / directory).rglob("*.md"))
    return sorted({path for path in paths if path.is_file()})


def clean_target(raw):
    value = raw.strip()
    value = value[1:value.index(">")] if value.startswith("<") and ">" in value else value.split(maxsplit=1)[0]
    return unquote(value.split("#", 1)[0])


def test_links_relativos_e_areas_privadas():
    broken, private = [], []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in LINK.findall(text):
            target = clean_target(raw)
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            parts = {part.casefold() for part in Path(target).parts}
            label = f"{path.relative_to(ROOT)} -> {target}"
            if parts & PRIVATE:
                private.append(label)
            elif not (path.parent / target).resolve().exists():
                broken.append(label)
    assert not broken, "Links relativos quebrados:\n" + "\n".join(broken)
    assert not private, "Links públicos para áreas privadas:\n" + "\n".join(private)


def test_titulos_unicos_e_institucionais():
    problems = []
    for path in markdown_files():
        headings = [
            line.lstrip("#").strip()
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if re.match(r"^#{1,6}\s+", line)
        ]
        duplicates = [title for title, count in Counter(headings).items() if count > 1]
        if duplicates:
            problems.append(f"{path.relative_to(ROOT)}: duplicados {duplicates}")
        for title in headings:
            if any(term in title.casefold() for term in PROMPT_TITLES):
                problems.append(f"{path.relative_to(ROOT)}: título de prompt {title!r}")
    assert not problems, "\n".join(problems)


def test_cercas_de_codigo_balanceadas():
    problems = []
    for path in markdown_files():
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for fence in ("\x60\x60\x60", "~~~"):
            count = sum(line.lstrip().startswith(fence) for line in lines)
            if count % 2:
                problems.append(f"{path.relative_to(ROOT)}: {count} cercas {fence!r}")
    assert not problems, "\n".join(problems)


def test_indice_denodo_e_ponte_historica():
    canonical = ROOT / "docs" / "ocde" / "06-indicadores-ocde-denodo.md"
    bridge = ROOT / "docs" / "ocde" / "06-indicadores-ocde-mysql.md"
    assert canonical.is_file()
    text = bridge.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 20
    assert canonical.name in text
