"""
🚗 Araç Paylaşım Sistemi - Profesyonel Entegre Sürüm
OOP prensipleri ile geliştirilmiş, genişletilebilir modüler yapı
"""

from enum import Enum
from datetime import datetime
from typing import Optional
import json
import os


# ==================== ENUMS ====================
class OdemeYontemi(Enum):
    """Ödeme yöntemleri"""
    KREDI_KARTI = "Kredi Kartı"
    NAKIT = "Nakit"
    HAVALE = "Havale"
    MOBIL_ODEME = "Mobil Ödeme"


# ==================== MODELS ====================
class Arac:
    """Araç bilgilerini ve durumunu yöneten sınıf"""
    
    def __init__(self, arac_id: str, marka: str, model: str, tip: str, 
                 kilometre: float, saatlik_ucret: float):
        self._arac_id       = arac_id
        self._marka         = marka
        self._model         = model
        self._tip           = tip
        self._kilometre     = kilometre
        self._musait_mi     = True
        self._saatlik_ucret = saatlik_ucret

    # === Getter Methods ===
    def get_arac_id(self) -> str:       return self._arac_id
    def get_marka(self) -> str:         return self._marka
    def get_model(self) -> str:         return self._model
    def get_tip(self) -> str:           return self._tip
    def get_kilometre(self) -> float:   return self._kilometre
    def get_musait_mi(self) -> bool:    return self._musait_mi
    def get_saatlik_ucret(self) -> float: return self._saatlik_ucret
    def get_tam_ad(self) -> str:        return f"{self._marka} {self._model}"

    # === Business Methods ===
    def arac_durumu_guncelle(self, musait: bool) -> None:
        """Araç müsaitlik durumunu günceller"""
        self._musait_mi = musait

    def kilometre_guncelle(self, eklenen_km: float) -> None:
        """Aracın kilometresini günceller (negatif değer kontrolü ile)"""
        if eklenen_km < 0:
            raise ValueError("Km negatif olamaz.")
        self._kilometre += eklenen_km

    def to_dict(self) -> dict:
        return {
            "arac_id": self._arac_id,
            "marka": self._marka,
            "model": self._model,
            "tip": self._tip,
            "kilometre": self._kilometre,
            "saatlik_ucret": self._saatlik_ucret,
            "musait_mi": self._musait_mi
        }

    @classmethod
    def from_dict(cls, data: dict):
        arac = cls(data["arac_id"], data["marka"], data["model"], 
                   data["tip"], data["kilometre"], data["saatlik_ucret"])
        arac._musait_mi = data.get("musait_mi", True)
        return arac

    def __repr__(self) -> str:
        return f"Arac({self._arac_id}, {self.get_tam_ad()}, {self._tip})"


class Kullanici:
    """Kullanıcı bilgilerini ve kiralama geçmişini yöneten sınıf"""
    
    def __init__(self, kullanici_id: str, ad: str, ehliyet_no: str, telefon: str = ""):
        self._kullanici_id = kullanici_id
        self._ad           = ad
        self._ehliyet_no   = ehliyet_no
        self._telefon      = telefon
        self._kiralamalar  = []

    # === Getter Methods ===
    def get_kullanici_id(self) -> str: return self._kullanici_id
    def get_ad(self) -> str:           return self._ad
    def get_ehliyet_no(self) -> str:   return self._ehliyet_no
    def get_telefon(self) -> str:      return self._telefon

    # === Business Methods ===
    def kiralama_ekle(self, kiralama) -> None:
        """Kullanıcıya yeni kiralama ekler"""
        self._kiralamalar.append(kiralama)

    def kiralama_gecmisi(self) -> list:
        """Kullanıcının tüm kiralama geçmişini döndürür"""
        return list(self._kiralamalar)

    def aktif_kiralama(self):
        """Kullanıcının aktif kiralaması varsa döndürür, yoksa None"""
        for k in self._kiralamalar:
            if k.get_aktif():
                return k
        return None

    def to_dict(self) -> dict:
        return {
            "kullanici_id": self._kullanici_id,
            "ad": self._ad,
            "ehliyet_no": self._ehliyet_no,
            "telefon": self._telefon
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["kullanici_id"], data["ad"], data["ehliyet_no"], data.get("telefon", ""))

    def __repr__(self) -> str:
        return f"Kullanici({self._kullanici_id}, {self._ad})"


class Kiralama:
    """Kiralama işlemlerini ve ücret hesaplamalarını yöneten sınıf"""
    
    def __init__(self, kiralama_id: int, arac: Arac, kullanici: Kullanici, 
                 baslangic_saati: datetime):
        self._kiralama_id     = kiralama_id
        self._arac            = arac
        self._kullanici       = kullanici
        self._baslangic_saati = baslangic_saati
        self._bitis_saati: Optional[datetime] = None
        self._aktif           = True
        self._toplam_ucret    = 0.0

    # === Getter Methods ===
    def get_kiralama_id(self) -> int:     return self._kiralama_id
    def get_arac(self) -> Arac:           return self._arac
    def get_kullanici(self) -> Kullanici: return self._kullanici
    def get_baslangic_saati(self) -> datetime: return self._baslangic_saati
    def get_bitis_saati(self):            return self._bitis_saati
    def get_aktif(self) -> bool:          return self._aktif
    def get_toplam_ucret(self) -> float:  return self._toplam_ucret

    # === Business Methods ===
    def kiralama_baslat(self) -> tuple[bool, str]:
        """Kiralamayı başlatır ve aracı meşgul olarak işaretler"""
        self._arac.arac_durumu_guncelle(False)
        return True, f"✓ Kiralama #{self._kiralama_id} başlatıldı."

    def kiralama_bitir(self, bitis_saati: datetime, eklenen_km: float = 0) -> tuple[bool, str]:
        """Kiralamayı sonlandırır, ücreti hesaplar ve aracı günceller"""
        if not self._aktif:
            return False, "Bu kiralama zaten sona ermiş."
        if bitis_saati <= self._baslangic_saati:
            return False, "Bitiş saati başlangıçtan önce olamaz."

        self._bitis_saati = bitis_saati
        self._aktif = False
        
        sure_saat = (bitis_saati - self._baslangic_saati).total_seconds() / 3600
        hesaplanan_ucret = sure_saat * self._arac.get_saatlik_ucret()
        
        # 3 gün (72 saat) ve üzeri kiralamalarda %30 indirim
        if sure_saat >= 72:
            hesaplanan_ucret *= 0.70
            
        self._toplam_ucret = round(hesaplanan_ucret, 2)
        
        self._arac.kilometre_guncelle(eklenen_km)
        self._arac.arac_durumu_guncelle(True)
        
        return True, f"✓ Kiralama bitti. Süre: {sure_saat:.1f} saat | Ücret: ₺{self._toplam_ucret:.2f}"

    def kiralama_bilgisi(self) -> dict:
        """Kiralama detaylarını sözlük olarak döndürür"""
        sure = "Devam ediyor"
        if self._bitis_saati:
            dk = int((self._bitis_saati - self._baslangic_saati).total_seconds() / 60)
            sure = f"{dk // 60}s {dk % 60}dk"
        
        return {
            "id":         self._kiralama_id,
            "arac_id":    self._arac.get_arac_id(),
            "arac":       self._arac.get_tam_ad(),
            "kullanici":  self._kullanici.get_ad(),
            "baslangic":  self._baslangic_saati.strftime("%d.%m.%Y %H:%M"),
            "bitis":      self._bitis_saati.strftime("%d.%m.%Y %H:%M") if self._bitis_saati else "—",
            "sure":       sure,
            "ucret":      f"₺{self._toplam_ucret:.2f}",
            "aktif":      self._aktif,
        }

    def to_dict(self) -> dict:
        return {
            "kiralama_id": self._kiralama_id,
            "arac_id": self._arac.get_arac_id(),
            "kullanici_id": self._kullanici.get_kullanici_id(),
            "baslangic_saati": self._baslangic_saati.isoformat(),
            "bitis_saati": self._bitis_saati.isoformat() if self._bitis_saati else None,
            "aktif": self._aktif,
            "toplam_ucret": self._toplam_ucret
        }

    @classmethod
    def from_dict(cls, data: dict, arac: Arac, kullanici: Kullanici):
        k = cls(data["kiralama_id"], arac, kullanici, datetime.fromisoformat(data["baslangic_saati"]))
        if data.get("bitis_saati"):
            k._bitis_saati = datetime.fromisoformat(data["bitis_saati"])
        k._aktif = data.get("aktif", True)
        k._toplam_ucret = data.get("toplam_ucret", 0.0)
        return k

    def __repr__(self) -> str:
        status = "AKTİF" if self._aktif else "TAMAMLANDI"
        return f"Kiralama(#{self._kiralama_id}, {status})"


class Odeme:
    """Ödeme işlemlerini ve fatura bilgilerini yöneten sınıf"""
    
    def __init__(self, odeme_id: int, kiralama: Kiralama, tutar: float, 
                 yontem: OdemeYontemi, aciklama: str = ""):
        self._odeme_id    = odeme_id
        self._kiralama    = kiralama
        self._tutar       = tutar
        self._yontem      = yontem
        self._tarih       = datetime.now()
        self._durum       = "Tamamlandı"
        self._aciklama    = aciklama
    
    def odeme_detay(self) -> dict:
        """Ödeme bilgilerini sözlük olarak döndürür"""
        return {
            "id":            self._odeme_id,
            "kiralama_id":   self._kiralama.get_kiralama_id(),
            "kullanici":     self._kiralama.get_kullanici().get_ad(),
            "arac_id":       self._kiralama.get_arac().get_arac_id(),
            "arac":          self._kiralama.get_arac().get_tam_ad(),
            "tutar":         f"₺{self._tutar:.2f}",
            "yontem":        self._yontem.value,
            "tarih":         self._tarih.strftime("%d.%m.%Y %H:%M"),
            "durum":         self._durum,
            "aciklama":      self._aciklama
        }

    def iptal_et(self) -> bool:
        """Ödemeyi iptal eder (sadece 'Tamamlandı' durumundakiler)"""
        if self._durum == "Tamamlandı":
            self._durum = "İptal"
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "odeme_id": self._odeme_id,
            "kiralama_id": self._kiralama.get_kiralama_id(),
            "tutar": self._tutar,
            "yontem": self._yontem.name,
            "tarih": self._tarih.isoformat(),
            "durum": self._durum,
            "aciklama": self._aciklama
        }

    @classmethod
    def from_dict(cls, data: dict, kiralama: Kiralama):
        o = cls(data["odeme_id"], kiralama, data["tutar"], 
                OdemeYontemi[data["yontem"]], data.get("aciklama", ""))
        o._tarih = datetime.fromisoformat(data["tarih"])
        o._durum = data.get("durum", "Tamamlandı")
        return o

    def __repr__(self) -> str:
        return f"Odeme(#{self._odeme_id}, ₺{self._tutar}, {self._durum})"


class Bakim:
    """Araç bakım ve onarım süreçlerini yöneten sınıf"""
    
    def __init__(self, bakim_id: int, arac: Arac, aciklama: str, 
                 tarih: datetime, maliyet: float = 0.0, tahmini_sure_saati: float = 0):
        self._bakim_id             = bakim_id
        self._arac                 = arac
        self._aciklama             = aciklama
        self._tarih                = tarih
        self._maliyet              = maliyet
        self._tahmini_sure_saati   = tahmini_sure_saati
        self._tamamlandi_mi        = False
        self._baslangic_zamani: Optional[datetime] = None
        self._bitis_zamani: Optional[datetime] = None

    def bakim_baslat(self) -> str:
        """Bakımı başlatır ve aracı kullanım dışı bırakır"""
        self._arac.arac_durumu_guncelle(False)
        self._baslangic_zamani = datetime.now()
        return f"🔧 {self._arac.get_tam_ad()} bakıma alındı: {self._aciklama}"

    def bakim_bitir(self, gerceklesen_maliyet: float = None) -> str:
        """Bakımı tamamlar ve aracı tekrar müsait hale getirir"""
        if self._tamamlandi_mi:
            return "⚠️ Bu bakım zaten tamamlanmış."
        
        self._bitis_zamani = datetime.now()
        self._tamamlandi_mi = True
        if gerceklesen_maliyet is not None:
            self._maliyet = gerceklesen_maliyet
        self._arac.arac_durumu_guncelle(True)
        return f"✅ Bakım tamamlandı. Araç tekrar müsait. Maliyet: ₺{self._maliyet:.2f}"

    def bakim_detay(self) -> dict:
        """Bakım bilgilerini sözlük olarak döndürür"""
        return {
            "id": self._bakim_id,
            "arac": self._arac.get_tam_ad(),
            "arac_id": self._arac.get_arac_id(),
            "aciklama": self._aciklama,
            "tarih": self._tarih.strftime("%d.%m.%Y"),
            "maliyet": f"₺{self._maliyet:.2f}",
            "tamamlandi_mi": self._tamamlandi_mi,
            "baslangic": self._baslangic_zamani.strftime("%H:%M") if self._baslangic_zamani else "—",
            "bitis": self._bitis_zamani.strftime("%H:%M") if self._bitis_zamani else "—"
        }

    def to_dict(self) -> dict:
        return {
            "bakim_id": self._bakim_id,
            "arac_id": self._arac.get_arac_id(),
            "aciklama": self._aciklama,
            "tarih": self._tarih.isoformat(),
            "maliyet": self._maliyet,
            "tahmini_sure_saati": self._tahmini_sure_saati,
            "tamamlandi_mi": self._tamamlandi_mi,
            "baslangic_zamani": self._baslangic_zamani.isoformat() if self._baslangic_zamani else None,
            "bitis_zamani": self._bitis_zamani.isoformat() if self._bitis_zamani else None
        }

    @classmethod
    def from_dict(cls, data: dict, arac: Arac):
        b = cls(data["bakim_id"], arac, data["aciklama"], 
                datetime.fromisoformat(data["tarih"]), 
                data.get("maliyet", 0.0), 
                data.get("tahmini_sure_saati", 0))
        b._tamamlandi_mi = data.get("tamamlandi_mi", False)
        if data.get("baslangic_zamani"): 
            b._baslangic_zamani = datetime.fromisoformat(data["baslangic_zamani"])
        if data.get("bitis_zamani"): 
            b._bitis_zamani = datetime.fromisoformat(data["bitis_zamani"])
        return b

    def __repr__(self) -> str:
        status = "✅" if self._tamamlandi_mi else "🔄"
        return f"Bakim(#{self._bakim_id} {status} {self._arac.get_tam_ad()})"


class Rapor:
    """Sistem raporları ve istatistiklerini oluşturan sınıf"""
    
    def __init__(self, sistem):
        self._sistem = sistem

    def gelir_raporu(self, baslangic: datetime = None, bitis: datetime = None) -> dict:
        """Belirtilen tarih aralığındaki gelir raporunu döndürür"""
        kiralamalar = self._sistem.get_gecmis_kiralamalar()
        
        if baslangic and bitis:
            kiralamalar = [k for k in kiralamalar 
                          if baslangic <= k.get_baslangic_saati() <= bitis]
        
        toplam = sum(k.get_toplam_ucret() for k in kiralamalar)
        ortalama = toplam / len(kiralamalar) if kiralamalar else 0
        
        return {
            "kiralama_sayisi": len(kiralamalar),
            "toplam_gelir": f"₺{toplam:.2f}",
            "ortalama_kiralama": f"₺{ortalama:.2f}",
            "aktif_kiralama": len(self._sistem.get_aktif_kiralamalar())
        }

    def arac_kullanim_raporu(self) -> dict:
        """Her aracın kullanım istatistiklerini döndürür"""
        rapor = {}
        for arac in self._sistem.get_araclar().values():
            arac_kiralamalar = [
                k for k in self._sistem.get_kiralamalar() 
                if k.get_arac().get_arac_id() == arac.get_arac_id()
            ]
            toplam_km = sum(
                k.get_bitis_saati() and 
                (k.get_arac().get_kilometre() - arac.get_kilometre()) 
                or 0 for k in arac_kiralamalar
            )
            rapor[arac.get_arac_id()] = {
                "ad": arac.get_tam_ad(),
                "tip": arac.get_tip(),
                "toplam_kiralama": len(arac_kiralamalar),
                "tahmini_km": toplam_km,
                "musait_mi": arac.get_musait_mi()
            }
        return rapor

    def sistem_ozeti(self) -> dict:
        """Tüm sistemin genel özet raporu"""
        return {
            "toplam_arac": len(self._sistem.get_araclar()),
            "musait_arac": len(self._sistem.get_musait_araclar()),
            "bakimdaki_arac": len(self._sistem.get_bakimdaki_araclar()),
            "toplam_kullanici": len(self._sistem.get_kullanicilar()),
            "aktif_kiralama": len(self._sistem.get_aktif_kiralamalar()),
            "tamamlanan_kiralama": len(self._sistem.get_gecmis_kiralamalar()),
            "toplam_gelir": f"₺{self._sistem.toplam_gelir():.2f}",
            "toplam_odeme": len(self._sistem.get_odemeler()),
            "tamamlanan_bakim": self._sistem.get_bakim_istatistik()["tamamlanan"],
            "bekleyen_bakim": self._sistem.get_bakim_istatistik()["bekleyen"]
        }


# ==================== MAIN SYSTEM ====================
class PaylasimSistemi:
    """
    Araç paylaşım sisteminin ana yönetici sınıfı.
    Tüm işlemler bu sınıf üzerinden koordine edilir.
    """
    
    def __init__(self):
        self._araclar: dict[str, Arac]       = {}
        self._kullanicilar: dict[str, Kullanici] = {}
        self._kiralamalar: list[Kiralama]    = []
        self._odemeler: list[Odeme]          = []
        self._bakimlar: list[Bakim]          = []
        
        self._sonraki_kid: int = 1  # Kiralama ID counter
        self._sonraki_oid: int = 1  # Ödeme ID counter
        self._sonraki_bid: int = 1  # Bakım ID counter

    # === Data Persistence (JSON) ===
    def verileri_kaydet(self, dosya_adi="data.json") -> bool:
        try:
            data = {
                "araclar": [a.to_dict() for a in self._araclar.values()],
                "kullanicilar": [u.to_dict() for u in self._kullanicilar.values()],
                "kiralamalar": [k.to_dict() for k in self._kiralamalar],
                "odemeler": [o.to_dict() for o in self._odemeler],
                "bakimlar": [b.to_dict() for b in self._bakimlar],
                "counters": {
                    "kid": self._sonraki_kid,
                    "oid": self._sonraki_oid,
                    "bid": self._sonraki_bid
                }
            }
            with open(dosya_adi, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception:
            return False

    def verileri_yukle(self, dosya_adi="data.json") -> bool:
        if not os.path.exists(dosya_adi):
            return False
        try:
            with open(dosya_adi, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self._araclar.clear()
            for d in data.get("araclar", []):
                a = Arac.from_dict(d)
                self._araclar[a.get_arac_id()] = a
                
            self._kullanicilar.clear()
            for d in data.get("kullanicilar", []):
                u = Kullanici.from_dict(d)
                self._kullanicilar[u.get_kullanici_id()] = u
                
            self._kiralamalar.clear()
            for d in data.get("kiralamalar", []):
                arac = self._araclar.get(d["arac_id"])
                kullanici = self._kullanicilar.get(d["kullanici_id"])
                if arac and kullanici:
                    k = Kiralama.from_dict(d, arac, kullanici)
                    self._kiralamalar.append(k)
                    kullanici.kiralama_ekle(k)
                    
            self._odemeler.clear()
            for d in data.get("odemeler", []):
                k = next((x for x in self._kiralamalar if x.get_kiralama_id() == d["kiralama_id"]), None)
                if k:
                    self._odemeler.append(Odeme.from_dict(d, k))
                    
            self._bakimlar.clear()
            for d in data.get("bakimlar", []):
                arac = self._araclar.get(d["arac_id"])
                if arac:
                    self._bakimlar.append(Bakim.from_dict(d, arac))
                    
            counters = data.get("counters", {})
            self._sonraki_kid = counters.get("kid", 1)
            self._sonraki_oid = counters.get("oid", 1)
            self._sonraki_bid = counters.get("bid", 1)
            
            return True
        except Exception:
            return False

    # === Araç Yönetimi ===
    def arac_ekle(self, arac: Arac) -> tuple[bool, str]:
        """Sisteme yeni araç ekler"""
        if arac.get_arac_id() in self._araclar:
            return False, f"ID {arac.get_arac_id()} zaten kayıtlı."
        self._araclar[arac.get_arac_id()] = arac
        return True, f"✓ '{arac.get_tam_ad()}' sisteme eklendi."

    def arac_sil(self, arac_id: str) -> tuple[bool, str]:
        """Sistemden araç siler (yalnızca müsait ve kiralama kaydı olmayanlar)"""
        if arac_id not in self._araclar:
            return False, "Araç bulunamadı."

        arac = self._araclar[arac_id]
        if not arac.get_musait_mi():
            return False, "Araç şu an kirada veya bakımda."

        if any(k.get_arac().get_arac_id() == arac_id for k in self._kiralamalar):
            return False, "Bu araç için kiralama kaydı bulunduğu için silinemez."

        del self._araclar[arac_id]
        return True, f"✓ '{arac.get_tam_ad()}' sistemden silindi."

    def get_araclar(self) -> dict[str, Arac]:
        return self._araclar.copy()

    def get_musait_araclar(self, tip: str = None) -> dict[str, Arac]:
        """Müsait araçları filtreleyerek döndürür"""
        araclar = {k: v for k, v in self._araclar.items() if v.get_musait_mi()}
        if tip:
            araclar = {k: v for k, v in araclar.items() if v.get_tip() == tip}
        return araclar

    # === Kullanıcı Yönetimi ===
    def kullanici_ekle(self, kullanici: Kullanici) -> tuple[bool, str]:
        """Sisteme yeni kullanıcı ekler"""
        if kullanici.get_kullanici_id() in self._kullanicilar:
            return False, f"ID {kullanici.get_kullanici_id()} zaten kayıtlı."
        for u in self._kullanicilar.values():
            if u.get_ehliyet_no() == kullanici.get_ehliyet_no():
                return False, "Bu ehliyet numarası zaten kayıtlı."
        self._kullanicilar[kullanici.get_kullanici_id()] = kullanici
        return True, f"✓ '{kullanici.get_ad()}' kayıt edildi."

    def kullanici_sil(self, kullanici_id: str) -> tuple[bool, str]:
        """Sistemden kullanıcı siler (aktif veya geçmiş kiralama varsa silmez)"""
        if kullanici_id not in self._kullanicilar:
            return False, "Müşteri bulunamadı."

        kullanici = self._kullanicilar[kullanici_id]
        if kullanici.aktif_kiralama():
            return False, "Bu müşteri aktif kiralamaya sahip olduğu için silinemez."

        if any(k.get_kullanici().get_kullanici_id() == kullanici_id for k in self._kiralamalar):
            return False, "Bu müşteri için kiralama kaydı bulunduğu için silinemez."

        del self._kullanicilar[kullanici_id]
        return True, f"✓ '{kullanici.get_ad()}' sistemden silindi."

    def get_kullanicilar(self) -> dict[str, Kullanici]:
        return self._kullanicilar.copy()

    # === Kiralama Yönetimi ===
    def kiralama_baslat(self, arac_id: str, kullanici_id: str, 
                        baslangic: datetime) -> tuple[bool, str]:
        """Yeni kiralama başlatır"""
        if arac_id not in self._araclar:
            return False, "Araç bulunamadı."
        if kullanici_id not in self._kullanicilar:
            return False, "Kullanıcı bulunamadı."
        
        arac = self._araclar[arac_id]
        if not arac.get_musait_mi():
            return False, "Araç şu an başka bir kullanıcıda."
        
        kullanici = self._kullanicilar[kullanici_id]
        if kullanici.aktif_kiralama():
            return False, f"'{kullanici.get_ad()}' zaten aktif bir kiralamaya sahip."

        k = Kiralama(self._sonraki_kid, arac, kullanici, baslangic)
        self._sonraki_kid += 1
        
        ok, msg = k.kiralama_baslat()
        if ok:
            self._kiralamalar.append(k)
            kullanici.kiralama_ekle(k)
        return ok, msg

    def kiralama_bitir(self, kiralama_id: int, bitis: datetime, 
                       eklenen_km: float = 0, 
                       odeme_yontemi: OdemeYontemi = None) -> tuple[bool, str]:
        """Kiralamayı sonlandırır ve opsiyonel olarak ödeme oluşturur"""
        k = next((k for k in self._kiralamalar 
                  if k.get_kiralama_id() == kiralama_id and k.get_aktif()), None)
        if not k:
            return False, "Aktif kiralama bulunamadı."
        
        basarili, msg = k.kiralama_bitir(bitis, eklenen_km)
        
        if basarili and odeme_yontemi:
            self.odeme_olustur(kiralama_id, k.get_toplam_ucret(), odeme_yontemi)
        
        return basarili, msg

    def get_kiralamalar(self) -> list[Kiralama]:
        return list(self._kiralamalar)

    def get_aktif_kiralamalar(self) -> list[Kiralama]:
        return [k for k in self._kiralamalar if k.get_aktif()]

    def get_gecmis_kiralamalar(self) -> list[Kiralama]:
        return [k for k in self._kiralamalar if not k.get_aktif()]

    def toplam_gelir(self) -> float:
        return sum(k.get_toplam_ucret() for k in self._kiralamalar if not k.get_aktif())

    # === Ödeme Yönetimi ===
    def odeme_olustur(self, kiralama_id: int, tutar: float, 
                      yontem: OdemeYontemi, aciklama: str = "") -> tuple[bool, str]:
        """Yeni ödeme kaydı oluşturur"""
        kiralama = next((k for k in self._kiralamalar 
                         if k.get_kiralama_id() == kiralama_id), None)
        if not kiralama or kiralama.get_aktif():
            return False, "Kiralama bulunamadı veya hala aktif."
        
        odeme = Odeme(self._sonraki_oid, kiralama, tutar, yontem, aciklama)
        self._sonraki_oid += 1
        self._odemeler.append(odeme)
        return True, f"💰 Ödeme alındı: ₺{tutar:.2f} ({yontem.value})"

    def get_odemeler(self, kiralama_id: int = None) -> list[dict]:
        """Ödeme listesini filtreleyerek döndürür"""
        odemeler = self._odemeler
        if kiralama_id:
            odemeler = [o for o in odemeler if o._kiralama.get_kiralama_id() == kiralama_id]
        return [o.odeme_detay() for o in odemeler]

    # === Bakım Yönetimi ===
    def bakim_ekle(self, arac_id: str, aciklama: str, tarih: datetime, 
                   maliyet: float = 0.0, tahmini_sure: float = 0) -> tuple[bool, str]:
        """Yeni bakım kaydı ekler ve aracı otomatik bakıma alır"""
        if arac_id not in self._araclar:
            return False, "Araç bulunamadı."
        
        arac = self._araclar[arac_id]
        bakim = Bakim(self._sonraki_bid, arac, aciklama, tarih, maliyet, tahmini_sure)
        self._sonraki_bid += 1
        self._bakimlar.append(bakim)
        
        return True, bakim.bakim_baslat()

    def bakim_tamamla(self, bakim_id: int, gerceklesen_maliyet: float = None) -> tuple[bool, str]:
        """Bakımı tamamlar ve aracı tekrar müsait hale getirir"""
        bakim = next((b for b in self._bakimlar 
                      if b._bakim_id == bakim_id and not b._tamamlandi_mi), None)
        if not bakim:
            return False, "Bakım bulunamadı veya zaten tamamlandı."
        return True, bakim.bakim_bitir(gerceklesen_maliyet)

    def get_bakimlar(self, arac_id: str = None, sadece_aktif: bool = False) -> list[dict]:
        """Bakım listesini filtreleyerek döndürür"""
        bakimlar = self._bakimlar
        if arac_id:
            bakimlar = [b for b in bakimlar if b._arac.get_arac_id() == arac_id]
        if sadece_aktif:
            bakimlar = [b for b in bakimlar if not b._tamamlandi_mi]
        return [b.bakim_detay() for b in bakimlar]

    def get_bakimdaki_araclar(self) -> dict[str, Arac]:
        """Şu anda bakımda olan araçları döndürür"""
        bakimda_ids = {b._arac.get_arac_id() for b in self._bakimlar if not b._tamamlandi_mi}
        return {k: v for k, v in self._araclar.items() if k in bakimda_ids}

    def get_bakim_istatistik(self) -> dict:
        """Bakım istatistiklerini döndürür"""
        return {
            "toplam": len(self._bakimlar),
            "tamamlanan": sum(1 for b in self._bakimlar if b._tamamlandi_mi),
            "bekleyen": sum(1 for b in self._bakimlar if not b._tamamlandi_mi),
            "toplam_maliyet": sum(b._maliyet for b in self._bakimlar if b._tamamlandi_mi)
        }

    # === Raporlama ===
    def rapor_olustur(self) -> Rapor:
        """Yeni rapor nesnesi oluşturur"""
        return Rapor(self)

    def detayli_rapor(self) -> dict:
        """Hızlı sistem özeti döndürür"""
        return self.rapor_olustur().sistem_ozeti()

    # === Yardımcı Metotlar ===
    def __len__(self) -> int:
        return len(self._araclar)

    def __repr__(self) -> str:
        return f"PaylasimSistemi(araç:{len(self._araclar)}, kullanıcı:{len(self._kullanicilar)}, kiralama:{len(self._kiralamalar)})"


# ==================== ÖRNEK KULLANIM ====================
if __name__ == "__main__":
    from datetime import timedelta
    
    print("🚗 Araç Paylaşım Sistemi - Demo\n" + "="*50)
    print("\n📚 Tanımlı Enum'lar:")
    for yontem in OdemeYontemi:
        print(f"  • {yontem.name} = {yontem.value}")
    
    # Sistem başlatma
    sistem = PaylasimSistemi()
    
    # Test verileri ekleme
    arac1 = Arac("A001", "Toyota", "Corolla", "Sedan", 50000, 150.0)
    arac2 = Arac("A002", "Honda", "Civic", "Hatchback", 30000, 175.0)
    kullanici1 = Kullanici("U001", "Ahmet Yılmaz", "EH123456", "05551234567")
    
    sistem.arac_ekle(arac1)
    sistem.arac_ekle(arac2)
    sistem.kullanici_ekle(kullanici1)
    
    # Kiralama başlatma
    baslangic = datetime.now()
    ok, msg = sistem.kiralama_baslat("A001", "U001", baslangic)
    print(f"→ {msg}")
    
    # Kiralama bitirme + ödeme
    bitis = baslangic + timedelta(hours=3, minutes=30)
    ok, msg = sistem.kiralama_bitir(
        kiralama_id=1, 
        bitis=bitis, 
        eklenen_km=120,
        odeme_yontemi=OdemeYontemi.KREDI_KARTI
    )
    print(f"→ {msg}")
    
    # Bakım ekleme
    ok, msg = sistem.bakim_ekle("A002", "Periyodik bakım + yağ değişimi", datetime.now(), 450.0)
    print(f"→ {msg}")
    
    # Raporları görüntüleme
    print("\n📊 Sistem Özeti:")
    for k, v in sistem.detayli_rapor().items():
        print(f"  • {k}: {v}")
    
    print("\n💳 Ödemeler:")
    for o in sistem.get_odemeler():
        print(f"  • #{o['id']} | {o['kullanici']} | {o['tutar']} | {o['yontem']}")
    
    print("\n🔧 Bakımdaki Araçlar:")
    for b in sistem.get_bakimlar(sadece_aktif=True):
        print(f"  • {b['arac']} | {b['aciklama']} | ₺{b['maliyet']}")
