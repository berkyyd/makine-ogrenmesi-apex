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
    src = nb.cells[CELL_IDX].source.splitlines()

    # Ensure plotly imports exist after pandas/numpy imports.
    want_lines = [
        "import plotly.express as px",
        "import plotly.graph_objects as go",
    ]

    joined = "\n".join(src)
    changed = False

    if "import plotly.express as px" not in joined:
        # insert after pandas import if exists else at end of import block
        insert_at = 0
        for i, line in enumerate(src):
            if line.strip() == "import pandas as pd":
                insert_at = i + 1
                break
        src.insert(insert_at, "import plotly.express as px")
        changed = True

    if "import plotly.graph_objects as go" not in "\n".join(src):
        insert_at = 0
        for i, line in enumerate(src):
            if line.strip() == "import plotly.express as px":
                insert_at = i + 1
                break
        src.insert(insert_at, "import plotly.graph_objects as go")
        changed = True

    if not changed:
        print("Setup imports already ok.")
        return

    nb.cells[CELL_IDX].source = "\n".join(src) + "\n"
    nbformat.write(nb, NOTEBOOK_PATH)

    data = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    NOTEBOOK_PATH.write_text(
        json.dumps(cleanse(data), ensure_ascii=False, indent=1, allow_nan=False),
        encoding="utf-8",
    )
    print("Added plotly imports to setup cell.")


if __name__ == "__main__":
    main()

