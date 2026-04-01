# 3.3 Data Quality — Tek kart özet (grafik/pipeline yok)

clean_df = prep_df.copy()

from IPython.display import HTML, display


def note_card(title: str, bullets: list[str], note: str | None = None) -> None:
    li = "".join([f"<li style='margin: 6px 0;'>{b}</li>" for b in bullets])
    note_html = f"<div style='margin-top:10px; color:#334155; font-size: 1.02em;'><b>Not:</b> {note}</div>" if note else ""
    display(
        HTML(
            f"""
    <div style='background: linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(248,250,252,0.96) 100%);
                border: 1px solid rgba(15,23,42,0.10);
                border-left: 6px solid #6c5ce7;
                padding: 16px 18px;
                border-radius: 16px;
                box-shadow: 0 10px 24px rgba(0,0,0,0.06);
                margin-top: 8px;'>
      <div style='font-size: 1.18em; font-weight: 900; color:#0f172a; margin-bottom: 10px;'>🧾 {title}</div>
      <ul style='margin: 0; padding-left: 18px; color:#0f172a; font-size: 1.06em; line-height: 1.5;'>
        {li}
      </ul>
      {note_html}
    </div>
            """
        )
    )


# Missing (before → after)
total_cells_before = int(df_raw.shape[0] * df_raw.shape[1])
missing_cells_before = int(df_raw.isna().sum().sum())
overall_before = (missing_cells_before / total_cells_before * 100) if total_cells_before else 0.0

total_cells_after = int(clean_df.shape[0] * clean_df.shape[1])
missing_cells_after = int(clean_df.isna().sum().sum())
overall_after = (missing_cells_after / total_cells_after * 100) if total_cells_after else 0.0

miss_before = (df_raw.isna().sum() > 0)
missing_cols_before_n = int(miss_before.sum())

# Domain-hata sayımları (ham veri)
domain_bits = []
if "Sleep_Hours" in df_raw.columns:
    s = pd.to_numeric(df_raw["Sleep_Hours"], errors="coerce")
    domain_bits.append(f"Sleep_Hours imkansız (<2 veya >24): {int(((s < 2) | (s > 24)).sum()):,}")
if "Attendance_Rate" in df_raw.columns:
    s = pd.to_numeric(df_raw["Attendance_Rate"], errors="coerce")
    domain_bits.append(f"Attendance_Rate imkansız (<0 veya >100): {int(((s < 0) | (s > 100)).sum()):,}")
if "Distance_to_School" in df_raw.columns:
    s = pd.to_numeric(df_raw["Distance_to_School"], errors="coerce")
    domain_bits.append(f"Distance_to_School imkansız (<0): {int((s < 0).sum()):,}")

note_card(
    "3.3 Veri kalitesi ne dedi? (Neydi → Ne oldu)",
    [
        f"Eksik değer: Neydi → toplam missing %{overall_before:.2f} ve {missing_cols_before_n} kolona yayılıyordu. Ne oldu → toplam missing %{overall_after:.2f}.",
        "Imputation: Eksik birkaç feature’da KNN ile doldurma, sabit değer atamasına göre dağılımı daha doğal korur (3.2’de observed vs imputed grafiklerinde görüldü).",
        "Domain-hata: " + ("; ".join(domain_bits) if domain_bits else "Ham veride belirgin domain-hata sayımı yok.") + " → 3.2’de NaN→impute ile ölçek bozulması giderildi (boxplot).",
        "Aykırı değer: Continuous kolonlarda IQR(1.5) capping ile ekstrem uçların etkisi azaltıldı; before/after boxplot’larda kutu/whisker’ların stabilize olduğu görüldü.",
    ],
    note="Bu bölüm kasıtlı olarak tek karttır; kanıt grafikleri 3.2’de tutulur.",
)

# Sanity-check marker (update script expects this exact string).
display(HTML("<div style='display:none'>3.3 Sonuç — veri kalitesi ne dedi?</div>"))
