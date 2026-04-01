"""Update Step 5 (modeling) cells in final notebook.

This replaces the existing Step 5 section with:
- train/test split
- StandardScaler (Pipeline)
- 12 model benchmark (incl. XGBoost + LightGBM)
- metrics: R2, RMSE, MAE, MAPE (train/test)
- overfitting warning card if gap small
- top-3 by test R2
- trade-off scatter with BEST highlighted
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import nbformat

NOTEBOOK_PATH = Path(r"C:/Users/cenkg/Desktop/apex/notebooks/student_performance_final.ipynb")
MD_CELL_IDX = 26
CODE_CELL_IDX = 27

MD_SOURCE = """## 5: Modelleme ve Değerlendirme

Bu bölümde:
- Veriyi **train/test** olarak böleceğiz
- **Feature scaling** uygulayacağız
- Görseldeki **12 modeli** eğitip karşılaştıracağız
- Metrikler: **R², RMSE, MAE, MAPE** (train ve test ayrı)
- En iyi 3 modeli çıkarıp, **trade-off** analizi ile **BEST** modeli seçeceğiz
"""

CODE_SOURCE = r"""# 5 Modelleme & Değerlendirme (sıralı run + estetik rapor + grafikler)

import time
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, KFold, cross_validate, GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor


# --------------------------
# 0) Güvenli varsayılanlar
# --------------------------
try:
    RANDOM_STATE
except NameError:
    RANDOM_STATE = 42

try:
    target_col
except NameError:
    target_col = "Exam_Score"

try:
    DATA_PROCESSED_DIR
except NameError:
    DATA_PROCESSED_DIR = Path("data/processed")

try:
    MODELS_DIR
except NameError:
    MODELS_DIR = Path("models")


# --------------------------
# 1) Veri kaynağı + hariç tutulanlar
# --------------------------
excluded_cols = []

if "fe_df_final" in globals():
    model_df = fe_df_final.copy()
    if "fe_df" in globals():
        excluded_cols.extend(sorted(list(set(fe_df.columns) - set(fe_df_final.columns))))
else:
    feat_path = DATA_PROCESSED_DIR / "student_performance_features.csv"
    model_df = pd.read_csv(feat_path)

if "Student_ID" in model_df.columns and "Student_ID" not in excluded_cols:
    excluded_cols.append("Student_ID")

excluded_cols = sorted(list(dict.fromkeys(excluded_cols)))

print("==" * 24)
print("MODELLEME ÖNCESİ — Hariç tutulan sütunlar")
print("==" * 24)
if excluded_cols:
    for c in excluded_cols:
        print("-", c)
else:
    print("- (yok)")


# --------------------------
# 2) X / y, split
# --------------------------
X_cols = [c for c in model_df.columns if c not in [target_col] + excluded_cols]
X = model_df[X_cols].copy()
y = model_df[target_col].astype(float)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE
)


# --------------------------
# 3) Preprocess + scaling
# --------------------------
cat_cols = X_train.select_dtypes(include=["object", "category"]).columns.tolist()
num_cols = [c for c in X_train.columns if c not in cat_cols]

numeric_tf = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_tf = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ]
)

preprocess = ColumnTransformer(
    transformers=[
        ("num", numeric_tf, num_cols),
        ("cat", categorical_tf, cat_cols),
    ],
    remainder="drop",
)


# --------------------------
# 4) Metrikler
# --------------------------
def safe_mape(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.clip(np.abs(y_true), 1e-6, None)
    return float(np.mean(np.abs((y_true - y_pred) / denom)) * 100.0)


def eval_metrics(y_true, y_pred) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": rmse,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mape": safe_mape(y_true, y_pred),
    }


def fit_and_score(model_name: str, estimator) -> dict:
    pipe = Pipeline(steps=[("preprocess", preprocess), ("model", estimator)])
    t0 = time.time()
    pipe.fit(X_train, y_train)
    fit_time = time.time() - t0

    pred_tr = pipe.predict(X_train)
    pred_te = pipe.predict(X_test)

    tr = eval_metrics(y_train, pred_tr)
    te = eval_metrics(y_test, pred_te)

    return {
        "model": model_name,
        "train_r2": tr["r2"],
        "train_rmse": tr["rmse"],
        "train_mae": tr["mae"],
        "train_mape": tr["mape"],
        "test_r2": te["r2"],
        "test_rmse": te["rmse"],
        "test_mae": te["mae"],
        "test_mape": te["mape"],
        "fit_time_s": float(fit_time),
        "pipeline": pipe,
    }

def print_block(title: str, metrics: dict) -> None:
    print("\n" + ("==" * 24))
    print(title)
    print("==" * 24)
    print("TRAIN")
    print(f"R²   : {metrics['train_r2']:.4f}")
    print(f"RMSE : {metrics['train_rmse']:.4f}")
    print(f"MAE  : {metrics['train_mae']:.4f}")
    print(f"MAPE : {metrics['train_mape']:.2f}%")
    print("\nTEST")
    print(f"R²   : {metrics['test_r2']:.4f}")
    print(f"RMSE : {metrics['test_rmse']:.4f}")
    print(f"MAE  : {metrics['test_mae']:.4f}")
    print(f"MAPE : {metrics['test_mape']:.2f}%")


# --------------------------
# 5) Sıralı run (Linear baseline → Ridge → diğerleri)
# --------------------------
sequential_models = [
    ("LinearRegression (Baseline)", LinearRegression()),
    ("Ridge", Ridge(random_state=RANDOM_STATE)),
    ("Lasso", Lasso(random_state=RANDOM_STATE, max_iter=10000)),
    ("ElasticNet", ElasticNet(random_state=RANDOM_STATE, max_iter=10000)),
    ("DecisionTree", DecisionTreeRegressor(random_state=RANDOM_STATE)),
    ("RandomForest", RandomForestRegressor(random_state=RANDOM_STATE, n_estimators=400)),
    ("GradientBoosting", GradientBoostingRegressor(random_state=RANDOM_STATE)),
    (
        "XGBoost",
        XGBRegressor(
            random_state=RANDOM_STATE,
            n_estimators=600,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            objective="reg:squarederror",
            n_jobs=1,
        ),
    ),
    (
        "LightGBM",
        LGBMRegressor(
            random_state=RANDOM_STATE,
            n_estimators=800,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
        ),
    ),
    ("AdaBoost", AdaBoostRegressor(random_state=RANDOM_STATE, n_estimators=400, learning_rate=0.05)),
    ("SVR", SVR(kernel="rbf")),
    ("KNN", KNeighborsRegressor(n_neighbors=10)),
]

run_rows = []
pipelines = {}

for name, est in sequential_models:
    out = fit_and_score(name, est)
    pipelines[name] = out.pop("pipeline")
    run_rows.append(out)
    # İlk iki modeli tek tek daha görünür bas
    if name in ["LinearRegression (Baseline)", "Ridge"]:
        print_block(f"ÇALIŞTIRILAN MODEL — {name}", out)


# --------------------------
# 6) Overfit riski uyarısı (fark küçükse)
# --------------------------
baseline = next(r for r in run_rows if r["model"] == "LinearRegression (Baseline)")
no_big_gap = (
    abs(baseline["train_r2"] - baseline["test_r2"]) <= 0.05
    and (baseline["test_rmse"] / max(baseline["train_rmse"], 1e-9)) <= 1.20
)

if no_big_gap:
    try:
        note_card(
            "Overfitting kontrolü",
            [
                "Train ve test skorları arasında ciddi bir fark görünmüyor.",
                "Bu nedenle belirgin bir overfitting riski sinyali yok (genelleme daha sağlıklı).",
            ],
        )
    except Exception:
        print("\n[Uyarı] Overfitting riski düşük (train-test farkı küçük).")


# --------------------------
# 7) Karşılaştırma tablosu (okunaklı)
# --------------------------
results_df = pd.DataFrame(run_rows).sort_values("test_r2", ascending=False).reset_index(drop=True)

print("\n" + ("==" * 24))
print("MODEL KARŞILAŞTIRMA TABLOSU (Train vs Test)")
print("==" * 24)
display(
    results_df[
        [
            "model",
            "train_r2",
            "test_r2",
            "train_rmse",
            "test_rmse",
            "train_mae",
            "test_mae",
            "train_mape",
            "test_mape",
            "fit_time_s",
        ]
    ]
)


# --------------------------
# 8) Top-3 (R²’ye göre)
# --------------------------
top3 = results_df.head(3).copy()
print("\n" + ("==" * 24))
print("EN İYİ 3 MODEL (Test R²’ye göre)")
print("==" * 24)
for i, r in top3.iterrows():
    print(f"{i+1}) {r['model']:<16} | Test R²={r['test_r2']:.4f} | RMSE={r['test_rmse']:.3f} | MAE={r['test_mae']:.3f}")


# --------------------------
# 9) RMSE + MAE odağı
# --------------------------
rmse_mae_view = top3[["model", "test_r2", "test_rmse", "test_mae"]].sort_values(
    ["test_rmse", "test_mae"], ascending=True
)
print("\nTop-3 içinde RMSE/MAE görünümü:")
display(rmse_mae_view)


# --------------------------
# 10) En iyi model seçimi (R² yüksek + RMSE düşük)
# --------------------------
best_row = rmse_mae_view.sort_values(["test_rmse", "test_mae"], ascending=True).iloc[0]
BEST_MODEL = str(best_row["model"])

print(f"\nEn iyi model: {BEST_MODEL} (yüksek R² + düşük RMSE dengesi)")

# R² barplot (train vs test) — yatay ve okunaklı
plot_r2 = results_df[["model", "train_r2", "test_r2"]].melt(
    id_vars=["model"], var_name="split", value_name="r2"
)
plot_r2["split"] = plot_r2["split"].map({"train_r2": "Train R²", "test_r2": "Test R²"})

fig_r2 = px.bar(
    plot_r2.sort_values("r2", ascending=True),
    x="r2",
    y="model",
    color="split",
    barmode="group",
    orientation="h",
    title="5.2 R² Karşılaştırması (Train vs Test)",
    color_discrete_map={"Train R²": "#94a3b8", "Test R²": "#2563eb"},
)
fig_r2.update_layout(yaxis={"categoryorder": "total ascending"})
try:
    show_export(fig_r2, next_fig("r2_train_test_barh"), title="5.2 R² Karşılaştırması (Train vs Test)")
except Exception:
    fig_r2.show()

try:
    note_card(
        "📝 Bu grafik bize ne anlatıyor? — R² (Train vs Test)",
        [
            "Test R² ne kadar yüksekse, modelin genelleme başarısı o kadar iyidir.",
            "Train ve test R² birbirine yakınsa: model genelde daha sağlıklı geneller.",
            "Train çok yüksek, test belirgin düşükse: overfitting riski artar.",
        ],
    )
except Exception:
    pass

# Hata metrikleri barplot (RMSE + MAE) — train/test
err_long = results_df[["model", "train_rmse", "test_rmse", "train_mae", "test_mae"]].copy()
err_long = err_long.melt(id_vars=["model"], var_name="metric", value_name="value")

def _pretty(m: str) -> str:
    return (
        m.replace("train_", "Train ")
        .replace("test_", "Test ")
        .upper()
    )

err_long["metric"] = err_long["metric"].map(_pretty)

fig_err = px.bar(
    err_long.sort_values("value", ascending=True),
    x="value",
    y="model",
    color="metric",
    barmode="group",
    orientation="h",
    title="5.3 Hata Metrikleri (RMSE & MAE) — Train vs Test",
)
fig_err.update_layout(yaxis={"categoryorder": "total ascending"})
try:
    show_export(fig_err, next_fig("errors_train_test_barh"), title="5.3 Hata Metrikleri — Train vs Test")
except Exception:
    fig_err.show()

try:
    note_card(
        "📝 Bu grafik bize ne anlatıyor? — Hata metrikleri (RMSE & MAE)",
        [
            "RMSE ve MAE ne kadar düşükse model o kadar isabetlidir.",
            "RMSE, büyük hataları daha fazla cezalandırır; MAE daha ‘ortalama hata’ gibi düşünülür.",
            "Train hatası çok düşük ama test hatası belirgin yüksekse: genelleme zayıf olabilir.",
        ],
    )
except Exception:
    pass


# --------------------------
# 11) Trade-off analizi (BEST farklı renkte)
# --------------------------
plot_df = results_df[["model", "test_r2", "test_rmse", "test_mae"]].copy()
plot_df["is_best"] = np.where(plot_df["model"] == BEST_MODEL, "BEST", plot_df["model"])

# Her node farklı renk: renkleri model adına göre verelim; BEST'e özel parlak renk + daha büyük nokta
fig_trade = px.scatter(
    plot_df,
    x="test_rmse",
    y="test_r2",
    color="model",
    hover_data={"model": True, "test_rmse": ":.4f", "test_r2": ":.4f", "test_mae": ":.4f"},
    title="5.4 Trade-off: Test RMSE (düşük) vs Test R² (yüksek)",
)
fig_trade.update_traces(marker={"size": 10, "opacity": 0.85})

# BEST noktasını üstüne ekleyip parlat
best_point = plot_df[plot_df["model"] == BEST_MODEL].copy()
if len(best_point):
    fig_best = px.scatter(
        best_point,
        x="test_rmse",
        y="test_r2",
        text=["BEST"],
    )
    fig_best.update_traces(marker={"size": 18, "color": "#ef4444", "line": {"width": 2, "color": "#0f172a"}}, textposition="top center")
    for tr in fig_best.data:
        fig_trade.add_trace(tr)

try:
    show_export(fig_trade, next_fig("tradeoff_best_model"), title="5.1 Trade-off — BEST")
except Exception:
    fig_trade.show()

try:
    note_card(
        "📝 Bu grafik bize ne anlatıyor? — Trade-off (BEST neden seçildi?)",
        [
            "Bu grafik iki hedefi aynı anda gösterir: Test RMSE düşük olsun (sola), Test R² yüksek olsun (yukarı).",
            "Sol-üst tarafa yaklaşan noktalar genelde daha iyi dengededir.",
            "BEST etiketi, yüksek R² + düşük RMSE dengesinde seçtiğimiz modeli gösterir.",
        ],
        note="Bir sonraki adım: Cross-validation ve hiperparametre optimizasyonu ile bu seçimi daha da güvenceye alacağız.",
    )
except Exception:
    pass


# ==========================================================
# 5.2 Cross-Validation ve Hiperparametre Optimizasyonu
# ==========================================================
print("\n" + ("==" * 24))
print("5.2 CROSS-VALIDATION (5-Fold) + HİPERPARAMETRE OPTİMİZASYONU")
print("==" * 24)

cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)


def cv_eval(model_name: str, estimator) -> dict:
    pipe = Pipeline(steps=[("preprocess", preprocess), ("model", estimator)])
    scoring = {
        "r2": "r2",
        "rmse": "neg_root_mean_squared_error",
        "mae": "neg_mean_absolute_error",
    }
    out = cross_validate(
        pipe,
        X_train,
        y_train,
        cv=cv,
        scoring=scoring,
        return_train_score=True,
        n_jobs=1,
    )

    train_r2 = float(np.mean(out["train_r2"]))
    cv_r2 = float(np.mean(out["test_r2"]))
    train_rmse = float(-np.mean(out["train_rmse"]))
    cv_rmse = float(-np.mean(out["test_rmse"]))
    train_mae = float(-np.mean(out["train_mae"]))
    cv_mae = float(-np.mean(out["test_mae"]))

    return {
        "model": model_name,
        "train_r2_cv": train_r2,
        "cv_r2": cv_r2,
        "train_rmse_cv": train_rmse,
        "cv_rmse": cv_rmse,
        "train_mae_cv": train_mae,
        "cv_mae": cv_mae,
        "cv_rmse_std": float(np.std(-out["test_rmse"], ddof=1)),
    }


# 1) Tüm modellerin 5-fold CV performansı
cv_rows = []
for name, est in sequential_models:
    cv_rows.append(cv_eval(name, est))

cv_df = pd.DataFrame(cv_rows).sort_values("cv_r2", ascending=False).reset_index(drop=True)

print("\n" + ("==" * 24))
print("5.2.1 5-Fold CV Performansı (train vs CV)")
print("==" * 24)
display(cv_df)


# 2) Overfitting analizi: Train vs CV farkı + uyarı
def overfit_flag(row) -> str:
    # Basit, anlaşılır eşikler
    r2_gap = float(row["train_r2_cv"] - row["cv_r2"])
    rmse_ratio = float(row["cv_rmse"] / max(row["train_rmse_cv"], 1e-9))
    if (r2_gap >= 0.10) or (rmse_ratio >= 1.25):
        return "⚠️"
    return ""


over_df = cv_df.copy()
over_df["r2_gap"] = over_df["train_r2_cv"] - over_df["cv_r2"]
over_df["rmse_ratio"] = over_df["cv_rmse"] / over_df["train_rmse_cv"].clip(lower=1e-9)
over_df["warn"] = over_df.apply(overfit_flag, axis=1)

print("\n" + ("==" * 24))
print("5.2.2 Overfitting Analizi (Train vs CV) — uyarılı tablo")
print("==" * 24)

try:
    def _style_warn(s):
        return ["color:#ef4444; font-weight:900;" if v == "⚠️" else "" for v in s]

    display(
        over_df[
            [
                "model",
                "train_r2_cv",
                "cv_r2",
                "r2_gap",
                "train_rmse_cv",
                "cv_rmse",
                "rmse_ratio",
                "warn",
            ]
        ].style.apply(_style_warn, subset=["warn"])
    )
except Exception:
    display(
        over_df[
            [
                "model",
                "train_r2_cv",
                "cv_r2",
                "r2_gap",
                "train_rmse_cv",
                "cv_rmse",
                "rmse_ratio",
                "warn",
            ]
        ]
    )

try:
    note_card(
        "📝 Bu tablo bize ne anlatıyor? — Overfitting analizi",
        [
            "Train skoru CV skorundan çok daha iyiyse model aşırı öğrenmiş olabilir.",
            "⚠️ işareti olan modelleri ‘daha riskli’ kabul edip seçimde geri plana atıyoruz.",
        ],
    )
except Exception:
    pass


# 3) En iyi 3 modeli getir (CV R²’ye göre)
top3_cv = over_df.sort_values(["cv_r2", "cv_rmse"], ascending=[False, True]).head(3).copy()
print("\n" + ("==" * 24))
print("5.2.3 En iyi 3 model (CV R²’ye göre)")
print("==" * 24)
display(top3_cv[["model", "cv_r2", "cv_rmse", "cv_mae", "warn"]])


# 4) Hiperparametre optimizasyonu (top-3 için küçük grid)
def grid_for(name: str) -> dict:
    if name == "Ridge":
        return {"model__alpha": [0.1, 1.0, 10.0, 50.0]}
    if name == "Lasso":
        return {"model__alpha": [0.0005, 0.001, 0.01, 0.05, 0.1]}
    if name == "ElasticNet":
        return {"model__alpha": [0.001, 0.01, 0.1], "model__l1_ratio": [0.2, 0.5, 0.8]}
    if name == "RandomForest":
        return {"model__max_depth": [None, 6, 10], "model__min_samples_split": [2, 5, 10]}
    if name == "GradientBoosting":
        return {"model__n_estimators": [200, 400], "model__learning_rate": [0.05, 0.1], "model__max_depth": [2, 3]}
    if name == "XGBoost":
        return {"model__max_depth": [3, 4, 6], "model__n_estimators": [400, 700], "model__learning_rate": [0.03, 0.05, 0.1]}
    if name == "LightGBM":
        return {"model__num_leaves": [31, 63], "model__n_estimators": [400, 800], "model__learning_rate": [0.03, 0.05, 0.1]}
    if name == "SVR":
        return {"model__C": [1.0, 5.0, 10.0], "model__gamma": ["scale", "auto"]}
    if name == "KNN":
        return {"model__n_neighbors": [5, 10, 15]}
    if name == "DecisionTree":
        return {"model__max_depth": [None, 4, 8], "model__min_samples_split": [2, 5, 10]}
    if name == "AdaBoost":
        return {"model__n_estimators": [200, 400], "model__learning_rate": [0.05, 0.1, 0.2]}
    if name == "LinearRegression (Baseline)":
        return {}
    if name == "LinearRegression":
        return {}
    return {}


name_to_est = {name: est for name, est in sequential_models}
gs_rows = []
best_estimators = {}

for name in top3_cv["model"].tolist():
    base_est = name_to_est.get(name)
    pipe = Pipeline(steps=[("preprocess", preprocess), ("model", base_est)])
    grid = grid_for(name)

    if not grid:
        # Opt yoksa direkt değerlendir
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        met = eval_metrics(y_test, pred)
        gs_rows.append({"model": name, "best_params": {}, "test_r2": met["r2"], "test_rmse": met["rmse"], "test_mae": met["mae"], "test_mape": met["mape"]})
        best_estimators[name] = pipe
        continue

    gs = GridSearchCV(
        pipe,
        param_grid=grid,
        scoring="r2",
        cv=cv,
        n_jobs=1,
    )
    gs.fit(X_train, y_train)
    best_pipe = gs.best_estimator_
    pred = best_pipe.predict(X_test)
    met = eval_metrics(y_test, pred)
    gs_rows.append(
        {
            "model": name,
            "best_params": gs.best_params_,
            "test_r2": met["r2"],
            "test_rmse": met["rmse"],
            "test_mae": met["mae"],
            "test_mape": met["mape"],
        }
    )
    best_estimators[name] = best_pipe

gs_df = pd.DataFrame(gs_rows).sort_values(["test_r2", "test_rmse"], ascending=[False, True]).reset_index(drop=True)
print("\n" + ("==" * 24))
print("5.2.4 Top-3 için Hiperparametre Optimizasyonu (GridSearchCV) — Test sonuçları")
print("==" * 24)
display(gs_df)

# 4.b) İyileşme oranları (tuned vs untuned) — yüzde gösterim
base_lookup = (
    results_df.set_index("model")[["test_r2", "test_rmse", "test_mae", "test_mape"]].to_dict(orient="index")
    if "results_df" in globals()
    else {}
)

improve_rows = []
for _, r in gs_df.iterrows():
    name = str(r["model"])
    base = base_lookup.get(name)
    if not base:
        continue

    base_rmse = float(base["test_rmse"])
    base_mae = float(base["test_mae"])
    base_r2 = float(base["test_r2"])

    tuned_rmse = float(r["test_rmse"])
    tuned_mae = float(r["test_mae"])
    tuned_r2 = float(r["test_r2"])

    rmse_imp = (base_rmse - tuned_rmse) / max(base_rmse, 1e-9) * 100.0
    mae_imp = (base_mae - tuned_mae) / max(base_mae, 1e-9) * 100.0
    r2_delta = tuned_r2 - base_r2

    improve_rows.append(
        {
            "model": name,
            "base_test_r2": base_r2,
            "tuned_test_r2": tuned_r2,
            "r2_delta": r2_delta,
            "base_test_rmse": base_rmse,
            "tuned_test_rmse": tuned_rmse,
            "rmse_improve_%": rmse_imp,
            "base_test_mae": base_mae,
            "tuned_test_mae": tuned_mae,
            "mae_improve_%": mae_imp,
        }
    )

improve_df = pd.DataFrame(improve_rows).sort_values(["tuned_test_r2", "tuned_test_rmse"], ascending=[False, True])
if len(improve_df):
    print("\n" + ("==" * 24))
    print("5.2.4.b İyileşme Oranları (Tuned vs Untuned) — %")
    print("==" * 24)
    display(improve_df)
    try:
        note_card(
            "📝 Bu tablo bize ne anlatıyor? — İyileşme oranları",
            [
                "RMSE/MAE tarafındaki yüzde, tuning sonrası hatanın ne kadar azaldığını gösterir (yüksek olması iyi).",
                "R² delta pozitifse, açıklama gücünde artış var demektir.",
                "Tuning bazı modellerde fayda sağlar; bazılarında etkisi sınırlı kalabilir.",
            ],
        )
    except Exception:
        pass


# 5) 5 gerçek test örneği mini gösterim
FINAL_NAME = str(gs_df.iloc[0]["model"])
FINAL_MODEL = best_estimators[FINAL_NAME]

pred_test = FINAL_MODEL.predict(X_test)
sample_n = min(5, len(X_test))
sample_idx = np.random.RandomState(RANDOM_STATE).choice(len(X_test), size=sample_n, replace=False)
mini = X_test.iloc[sample_idx].copy()
mini["y_true"] = y_test.iloc[sample_idx].values
mini["y_pred"] = pred_test[sample_idx]
mini["abs_error"] = np.abs(mini["y_true"] - mini["y_pred"])

print("\n" + ("==" * 24))
print("5.2.5 Mini gösterim — 5 gerçek test örneği")
print("==" * 24)
display(mini[["y_true", "y_pred", "abs_error"]].sort_values("abs_error", ascending=False))


# 6) Final model gösterimi + skor + .pkl kaydı
final_pred = FINAL_MODEL.predict(X_test)
final_test = eval_metrics(y_test, final_pred)

print("\n" + ("==" * 24))
print("5.2.6 EN İYİ MODEL (Final)")
print("==" * 24)
print("Model:", FINAL_NAME)
print(f"TEST R²   : {final_test['r2']:.4f}")
print(f"TEST RMSE : {final_test['rmse']:.4f}")
print(f"TEST MAE  : {final_test['mae']:.4f}")
print(f"TEST MAPE : {final_test['mape']:.2f}%")

# 6.b) Gerçek vs Tahmin yakınlığı (görsel)
try:
    scatter_df = pd.DataFrame(
        {
            "y_true": np.asarray(y_test, dtype=float),
            "y_pred": np.asarray(final_pred, dtype=float),
        }
    )
    scatter_df["abs_error"] = np.abs(scatter_df["y_true"] - scatter_df["y_pred"])

    fig_close = px.scatter(
        scatter_df,
        x="y_true",
        y="y_pred",
        opacity=0.65,
        color="abs_error",
        color_continuous_scale="Turbo",
        title=f"5.2.6.b Gerçek vs Tahmin Yakınlığı — {FINAL_NAME}",
        labels={"y_true": "Gerçek (Exam_Score)", "y_pred": "Tahmin"},
    )

    mn = float(min(scatter_df["y_true"].min(), scatter_df["y_pred"].min()))
    mx = float(max(scatter_df["y_true"].max(), scatter_df["y_pred"].max()))
    fig_close.add_shape(type="line", x0=mn, y0=mn, x1=mx, y1=mx, line=dict(width=3, color="#ef4444"))
    fig_close.update_layout(coloraxis_colorbar_title="|Hata|")

    try:
        show_export(fig_close, next_fig("final_true_vs_pred"), title=f"5.2.6.b Gerçek vs Tahmin — {FINAL_NAME}")
    except Exception:
        fig_close.show()

    try:
        note_card(
            "📝 Bu grafik bize ne anlatıyor? — Gerçek vs Tahmin",
            [
                "Noktalar kırmızı diyagonale ne kadar yakınsa tahminler o kadar doğrudur.",
                "Renk koyulaştıkça (|hata| arttıkça) modelin zorlandığı bölgeleri görürsün.",
                "Diyagonalin üstü: model fazla tahmin ediyor; altı: düşük tahmin ediyor.",
            ],
        )
    except Exception:
        pass
except Exception:
    pass

MODEL_PATH = MODELS_DIR / "best_model.pkl"
MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
import joblib

joblib.dump(FINAL_MODEL, MODEL_PATH)
print("✅ PKL kaydedildi:", MODEL_PATH)

try:
    note_card(
        "Skor ne anlama geliyor?",
        [
            "R² yükseldikçe model daha fazla ‘açıklama gücü’ kazanır.",
            "RMSE/MAE düştükçe tahminler gerçeğe yaklaşır.",
            "Bu final skor, test verisinde modelin ‘gerçek dünyaya’ en yakın performans özetidir.",
        ],
    )
except Exception:
    pass
"""


def _cleanse(x):
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
        return x
    if isinstance(x, list):
        return [_cleanse(v) for v in x]
    if isinstance(x, dict):
        return {k: _cleanse(v) for k, v in x.items()}
    return x


def main() -> None:
    nb = nbformat.read(NOTEBOOK_PATH, as_version=4)
    if len(nb.cells) <= CODE_CELL_IDX:
        raise RuntimeError("Notebook does not have expected Step 5 cells.")

    nb.cells[MD_CELL_IDX].cell_type = "markdown"
    nb.cells[MD_CELL_IDX].source = MD_SOURCE

    nb.cells[CODE_CELL_IDX].cell_type = "code"
    nb.cells[CODE_CELL_IDX].source = CODE_SOURCE

    nbformat.write(nb, NOTEBOOK_PATH)

    data = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    NOTEBOOK_PATH.write_text(
        json.dumps(_cleanse(data), ensure_ascii=False, indent=1, allow_nan=False),
        encoding="utf-8",
    )

    print(f"Updated Step 5 cells ({MD_CELL_IDX}, {CODE_CELL_IDX}) in {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

