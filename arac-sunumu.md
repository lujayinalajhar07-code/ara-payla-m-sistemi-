# Araç Paylaşım Sistemi Backend Sunumu

## 1. Proje Tanımı

Bu backend, **araç paylaşım / araç kiralama** mantığıyla çalışan nesne yönelimli bir sistemdir.  
Temel amaç; araç, kullanıcı, kiralama, ödeme, bakım ve raporlama süreçlerini tek bir merkezden yönetmektir.

Sistem;
- araç ekleme ve silme,
- kullanıcı yönetimi,
- kiralama başlatma ve bitirme,
- ödeme kaydı oluşturma,
- bakım süreçlerini takip etme,
- veri kaydetme / yükleme,
- rapor üretme

gibi işlemleri destekler.

---

## 2. Genel Mimari

Backend tamamen **OOP (Object-Oriented Programming)** yaklaşımıyla yazılmıştır.

### Ana yapı taşları
- **Enum**: Ödeme yöntemleri
- **Model sınıfları**: `Arac`, `Kullanici`, `Kiralama`, `Odeme`, `Bakim`
- **Servis sınıfları**: `Rapor`, `PaylasimSistemi`

### Tasarım yaklaşımı
- Her sınıf tek bir sorumluluk taşır.
- Veriler nesne tabanlı saklanır.
- JSON ile kalıcı veri kaydı yapılabilir.
- GUI katmanı bu backend ile doğrudan çalışabilir.

---

## 3. Kullanılan Teknolojiler

- **Python**
- **Enum**
- **datetime**
- **typing.Optional**
- **json**
- **os**

Bu modüller sayesinde sistem hem veri modeli hem de dosya tabanlı saklama işlemlerini destekler.

---

## 4. Enum Yapısı

### `OdemeYontemi`
Ödeme türlerini sabit ve kontrollü şekilde tutmak için kullanılır.

Tanımlı değerler:
- `KREDI_KARTI` → Kredi Kartı
- `NAKIT` → Nakit
- `HAVALE` → Havale
- `MOBIL_ODEME` → Mobil Ödeme

### Bu yapının amacı
- Hatalı string kullanımını önlemek
- Ödeme türlerini standart hale getirmek
- GUI ve backend arasında tutarlı veri sağlamak

---

## 5. Model Sınıfları

# 5.1 `Arac` Sınıfı

Araç bilgilerini ve aracın güncel durumunu temsil eder.

### Özellikler
- araç ID
- marka
- model
- tip
- kilometre
- müsaitlik durumu
- saatlik ücret

### Sorumlulukları
- Araç bilgisini saklamak
- Müsait / meşgul durumunu güncellemek
- Km bilgisini artırmak
- Sözlük yapısına dönüştürmek
- JSON’a uygun şekilde serialize etmek

### Önemli metotlar
- `arac_durumu_guncelle(musait)`
- `kilometre_guncelle(eklenen_km)`
- `to_dict()`
- `from_dict()`
- `get_tam_ad()`

### Not
Bu sınıf, sistemdeki her aracı bağımsız bir nesne olarak yönetir.

---

# 5.2 `Kullanici` Sınıfı

Sistemdeki müşteri bilgisini tutar.

### Özellikler
- kullanıcı ID
- ad
- ehliyet numarası
- telefon
- kiralama geçmişi

### Sorumlulukları
- Kullanıcı verisini saklamak
- Kullanıcının geçmiş kiralamalarını tutmak
- Aktif kiralama kontrolü yapmak

### Önemli metotlar
- `kiralama_ekle(kiralama)`
- `kiralama_gecmisi()`
- `aktif_kiralama()`
- `to_dict()`
- `from_dict()`

### Avantajı
Bu yapı sayesinde bir kullanıcıya ait geçmiş ve aktif kiralamalar kolayca izlenebilir.

---

# 5.3 `Kiralama` Sınıfı

Sistemin en kritik iş mantığı sınıflarından biridir.

### Özellikler
- kiralama ID
- araç
- kullanıcı
- başlangıç zamanı
- bitiş zamanı
- aktif / tamamlandı durumu
- toplam ücret

### Sorumlulukları
- Kiralama başlatmak
- Kiralama sonlandırmak
- Süre ve ücret hesaplamak
- Araç durumunu güncellemek

### Ücret hesaplama mantığı
- Kiralama süresi saat üzerinden hesaplanır
- Ücret = süre × aracın saatlik ücreti
- 72 saat ve üzeri kiralamalarda %30 indirim uygulanır

### Önemli metotlar
- `kiralama_baslat()`
- `kiralama_bitir(bitis_saati, eklenen_km)`
- `kiralama_bilgisi()`
- `to_dict()`
- `from_dict()`

### İş akışı
1. Araç kiralanır
2. Araç müsaitlik durumu `False` olur
3. Kiralama bitince ücret hesaplanır
4. Araç tekrar müsait hale gelir

---

# 5.4 `Odeme` Sınıfı

Kiralama sonrası oluşan ödeme bilgisini tutar.

### Özellikler
- ödeme ID
- ilgili kiralama
- tutar
- ödeme yöntemi
- tarih
- durum
- açıklama

### Sorumlulukları
- Ödeme kaydı oluşturmak
- Ödeme detaylarını göstermek
- İptal işlemini yönetmek

### Önemli metotlar
- `odeme_detay()`
- `iptal_et()`
- `to_dict()`
- `from_dict()`

### Not
Ödeme yöntemi `OdemeYontemi` enum’u ile yönetilir.

---

# 5.5 `Bakim` Sınıfı

Araç bakım süreçlerini takip eder.

### Özellikler
- bakım ID
- araç
- açıklama
- tarih
- maliyet
- tahmini süre
- tamamlanma durumu
- başlangıç / bitiş zamanı

### Sorumlulukları
- Aracı bakıma almak
- Bakımı tamamlamak
- Bakım maliyetini kaydetmek
- Araç durumunu güncellemek

### Önemli metotlar
- `bakim_baslat()`
- `bakim_bitir(gerceklesen_maliyet)`
- `bakim_detay()`
- `to_dict()`
- `from_dict()`

### İşleyiş
- Bakım başlatılınca araç kullanım dışı olur
- Bakım bitince araç tekrar müsait olur

---

## 6. Raporlama Katmanı

# 6.1 `Rapor` Sınıfı

Sistemdeki verileri analiz etmek ve özet raporlar üretmek için kullanılır.

### Sorumlulukları
- Gelir raporu üretmek
- Araç kullanım raporu hazırlamak
- Sistem özeti çıkarmak

### Önemli metotlar
- `gelir_raporu(baslangic, bitis)`
- `arac_kullanim_raporu()`
- `sistem_ozeti()`

### Rapor örnekleri
- toplam gelir
- ortalama kiralama tutarı
- aktif kiralama sayısı
- araç başına kullanım sayısı
- bakımda olan araç sayısı

### Avantajı
Yönetici paneli veya GUI tarafında hazır istatistik üretmeyi kolaylaştırır.

---

## 7. Ana Sistem Sınıfı

# `PaylasimSistemi`

Bu sınıf, backend’in merkezi yönetim noktasıdır.  
Tüm işlemler bu sınıf üzerinden koordine edilir.

---

### İç veri yapıları
- `self._araclar` → araçlar sözlüğü
- `self._kullanicilar` → kullanıcılar sözlüğü
- `self._kiralamalar` → kiralama listesi
- `self._odemeler` → ödeme listesi
- `self._bakimlar` → bakım listesi

### Sayaçlar
- `self._sonraki_kid`
- `self._sonraki_oid`
- `self._sonraki_bid`

Bu sayaçlar sırasıyla kiralama, ödeme ve bakım ID üretimi için kullanılır.

---

## 8. PaylasimSistemi Sorumlulukları

### 8.1 Veri kaydetme ve yükleme
- `verileri_kaydet()`
- `verileri_yukle()`

JSON formatında tüm sistem verisini diske yazabilir ve tekrar geri okuyabilir.

### 8.2 Araç yönetimi
- `arac_ekle()`
- `arac_sil()`
- `get_araclar()`
- `get_musait_araclar()`

### 8.3 Kullanıcı yönetimi
- `kullanici_ekle()`
- `kullanici_sil()`
- `get_kullanicilar()`

### 8.4 Kiralama yönetimi
- `kiralama_baslat()`
- `kiralama_bitir()`
- `get_kiralamalar()`
- `get_aktif_kiralamalar()`
- `get_gecmis_kiralamalar()`
- `toplam_gelir()`

### 8.5 Ödeme yönetimi
- `odeme_olustur()`
- `get_odemeler()`

### 8.6 Bakım yönetimi
- `bakim_ekle()`
- `bakim_tamamla()`
- `get_bakimlar()`
- `get_bakimdaki_araclar()`
- `get_bakim_istatistik()`

### 8.7 Raporlama
- `rapor_olustur()`
- `detayli_rapor()`

---

## 9. Veri Akışı

### Araç ekleme
1. `Arac` nesnesi oluşturulur
2. `PaylasimSistemi.arac_ekle()` ile sisteme eklenir

### Kullanıcı ekleme
1. `Kullanici` nesnesi oluşturulur
2. `kullanici_ekle()` ile kayıt edilir

### Kiralama başlatma
1. Araç ve kullanıcı kontrol edilir
2. Uygunsa `Kiralama` nesnesi oluşturulur
3. Araç müsaitlik durumu kapatılır

### Kiralama bitirme
1. Kiralama aktif mi kontrol edilir
2. Bitiş zamanı ve km bilgisi alınır
3. Ücret hesaplanır
4. Araç tekrar müsait hale gelir
5. İstenirse ödeme oluşturulur

### Bakım süreci
1. Araç için bakım kaydı açılır
2. Araç bakımda olarak işaretlenir
3. Bakım bitince tekrar aktif edilir

---

## 10. Veri Kalıcılığı ve Kullandığı Yapı

Bu projede **gerçek bir veritabanı sistemi kullanılmıyor**.  
Yani kodda **SQLite, MySQL, PostgreSQL gibi bir DB bağlantısı yok**.

Bunun yerine sistem, verileri **JSON dosyası** olarak saklıyor.  
Yani kullanılan yaklaşım bir **dosya tabanlı kalıcılık** yöntemidir.

### Kullanılan dosya yapısı
- `data.json`

### Kaydedilen içerikler
- araçlar
- kullanıcılar
- kiralamalar
- ödemeler
- bakımlar
- sayaç bilgileri

### Neden önemli?
- Uygulama kapansa bile veriler kaybolmaz
- GUI yeniden açıldığında sistem kaldığı yerden devam edebilir
- Küçük ve orta ölçekli projeler için basit ve anlaşılır bir çözüm sunar

### Not
Bu yapı bir veritabanı alternatifi olarak kullanılabilir, fakat:
- çok büyük veri için uygun değildir
- gelişmiş sorgulama desteği yoktur
- eşzamanlı çoklu kullanıcı senaryolarında sınırlıdır

---

## 11. Hata Yönetimi ve Doğrulamalar

Sistem birçok iş kuralı kontrolü yapar:

### Örnek kontroller
- Aynı araç ID iki kez eklenemez
- Aynı kullanıcı ID iki kez eklenemez
- Aynı ehliyet numarası tekrar kullanılamaz
- Kiralı araç silinemez
- Aktif kiralaması olan kullanıcı silinemez
- Kiralama bitiş zamanı başlangıçtan önce olamaz
- Negatif kilometre girilemez

Bu kontroller veri bütünlüğünü korur.

---

## 12. GUI ile Entegrasyon

Backend, `gui.py` ile doğrudan entegredir.

### GUI tarafının kullandığı yapılar
- `Arac`
- `Kullanici`
- `PaylasimSistemi`
- `OdemeYontemi`

### GUI’nin backend’den aldığı bilgiler
- araç listesi
- kullanıcı listesi
- aktif kiralamalar
- ödeme yöntemleri
- raporlar
- bakım durumu

### Avantajı
Backend ve arayüz birbirinden ayrıdır.  
Bu da kodun daha temiz, bakımı kolay ve genişletilebilir olmasını sağlar.

---

## 13. Güçlü Yönler

### 1. Nesne yönelimli yapı
Kod modüler ve okunabilir.

### 2. Genişletilebilir mimari
Yeni araç tipi, yeni ödeme yöntemi veya yeni rapor kolayca eklenebilir.

### 3. Veri kalıcılığı
JSON kaydı sayesinde sistem kalıcıdır.

### 4. İş kuralı kontrolü
Hatalı kullanım durumları engellenir.

### 5. GUI ile uyum
Backend, masaüstü arayüz ile rahatça kullanılabilir.

---

## 14. Geliştirme Önerileri

Bu backend daha da geliştirilebilir:

- SQLite veya PostgreSQL entegrasyonu
- Daha ayrıntılı fatura sistemi
- Kullanıcı giriş / yetkilendirme yapısı
- Tarih filtreli gelişmiş raporlar
- Log kayıt sistemi
- Birim testler
- API katmanı (FastAPI / Flask)

---

## 15. Örnek Sunum Akışı

Aşağıdaki sıra sunumda kullanılabilir:

1. Projenin amacı
2. Genel mimari
3. Enum ve model yapıları
4. `Arac` ve `Kullanici` sınıfları
5. `Kiralama` süreci
6. `Odeme` yönetimi
7. `Bakim` işlemleri
8. `Rapor` sınıfı
9. `PaylasimSistemi` ana kontrol mekanizması
10. Veri kaydı ve GUI entegrasyonu
11. Güçlü yönler ve geliştirme önerileri

---

## 16. Kısa Özet

Bu backend, araç paylaşım sisteminin tüm temel iş mantığını yöneten, nesne yönelimli, modüler ve genişletilebilir bir yapıdır.  
Araç, kullanıcı, kiralama, ödeme, bakım ve raporlama süreçleri tek merkezden kontrol edilir.  
JSON veri saklama ve GUI entegrasyonu sayesinde proje gerçek kullanım senaryolarına uygun bir altyapı sunar.

---

## 17. Sonuç

Bu proje yalnızca bir veri saklama yapısı değil;  
**iş kuralı, süreç yönetimi, raporlama ve arayüz entegrasyonu** içeren tam bir backend mimarisidir.

Sunumda vurgulanması gereken ana nokta şudur:

> Bu sistem, araç paylaşım senaryosunun yalnızca kayıt tutan değil, süreçleri yöneten akıllı bir backend’idir.
