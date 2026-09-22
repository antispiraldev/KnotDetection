"""Shared Markdown + PDF rendering for the project's documents.

Both `build_primer.py` and `build_report.py` define their text once as a list of
(kind, payload) pairs and render it to a Markdown file and a PDF, so the two formats
cannot drift apart. Kinds: h1, h2, p, bullets, fig (name, caption), table (rows).
Needs `fpdf2`, and DejaVu fonts for the PDF.
"""

from __future__ import annotations

from pathlib import Path

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def _table(body) -> tuple[list[str], list[list[str]]]:
    """A table payload is either {"header": [...], "rows": [...]} or rows of pairs."""
    if isinstance(body, dict):
        return list(body["header"]), [list(r) for r in body["rows"]]
    return ["Term", "Meaning"], [list(r) for r in body]


def render_markdown(path: Path, content: list) -> None:
    lines = []
    for kind, body in content:
        if kind == "h1":
            lines += [f"# {body}", ""]
        elif kind == "h2":
            lines += [f"## {body}", ""]
        elif kind == "p":
            lines += [body, ""]
        elif kind == "bullets":
            lines += [f"- {b}" for b in body] + [""]
        elif kind == "fig":
            name, caption = body
            lines += [f"![{caption}]({name})", "", f"*{caption}*", ""]
        elif kind == "table":
            head, rows = _table(body)
            lines += ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
            lines += ["| " + " | ".join(r) + " |" for r in rows] + [""]
    path.write_text("\n".join(lines))


def render_pdf(path: Path, content: list, out_dir: Path) -> None:
    from fpdf import FPDF

    pdf = FPDF(format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_font("DV", "", str(FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DV", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_page()
    width = pdf.w - pdf.l_margin - pdf.r_margin

    def para(text: str, size: float = 10.5, gap: float = 2.5) -> None:
        pdf.set_font("DV", "", size)
        pdf.set_text_color(34, 34, 34)
        pdf.multi_cell(width, 5.4, text, markdown=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(gap)

    def fig_height(name: str) -> float:
        import PIL.Image
        with PIL.Image.open(out_dir / name) as im:
            return width * im.height / im.width

    for i, (kind, body) in enumerate(content):
        if kind == "h1":
            pdf.set_font("DV", "B", 19)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(width, 9, body, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "h2":
            # Keep a heading with what follows it: a figure if one comes next.
            nxt = content[i + 1] if i + 1 < len(content) else None
            need = 45 if not (nxt and nxt[0] == "fig") else fig_height(nxt[1][0]) + 25
            if pdf.get_y() + need > pdf.h - pdf.b_margin:
                pdf.add_page()
            pdf.ln(2)
            pdf.set_font("DV", "B", 13)
            pdf.set_text_color(47, 111, 176)
            pdf.cell(width, 7, body, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif kind == "p":
            para(body)
        elif kind == "bullets":
            for b in body:
                pdf.set_font("DV", "", 10.5)
                pdf.set_text_color(34, 34, 34)
                pdf.cell(5, 5.4, "•")
                pdf.multi_cell(width - 5, 5.4, b, markdown=True, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            pdf.ln(1.5)
        elif kind == "fig":
            name, caption = body
            img = out_dir / name
            import PIL.Image
            with PIL.Image.open(img) as im:
                h = width * im.height / im.width
            if pdf.get_y() + h + 12 > pdf.h - pdf.b_margin:
                pdf.add_page()
            pdf.image(str(img), x=pdf.l_margin, w=width)
            pdf.set_font("DV", "", 8.8)
            pdf.set_text_color(110, 110, 110)
            pdf.multi_cell(width, 4.6, caption, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
        elif kind == "table":
            head, rows = _table(body)
            pdf.set_font("DV", "", 9.5)
            pdf.set_text_color(34, 34, 34)
            widths = (32, 68) if len(head) == 2 else tuple([100 // len(head)] * len(head))
            with pdf.table(col_widths=widths, line_height=5.2, first_row_as_headings=True,
                           markdown=True) as t:
                row = t.row()
                for h in head:
                    row.cell(h)
                for r in rows:
                    row = t.row()
                    for c in r:
                        row.cell(c)
    pdf.output(str(path))


