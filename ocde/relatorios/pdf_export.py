"""Exportação PDF simples e validável do relatório gerencial."""
from __future__ import annotations

from pathlib import Path

# Pré-carrega antes da JVM: o import hook do JPype pode interceptar módulos opcionais.
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    from pypdf import PdfReader
except ImportError:
    pass


def export_pdf(markdown_text: str, destination: Path, title: str) -> Path:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:
        raise RuntimeError(
            "A geração PDF requer reportlab. Instale requirements-report.txt na .venv."
        ) from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = []
    lines = markdown_text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            story.append(Spacer(1, 2.5 * mm))
            index += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            rows = [[cell.strip() for cell in item.strip("|").split("|")] for item in table_lines]
            if len(rows) > 1 and all(set(cell) <= {"-", ":"} for cell in rows[1]):
                rows.pop(1)
            if rows:
                table = Table(rows, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDEFE5")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ]))
                story.append(table)
            continue
        if line.startswith("# "):
            story.append(Paragraph(line[2:], styles["Title"]))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["Heading2"]))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], styles["BodyText"]))
        else:
            safe = line.replace("**", "").replace("`", "")
            story.append(Paragraph(safe, styles["BodyText"]))
        index += 1

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(18 * mm, 10 * mm, title[:90])
        canvas.drawRightString(192 * mm, 10 * mm, f"Página {document.page}")
        canvas.restoreState()

    document = SimpleDocTemplate(
        str(destination), pagesize=A4, rightMargin=14 * mm, leftMargin=14 * mm,
        topMargin=14 * mm, bottomMargin=17 * mm, title=title,
        author="ICMBio", subject="Relatório gerencial anonimizado do PGD",
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    validate_pdf(destination)
    return destination


def validate_pdf(path: Path) -> None:
    if not path.exists() or path.stat().st_size < 100:
        raise RuntimeError(f"PDF ausente ou vazio: {path}")
    try:
        from pypdf import PdfReader
    except ImportError:
        return
    reader = PdfReader(str(path))
    if not reader.pages:
        raise RuntimeError("O PDF gerado não contém páginas.")
    from ocde.relatorios.privacidade import scan_text
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    findings = scan_text(extracted)
    if findings:
        raise RuntimeError("Validação de privacidade do PDF falhou: " + "; ".join(findings))
