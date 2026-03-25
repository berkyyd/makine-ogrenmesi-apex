# Adım 3 — Feature Engineering, Encoding ve Feature Selection (Yol Haritası)

## Biz ne yaptık?

Önceki notebook’ta (`student_performance.ipynb`) ekip şunları yaptı:
1. **Berkay:** EDA (Exploratory Data Analysis) ve görselleştirmeleri yaptı.  
   Veri setini tanıdı: dağılımlar, korelasyonlar, eksik/aykırı değer durumu gibi.

2. **Feza:** **Adım 2 — Veri Temizleme ve Ön İşleme (Data Cleaning & Preprocessing)** kısmını yaptı.  
   Eksikleri doldurdu, tip/yuvarlama tutarlılığı sağladı, tutarsız değerleri düzeltti ve en sonunda temizlenmiş veri setini kaydetti:
   - `dataset/student_performance_cleaned.csv`

Bu noktada **temizlenmiş veri var**, ancak modelin çalışacağı şekilde **Adım 3** (feature engineering, encoding ve feature selection) henüz tamamlanmadı. Bu doküman Adım 3’ü tamamlamana yardım eder.

## Sen ne yapacaksın?

Bu doküman Adım 3’te (Feature Engineering + Encoding + Feature Selection) senin işin için yazıldı (Ethem).

Yapacağın şeyler:
- Temizlenmiş veriyi yükle (`student_performance_cleaned.csv`)
- Yeni anlamlı feature’lar üret (toplam/oran/etkileşim vb.)
- Kategorileri encoding ile sayıya çevir (label veya one-hot)
- Feature selection yap: korelasyon + mutual information ile “aday” belirle, gerekirse birkaçını dene
- En sonda testlerle doğru yaptığını doğrula (özellikle leakage ve `inf/nan`/kolon karışması)

Dosyanın sonunda, arkadaşın elinde doğrudan modellemeye uygun bir `features` dataset’i olacak.

Bu doküman **ML’den yeni başlayan** bir arkadaş için yazıldı. Amacımız: temizlenmiş veriden modellemeye hazır feature tablosunu üretmek.

## 0) Hedef çıktısı (en sonda ne olacak?)

Sonunda elinde şu tipte bir çıktı olacak:

- Modelde kullanılacak özellikler (X) hazır
- Hedef sütun (`Exam_Score`) net biçimde ayrılmış
- Kategoriler encoding ile sayıya çevrilmiş
- Yeni üretilen feature’lar (örn. `total_study`, `ratio` vb.) tabloya eklenmiş
- Gereksizleri azalttığın için tablo çok şişmemiş
- Bir CSV dosyası kaydedilmiş (örn. `dataset/student_performance_features.csv`)

Not: Bu adımda hedef `Exam_Score` kullanılabilir ama **yeni feature üretirken “kullanma”** mantığına dikkat (veri sızıntısı/leakage).

---

## 1) Terimler (kısaca)

- **Feature (özellik):** Modelin gördüğü sütun (ör. `Weekly_Study_Hours`).
- **Feature engineering:** Mevcut sütunlardan yeni sütun türetmek (oran, toplam, etkileşim).
- **Etkileşim (interaction):** İki özelliği birlikte ifade eden yeni sütun (örn. `Stress_Level * Weekly_Study_Hours`).
- **Dönüşüm:** Aynı bilgiyi farklı ölçekle ifade etmek (örn. `log1p`).
- **Encoding:** Kategorik sütunları sayıya çevirmek.
- **Label encoding:** Her kategoriye tek bir sayı verme.
- **One-hot encoding:** Her kategori için ayrı 0/1 sütunu açma.
- **Feature selection:** İlgisiz/tekrarlayan özellikleri azaltma.
- **Korelasyon:** Özellik ile hedef arasındaki doğrusal ilişki (Pearson).
- **Mutual information (MI):** Hedefle bilgi paylaşımını ölçen bir skor (genelde daha “doğrusal olmayan” ilişkilerde de yardımcı olur).

---

## 2) TODO Listesi (Sırayla yap)

- [ ] **T1 — Veriyi yükle ve kontrol et.**  
  `dataset/student_performance_cleaned.csv` dosyasını yükle, `shape`, `dtypes`, eksik değer var mı kontrol et.  
  Ayrıca sütunların içinde `Exam_Score` var mı doğrula.

- [ ] **T2 — Hedef ve ID ayrımı.**  
  Model için hedef sütununu belirle: `y = Exam_Score`.  
  `Student_ID` ile ne yapacağını kararlaştır:
  - Genel yaklaşım: `Student_ID` **X’ten çıkarılır** (kimlik bilgisi model için işe yaramaz).

- [ ] **T3 — Yeni feature üret (en az 3–5 tane).**  
  Sadece “anlamlı ve mantıklı” yeni sütunlar ekle.  
  Özellikle oranlar/toplamlar/etkileşimler.

- [ ] **T4 — En az 1 etkileşim (interaction) ekle.**  
  Örn: `stress_x_study`, `attendance_x_study` gibi.

- [ ] **T5 — Encoding kararı ver (Parent_Education_Level).**  
  `Parent_Education_Level` için:
  - Eğitim seviyesi sıralı bir anlam taşıyor mu? (düşük->yüksek gibi)
  - Modelin türü ne olacak? (lineer mi ağaç mı)
  Basit kural: **eminsen one-hot tercih et**, ama çok kategori varsa `drop_first` kullan.

- [ ] **T6 — Encoding’i uygula ve sütun adlarını temiz tut.**  
  `get_dummies(..., drop_first=True)` veya sklearn `OneHotEncoder` kullan.  
  `Label encoding` tercih edersen bir kolon adıyla (`Parent_Education_Ordinal` gibi) sakla.

- [ ] **T7 — Korelasyon ile kontrol (özellikler + hedef).**  
  Sayısal feature’ların `Exam_Score` ile korelasyonunu hesapla, hedefle en ilişkili ilk birkaçını listele.
  Ayrıca birbirine çok benzeyen (yüksek korelasyonlu) özellik çiftlerini not et.

- [ ] **T8 — Mutual information ile kontrol (mutual_info).**  
  MI skorlarına göre feature sıralaması çıkar.
  İlk liste + en düşük katkılı birkaç özelliği “aday” olarak işaretle.

- [ ] **T9 — Gereksizleri çıkarma denemesi yap.**  
  Korelasyon/MI sonucuna göre:
  - Çok az katkılı birkaç sütunu çıkarmayı dene
  - Ama “çok agresif silme”: küçük veri/yanlış varsayım durumunda performansı düşürebilir.

- [ ] **T10 — Son tabloyu kaydet.**  
  Model adımında direkt kullanacağın tabloyu CSV olarak kaydet.  
  Ek olarak bir markdown/cell’de “hangi sütunlar neden var” kısa özet yaz.

- [ ] **T11 — Son test: yanlış yaptın mı? (leakage, inf/nan, hedef karıştı mı?)**  
  Kod çıktılarına göre aşağıdaki kontrolleri yap.

---

## 3) Bölüm Bölüm: Ne yapacak? Nasıl prompt yazacak? Çıktıdan neyi anlamalı?

### Bölüm A — Veri yükleme ve hedefi ayırma

**Ne yapacak?**  
Temiz CSV’yi yükleyip kontrol edecek.

**Prompt (kopyala-yapıştır):**

```text
dataset/student_performance_cleaned.csv adresindeki CSV’yi pandas ile yükle.
1) shape (satır/sütun) yazdır
2) dtypes (tipleri) göster
3) missing değer sayısını hesapla (df.isna().sum())
4) target: Exam_Score var mı doğrula
5) Student_ID sütunu muhtemelen feature olmayacak: bunu varsayıp kontrol et
Train/test yapma, model kurma.
```

**Çıktıdan şunları anlamalı:**  
- `Exam_Score` gerçekten sütun mu?  
- Eksik değer kaldı mı? (kaldıysa sonraki adımda dikkat gerekir)  
- `Student_ID` sayısal görünüyor olabilir ama kimlik olduğu için genelde çıkarılır.

---

### Bölüm B — Feature engineering (yeni feature türetme)

**Kural (çok önemli):**  
Yeni feature üretirken `Exam_Score`’u girdi olarak kullanma. Bu veri sızıntısı (leakage) olur.

**Yeni feature fikri havuzu (sütun isimlerinize göre uyarlayın):**

- **Toplam / yük (total):**
  - `total_study_load`: `Weekly_Study_Hours + Practice_Exams_Passed` (mantıklı bir “çaba” göstergesi gibi)
- **Oran (ratio):**
  - `attendance_to_study_ratio`: `Attendance_Rate / (Weekly_Study_Hours + 1)`
- **Etkileşim (interaction):**
  - `stress_x_study`: `Stress_Level * Weekly_Study_Hours`
- **Verim (efficiency proxy):**
  - Doğrudan “Exam_Score / ...” yapma. Bunun yerine “hedef bağımsız” bir proxy:
  - örn. `Previous_Scores / (Weekly_Study_Hours + 1)` gibi (geçmiş performans + çaba oranı)

**Prompt:**

```text
Benim dataframe kolonlarım şunlar: 
Weekly_Study_Hours, Attendance_Rate, Sleep_Hours, Previous_Scores, Internet_Usage_Time,
Parent_Education_Level, Distance_to_School, Stress_Level, Practice_Exams_Passed,
Extracurricular_Activities, Exam_Score, Student_ID.

1) Exam_Score'u kullanmadan (leakage yapmadan) en az 3 yeni sütun üret:
   - total_study_load
   - attendance_to_study_ratio
   - stress_x_study
   (ve mümkünse bir tane daha: prev_efficiency veya sleep_to_stress vb.)
2) Oranlarda divide-by-zero olmaması için payda = (x + 1) veya clip kullan.
3) Yeni sütunları ekledikten sonra:
   - head() yazdır
   - inf/-inf var mı kontrol et
   - nan var mı kontrol et
4) Yeni sütunların kısa açıklamasını (markdown şeklinde) yaz.
```

**Çıktıdan şunları anlamalı:**  
- `inf` veya `nan` çıktı mı? (payda hatası olabilir)  
- Yeni sütunlar mantıklı değer aralığında mı?  
- `Exam_Score` hiç feature üretiminde kullanıldı mı? (kodu inceleyerek kontrol)

---

### Bölüm C — Dönüşümler (isteğe bağlı)

**Ne yapacak?**  
Sağa çarpık (çok uzun kuyruklu) değişkenlerde `log1p` denemesi yapabilir.

**Prompt:**

```text
Internet_Usage_Time ve Weekly_Study_Hours için histogram çiz.
Sağa çarpık görünüyorsa log1p dönüşümü için:
 - log_internet = np.log1p(Internet_Usage_Time)
 - log_study = np.log1p(Weekly_Study_Hours)

Sonra log’lu ve log’suz değerlerin dağılımını karşılaştır (plot).
Bu dönüşümü uyguladığını/demanetmediğini gerekçelendir.
```

**Çıktıdan:**  
- log dönüşümü gerçekten dağılımı daha “normal” hale getiriyor mu?

---

### Bölüm D — Feature dönüşümleri ve encoding (label/one-hot)

**Kural:**  
`Parent_Education_Level` kategorik. Bunu sayıya çevireceksin.

**Prompt (ön karar + uygulama):**

```text
Parent_Education_Level için value_counts göster.

1) Eğer eğitim seviyelerinde doğal sıralama varsa ordinal/label encoding dene:
   - Parent_Education_Level'i sıralı bir map ile 0..k arası sayıya çevir
   - Parent_Education_Ordinal isimli yeni kolon üret
2) Ayrıca güvenli bir alternatif olarak one-hot encoding uygula:
   - pd.get_dummies(Parent_Education_Level, prefix="PE", drop_first=True)

Sonra:
- Kaç yeni sütun eklendiğini söyle
- Encoding sonrası df'nin head() ve yeni kolon isimlerini yazdır

Hangi encoding'i kullanacağını (lineer model mi ağaç mı) 1-2 cümleyle gerekçelendir.
```

**Çıktıdan şunları anlamalı:**  
- One-hot sonrası sütun sayısı patlıyor mu?  
- `drop_first=True` referans kategoriyi düşürüyor (dummy trap azaltır).

---

### Bölüm E — Feature selection (korelasyon + mutual info + gereksiz çıkarma)

**Ne yapacak?**  
Hem korelasyon hem MI ile aday özellikleri incele.

**Prompt 1 (korelasyon):**

```text
Hedef y = Exam_Score.
X için sayısal feature kolonlarını seç:
 - Student_ID ve Exam_Score hariç
 - Engineered + encoding sonrası sayısallar

1) Pearson correlation (corrwith) hesapla
2) Korelasyonu Exam_Score ile en yüksek 10 pozitif ve en düşük 5 negatif olacak şekilde listele
3) Özellikler arası korelasyon matrisi için yüksek korelasyon çifti bul:
   - abs(corr) > 0.95 olan en belirgin çiftleri raporla
```

**Prompt 2 (mutual info):**

```text
Hedef y = Exam_Score.
X = sayısal feature kolonları.

sklearn.feature_selection.mutual_info_regression ile:
1) mutual information skorlarını hesapla (random_state=42)
2) Özellikleri MI skoruna göre büyükten küçüğe sırala ve ilk 15’i yazdır
3) En düşük MI skoruna sahip 5 özelliği “aday olarak” işaretle
Ama henüz silme; sadece aday göster.
```

**Prompt 3 (çıkarma stratejisi):**

```text
Korelasyon ve mutual information sonuçlarına göre:
- Birbirine çok benzeyen (korelasyon > 0.95) özellik çiftlerinden hangisini tutacağımı öner.
- MI’sı en düşük olan adaylardan 1-3 tanesini çıkarıp yeniden feature seti oluştur.

Bunu auto-drop yapmadan, önce “öneri tablosu” üret:
 - feature adı
 - korelasyon durumu
 - MI durumu
 - öneri (tut / aday olarak çıkar)
```

**Çıktıdan şunları anlamalı:**  
- Korelasyon lineer ilişkiyi ölçer; MI daha genel bir “bilgi” ölçüsüdür.  
- Çok benzer iki feature’dan biri genelde yeterlidir.

---

### Bölüm F — Son tabloyu kaydetme

**Prompt:**

```text
Final modeling dataframe oluştur:
- X özellikleri: Student_ID çıkarılmış, Exam_Score ayrı (ve X’te yok)
- Encoding sonrası Parent_Education_Level sayısal sütunları kullanılıyor

1) Final X sütun listesini yazdır
2) Final shape yazdır
3) Eksik değer ve inf/nan kontrol et
4) Final dataframe’i dataset/student_performance_features.csv olarak kaydet
5) Kısa bir açıklama yaz: yeni feature’lar neler ve encoding nasıl yapıldı.
```

---

## 4) Son Test (T11) — “Yanlış yaptım mı?” kontrol listesi

Bu adımı özellikle istiyoruz. Modelleme yapmadan önce aşağıdaki testleri yap:

1. **Leakage testi:**  
   Kodunda `Exam_Score` yeni feature oluştururken veya feature selection’da X’e karışmış mı?  
   - Beklenen: `Exam_Score` yalnızca `y` olarak kullanılmalı.

2. **Inf/Nan testi:**  
   Oran/etkileşim yaptığın yerlerde `inf`, `-inf`, `nan` ürettin mi?
   - Beklenen: `np.isfinite(df[...]).all()` benzeri kontrol “temiz” dönmeli.

3. **Encoding testi:**  
   One-hot sonrası `Parent_Education_Level` ham hali hâlâ X içinde mi kalmış?
   - Beklenen: Ham kategorik kolon model girdi kısmında yok.

4. **Sütun sayısı ve isim testi:**  
   encoding ile çok fazla sütun oluştuysa feature selection sonrasında hâlâ makul mu?

5. **Kaydetme testi:**  
   Kaydettiğin dosyayı tekrar yükleyince aynı kolonlar geliyor mu?

**Prompt (kopyala-yapıştır):**

```text
Final dataframe (features) için şu kontrolleri yap:
1) Exam_Score X içinde mi? (olmasın)
2) Student_ID X içinde mi? (genelde olmasın)
3) inf/-inf var mı? nan var mı? sayısını yaz
4) One-hot sonrası hala Parent_Education_Level ham string kolon var mı?
5) Kaydettiğin dataset/student_performance_features.csv dosyasını tekrar load edip
   shape ve kolon listesinin aynı olduğunu doğrula.
Sonuçları tek tek maddeler halinde raporla.
```

---

## 5) İstersen kullanım kılavuzu (mini)

Arkadaşın her bölümü şu sırayla yapabilir:

1. Veriyi kontrol et (T1–T2)
2. Feature üret (T3–T4)
3. Encoding (T5–T6)
4. Selection (T7–T9)
5. Kaydet + özet (T10)
6. Son test (T11)

İstersen bir “checklist” hücresi de ekleyebilirsin; her bölüm bitince ilgili kutuyu işaretlesin.

