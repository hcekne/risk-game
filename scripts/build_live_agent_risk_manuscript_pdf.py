from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


ROOT = Path("/app")
INPUT_MD = ROOT / "docs/article-plans/2026-05-10_live-agent-risk-manuscript.md"
OUTPUT_PDF = ROOT / "docs/article-plans/2026-05-10_live-agent-risk-manuscript.pdf"
HOST_REPO_ROOT = Path("/home/hcekne/repos/risk-game")

PAGE_W = 8.5
PAGE_H = 11.0
LEFT = 0.09
RIGHT = 0.91
TOP = 0.95
BOTTOM = 0.06
BODY_FS = 10.5
TITLE_FS = 18
H1_FS = 14
H2_FS = 12
CAPTION_FS = 9
MONO_FS = 8.5


@dataclass
class Block:
    kind: str
    text: str | None = None
    level: int | None = None
    items: list[str] | None = None
    rows: list[list[str]] | None = None
    image_path: Path | None = None
    caption: str | None = None


def clean_inline_md(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return " ".join(text.split())


def parse_pipe_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_blocks(md_text: str) -> list[Block]:
    lines = md_text.splitlines()
    blocks: list[Block] = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        image_match = re.match(r"!\[(.*)\]\((.*)\)", stripped)
        if image_match:
            blocks.append(
                Block(
                    kind="image",
                    image_path=Path(image_match.group(2)),
                    caption=clean_inline_md(image_match.group(1)),
                )
            )
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append(Block(kind="heading", level=3, text=clean_inline_md(stripped[4:])))
            i += 1
            continue
        if stripped.startswith("## "):
            blocks.append(Block(kind="heading", level=2, text=clean_inline_md(stripped[3:])))
            i += 1
            continue
        if stripped.startswith("# "):
            blocks.append(Block(kind="heading", level=1, text=clean_inline_md(stripped[2:])))
            i += 1
            continue

        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            rows = []
            for idx, table_line in enumerate(table_lines):
                if idx == 1 and re.fullmatch(r"\|[\s:\-|\t]+\|?", table_line):
                    continue
                rows.append(parse_pipe_row(table_line))
            blocks.append(Block(kind="table", rows=rows))
            continue

        if re.match(r"^[-*] ", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                items.append(clean_inline_md(re.sub(r"^[-*] ", "", lines[i].strip())))
                i += 1
            blocks.append(Block(kind="bullet_list", items=items))
            continue

        if re.match(r"^\d+\. ", stripped):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                items.append(clean_inline_md(re.sub(r"^\d+\. ", "", lines[i].strip())))
                i += 1
            blocks.append(Block(kind="numbered_list", items=items))
            continue

        if stripped.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(clean_inline_md(lines[i].strip()[2:]))
                i += 1
            blocks.append(Block(kind="blockquote", text=" ".join(quote_lines)))
            continue

        para_lines = []
        while i < len(lines):
            cur = lines[i].rstrip()
            cur_stripped = cur.strip()
            if not cur_stripped:
                break
            if (
                cur_stripped.startswith("#")
                or cur_stripped.startswith("|")
                or cur_stripped.startswith("![")
                or re.match(r"^[-*] ", cur_stripped)
                or re.match(r"^\d+\. ", cur_stripped)
                or cur_stripped.startswith("> ")
            ):
                break
            para_lines.append(cur_stripped)
            i += 1
        blocks.append(Block(kind="paragraph", text=clean_inline_md(" ".join(para_lines))))
    return blocks


def resolve_repo_path(path: Path) -> Path:
    if path.exists():
        return path
    try:
        relative = path.relative_to(HOST_REPO_ROOT)
        candidate = ROOT / relative
        if candidate.exists():
            return candidate
    except ValueError:
        pass
    return path


class PdfRenderer:
    def __init__(self, output_path: Path) -> None:
        self.pdf = PdfPages(output_path)
        self.page_number = 0
        self.fig = None
        self.ax = None
        self.y = TOP
        self.page_has_content = False
        self.new_page()

    def new_page(self) -> None:
        if self.fig is not None:
            self.finish_page()
        self.page_number += 1
        self.fig = plt.figure(figsize=(PAGE_W, PAGE_H))
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.axis("off")
        self.y = TOP
        self.page_has_content = False

    def finish_page(self) -> None:
        if self.fig is None:
            return
        self.ax.text(0.5, 0.025, f"{self.page_number}", ha="center", va="center", fontsize=9, family="DejaVu Serif")
        self.pdf.savefig(self.fig, bbox_inches="tight")
        plt.close(self.fig)
        self.fig = None
        self.ax = None

    def close(self) -> None:
        self.finish_page()
        self.pdf.close()

    def ensure_space(self, needed: float) -> None:
        if self.y - needed < BOTTOM:
            self.new_page()

    def line_height(self, font_size: float) -> float:
        return (font_size * 1.35) / 792.0

    def wrap(self, text: str, font_size: float, indent: int = 0) -> list[str]:
        width = max(32, int((96 - indent * 6) * (11.0 / font_size)))
        return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]

    def add_paragraph(
        self,
        text: str,
        font_size: float = BODY_FS,
        weight: str = "normal",
        style: str = "normal",
        indent: float = 0.0,
        extra_after: float = 0.008,
    ) -> None:
        lines = self.wrap(text, font_size, indent=int(indent * 10))
        lh = self.line_height(font_size)
        needed = len(lines) * lh + extra_after
        self.ensure_space(needed)
        self.ax.text(
            LEFT + indent,
            self.y,
            "\n".join(lines),
            ha="left",
            va="top",
            fontsize=font_size,
            fontweight=weight,
            style=style,
            family="DejaVu Serif",
            transform=self.ax.transAxes,
        )
        self.y -= needed
        self.page_has_content = True

    def add_heading(self, text: str, level: int) -> None:
        size = {1: TITLE_FS, 2: H1_FS, 3: H2_FS}.get(level, H2_FS)
        if level == 1 and self.page_has_content:
            self.new_page()
        else:
            self.ensure_space(self.line_height(size) * 2)
        self.add_paragraph(text, font_size=size, weight="bold", extra_after=0.012 if level == 1 else 0.01)

    def add_list(self, items: list[str], numbered: bool) -> None:
        for idx, item in enumerate(items, start=1):
            prefix = f"{idx}. " if numbered else "- "
            self.add_paragraph(prefix + item, indent=0.02, extra_after=0.004)
        self.y -= 0.004

    def add_blockquote(self, text: str) -> None:
        self.add_paragraph(text, font_size=11, style="italic", indent=0.03, extra_after=0.01)

    def add_table(self, rows: list[list[str]], title: str | None = None) -> None:
        self.new_page()
        if title:
            self.add_paragraph(title, font_size=10, weight="bold", extra_after=0.012)
        table_ax = self.fig.add_axes([0.07, 0.17, 0.86, 0.70])
        table_ax.axis("off")
        table = table_ax.table(cellText=rows[1:], colLabels=rows[0], cellLoc="left", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        for (r, c), cell in table.get_celld().items():
            cell.set_edgecolor("#444444")
            if r == 0:
                cell.set_text_props(weight="bold")
                cell.set_facecolor("#EAEAEA")
        self.page_has_content = True
        self.new_page()

    def add_image(self, image_path: Path, caption: str) -> None:
        self.new_page()
        self.add_paragraph(caption, font_size=CAPTION_FS, style="italic", extra_after=0.01)
        img = mpimg.imread(resolve_repo_path(image_path))
        h, w = img.shape[:2]
        max_w = 0.84
        max_h = 0.68
        aspect = h / w
        draw_w = max_w
        draw_h = draw_w * aspect * (PAGE_W / PAGE_H)
        if draw_h > max_h:
            draw_h = max_h
            draw_w = draw_h / aspect * (PAGE_H / PAGE_W)
        x = (1 - draw_w) / 2
        y = 0.16 + (max_h - draw_h) / 2
        img_ax = self.fig.add_axes([x, y, draw_w, draw_h])
        img_ax.imshow(img)
        img_ax.axis("off")
        self.page_has_content = True
        self.new_page()


def build_pdf(input_md: Path, output_pdf: Path) -> None:
    blocks = parse_blocks(input_md.read_text())
    renderer = PdfRenderer(output_pdf)
    pending_table_title: str | None = None

    for block in blocks:
        if block.kind == "heading":
            renderer.add_heading(block.text or "", block.level or 2)
            continue
        if block.kind == "paragraph":
            text = block.text or ""
            if text.startswith("Table 1."):
                pending_table_title = text
                continue
            renderer.add_paragraph(text)
            continue
        if block.kind == "bullet_list":
            renderer.add_list(block.items or [], numbered=False)
            continue
        if block.kind == "numbered_list":
            renderer.add_list(block.items or [], numbered=True)
            continue
        if block.kind == "blockquote":
            renderer.add_blockquote(block.text or "")
            continue
        if block.kind == "table":
            renderer.add_table(block.rows or [], title=pending_table_title)
            pending_table_title = None
            continue
        if block.kind == "image":
            renderer.add_image(block.image_path, block.caption or "")
            continue

    renderer.close()


if __name__ == "__main__":
    build_pdf(INPUT_MD, OUTPUT_PDF)
