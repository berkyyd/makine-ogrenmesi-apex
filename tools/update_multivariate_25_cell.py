import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    nb_path = repo_root / "student_performance_final.ipynb"
    template_path = repo_root / "tools" / "multivariate_25_cell_template.py"

    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    cell_idx = 15
    old_src = "".join(nb["cells"][cell_idx].get("source", []))
    needle = "# 2.5 Multivariate analizler (Plotly) + yorum"
    if needle not in old_src:
        raise RuntimeError("Target 2.5 cell not found; aborting.")

    new_src = template_path.read_text(encoding="utf-8")
    nb["cells"][cell_idx]["source"] = [line + "\n" for line in new_src.split("\n")]
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    # Sanity check
    nb2 = json.loads(nb_path.read_text(encoding="utf-8"))
    chk = "".join(nb2["cells"][cell_idx].get("source", []))
    if "multivariate_3d_scatter" in chk:
        raise RuntimeError("2.5.1 still present; expected removed.")
    if "multivariate_top_vs_bottom_diff" not in chk or "multivariate_sleep_internet_heatmap" not in chk:
        raise RuntimeError("Expected 2.5.2/2.5.3 not present after update.")


if __name__ == "__main__":
    main()

