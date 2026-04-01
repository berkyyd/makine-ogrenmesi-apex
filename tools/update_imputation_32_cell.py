import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    nb_path = repo_root / "student_performance_final.ipynb"
    template_path = repo_root / "tools" / "imputation_32_cell_template.py"

    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    cell_idx = 19
    old_src = "".join(nb["cells"][cell_idx].get("source", []))
    needle = "# 3.2 Imputation"
    if needle not in old_src:
        raise RuntimeError("Target 3.2 cell not found; aborting.")

    new_src = template_path.read_text(encoding="utf-8")
    nb["cells"][cell_idx]["source"] = [line + "\n" for line in new_src.split("\n")]
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")

    nb2 = json.loads(nb_path.read_text(encoding="utf-8"))
    chk = "".join(nb2["cells"][cell_idx].get("source", []))
    if "3.2 Özet — ne yaptık, ne elde ettik?" not in chk:
        raise RuntimeError("Update failed sanity-check.")


if __name__ == "__main__":
    main()

