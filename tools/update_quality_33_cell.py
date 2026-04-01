import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    nb_path = repo_root / "student_performance_final.ipynb"
    template_path = repo_root / "tools" / "quality_33_cell_template.py"

    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    cell_idx = 21
    # Cell index is stable in this notebook; allow overwriting even if the header changed
    # during previous iterations.
    old_src = "".join(nb["cells"][cell_idx].get("source", []))
    needles = [
        "# 3.3 Data quality report",
        "# 3.3 Data Quality",
        "3.3 Veri kalitesi",
    ]
    if not any(n in old_src for n in needles):
        # Still proceed, but warn by raising a clearer error only if index is invalid.
        if cell_idx >= len(nb.get("cells", [])):
            raise RuntimeError("Target 3.3 cell index out of range; aborting.")

    new_src = template_path.read_text(encoding="utf-8")
    nb["cells"][cell_idx]["source"] = [line + "\n" for line in new_src.split("\n")]
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    nb2 = json.loads(nb_path.read_text(encoding="utf-8"))
    chk = "".join(nb2["cells"][cell_idx].get("source", []))
    if "3.3 Sonuç — veri kalitesi ne dedi?" not in chk:
        raise RuntimeError("Update failed sanity-check.")


if __name__ == "__main__":
    main()

