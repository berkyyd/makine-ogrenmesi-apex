import json
import math
from pathlib import Path

import nbformat


NOTEBOOK_PATH = Path(r"C:/Users/cenkg/Desktop/apex/notebooks/student_performance_final.ipynb")
CELL_IDX = 4


def cleanse(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return x
    if isinstance(x, list):
        return [cleanse(v) for v in x]
    if isinstance(x, dict):
        return {k: cleanse(v) for k, v in x.items()}
    return x


def main() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    src = nb.cells[CELL_IDX].source
    marker = "# 2) Basit görsel boşluk yardımcısı"
    if marker not in src:
        raise RuntimeError("Setup cell marker not found; cell layout changed.")

    # If helpers already exist, skip
    if "def show_export" in src and "def narrate" in src and "def next_fig" in src:
        print("Helpers already present; nothing to do.")
        return

    addition = """


# ================================
# 3) Ortak helper'lar (Run All için)
# ================================
_fig_counter = 0


def next_fig(title_slug: str) -> str:
    \"\"\"Auto-numbered html filename for exports.\"\"\"
    global _fig_counter
    _fig_counter += 1
    safe = \"\".join(ch if ch.isalnum() or ch in \"_-\" else \"_\" for ch in str(title_slug))
    return f\"{_fig_counter:02d}_{safe}.html\"


def export_only(fig, filename: str) -> None:
    \"\"\"Export Plotly figure to figures/ without displaying.\"\"\"
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(FIG_DIR / filename), include_plotlyjs=\"cdn\", full_html=True)


def show_export(fig, filename: str, title: str | None = None) -> None:
    \"\"\"Show Plotly figure and export to figures/.\"\"\"
    if title:
        try:
            fig.update_layout(title=title)
        except Exception:
            pass
    export_only(fig, filename)
    try:
        fig.show()
    except Exception:
        display(fig)


def note_card(title: str, bullets: list[str], note: str | None = None) -> None:
    li = \"\".join([f\"<li style='margin: 6px 0;'>{b}</li>\" for b in bullets])
    note_html = (
        f\"<div style='margin-top:10px; color:#334155; font-size: 1.02em;'><b>Not:</b> {note}</div>\"
        if note
        else \"\"
    )
    display(
        HTML(
            f\"\"\"
    <div style='background: linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.96) 100%);
                border: 1px solid rgba(15,23,42,0.10);
                border-left: 6px solid #6c5ce7;
                padding: 16px 18px;
                border-radius: 16px;
                box-shadow: 0 10px 24px rgba(0,0,0,0.06);
                margin-top: 10px;'>
      <div style='font-size: 1.16em; font-weight: 900; color:#0f172a; margin-bottom: 10px;'>📝 {title}</div>
      <ul style='margin: 0; padding-left: 18px; color:#0f172a; font-size: 1.04em; line-height: 1.5;'>
        {li}
      </ul>
      {note_html}
    </div>
            \"\"\"
        )
    )


def narrate(title: str, bullets: list[str], note: str | None = None) -> None:
    \"\"\"Backward-compatible alias used across notebook.\"\"\"
    note_card(title, bullets, note=note)
"""

    nb.cells[CELL_IDX].source = src.rstrip() + addition + "\n"
    nbformat.write(nb, NOTEBOOK_PATH)

    # strict json rewrite (no NaN/Inf) for tooling
    data = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    NOTEBOOK_PATH.write_text(
        json.dumps(cleanse(data), ensure_ascii=False, indent=1, allow_nan=False),
        encoding="utf-8",
    )
    print("Updated setup helpers in cell", CELL_IDX)


if __name__ == "__main__":
    main()

