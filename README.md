# Student Performance (CRISP-DM) — Plotly End-to-End Regression

Bu repo, `Student Performance` veri seti ile **CRISP-DM** metodolojisini takip eden uçtan uca bir regresyon projesidir. Tüm görseller **Plotly (interaktif)** üretilir ve `figures/` altına **HTML** olarak kaydedilir. Final model + tüm preprocessing adımları **joblib** ile `models/` altına `.pkl` olarak kaydedilir (Streamlit deployment için).

## Proje Akışı (CRISP-DM)

```mermaid
flowchart TD
  A[Business_Understanding] --> B[Data_Understanding]
  B --> C[Data_Preparation]
  C --> D[Modeling]
  D --> E[Evaluation]
  E --> F[Deployment_Ready]
  F --> G[models/best_model.pkl]
  B --> H[figures/*.html]
  C --> I[data/processed/*.csv]
  B --> J[data/raw/*.csv]
```

## Klasör Yapısı

```
apex/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── anlatici_metin_sablonlari.md
├── figures/
├── models/
├── notebooks/
│   └── 01_student_performance_crispdm_plotly.ipynb
├── dataset/                      # (mevcut) eski çıktıların durduğu yer
├── requirements.txt
└── README.md
```

## Kurulum

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Çalıştırma

- Notebook: `notebooks/01_student_performance_crispdm_plotly.ipynb`
- Notebook çalıştıkça şu çıktılar oluşur:
  - `data/raw/student_performance_raw.csv`
  - `data/processed/student_performance_cleaned.csv`
  - `data/processed/student_performance_features.csv`
  - `figures/NN_*.html`
  - `models/best_model.pkl`

## Sonuçlar

Notebook içinde her adım **1 / 1.1 / 1.1.1** formatında ilerler ve her grafik için “neden var / ne gösteriyor / ne anlama geliyor / sonraki adım” yorumları eklenir.
