import json
from pathlib import Path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    nb_path = repo_root / "student_performance_final.ipynb"

    nb = json.loads(nb_path.read_text(encoding="utf-8"))

    # 2.1 özet kartı (markdown) hemen 2.1 code hücresinin ardından geliyor
    cell_idx = 7
    old_src = "".join(nb["cells"][cell_idx].get("source", []))
    if "Bu bilgiler bize ne anlatıyor?" not in old_src:
        raise RuntimeError("Target 2.1 summary cell not found; aborting.")

    new_md = """<div style="background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%); padding: 20px 24px; border-radius: 16px; box-shadow: 0 6px 26px rgba(100,100,180,0.15); margin: 18px 0 12px 0; color: #15314c;">
    <h3 style="margin:0 0 10px 0; color:#0b1020;">ℹ️ <b>Bu bilgiler bize ne anlatıyor?</b></h3>
    <div style="font-size: 1.08em; line-height: 1.54; color:#142036; font-weight: 420;">
        <ul style="margin:0 0 0 18px;padding:0;">
            <li><b>10.000 öğrencilik</b> geniş ve çeşitli bir veriyle çalışıyoruz. Değişkenlerin çoğu sayısal ve istatistiksel incelemeye uygun.</li>
            <li>Eksik değerler özellikle <b>Weekly_Study_Hours</b>, <b>Internet_Usage_Time</b> ve <b>Extracurricular_Activities</b> gibi alanlarda yoğunlaşıyor. Bu, basit “tek değerle doldurma” yerine ilişkiyi koruyan imputation (örn. KNN) ihtiyacını güçlendirir.</li>
            <li><b>Domain tutarlılık</b>: <b>Sleep_Hours</b> (ör. &lt;2 veya &gt;24), <b>Attendance_Rate</b> (0–100 dışı), <b>Distance_to_School</b> (negatif) gibi fiziksel/mantıksal imkansızlıklar veri hatası kabul edilmelidir.</li>
            <li>Bu dokümanda Adım 2’de sadece <b>tanı</b> (sayım + görsel) yapılır; <b>düzeltme</b> Adım 3’te “hata→NaN→akıllı imputation→(gerekirse) IQR capping” akışıyla gerçekleştirilir.</li>
            <li><b>Parent_Education_Level</b> hiyerarşik bir değişkendir; modelleme öncesi One-Hot yerine ordinal encoding yaklaşımı daha tutarlı olacaktır.</li>
        </ul>
    </div>
</div>
"""

    nb["cells"][cell_idx]["source"] = [line + "\n" for line in new_md.split("\n")]
    nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()

