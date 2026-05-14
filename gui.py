import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import locale
# تأكد من وجود ملف backend.py في نفس المجلد
from backend import Arac, Kullanici, PaylasimSistemi, OdemeYontemi

# Türkçe tarih/ay isimleri için locale ayarı
try:
    locale.setlocale(locale.LC_TIME, "tr_TR.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "") 

# ============================================================
# 🎨 PREMIUM RENK PALETİ
# ============================================================
P = {
    "bg":           "#0D0F1A",
    "bg2":          "#131629",
    "card":         "#1A1E35",
    "sidebar":      "#0F1220",
    "border":       "#2A2F52",
    "accent":       "#4F6EF7",
    "accent2":      "#7C3AED",
    "success":      "#10B981",
    "warning":      "#F59E0B",
    "danger":       "#EF4444",
    "text":         "#E8ECFF",
    "text2":        "#8892C0",
    "highlight":    "#6366F1",
    "gold":         "#F0C040",
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def make_shadow_frame(parent, **kwargs):
    """Gölge efekti için iç içe çerçeveler."""
    shadow = ctk.CTkFrame(parent, fg_color="#07090F", corner_radius=kwargs.get("corner_radius", 18) + 2)
    inner = ctk.CTkFrame(shadow, **kwargs)
    inner.pack(fill="both", expand=True, padx=3, pady=3)
    return shadow, inner


class PremiumVehicleGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ AutoRent Pro — Profesyonel Panel")
        self.geometry("1440x900")
        self.minsize(1100, 700)
        self.configure(fg_color=P["bg"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.system = PaylasimSistemi()
        
        #🪄JSON Veri Yükleme
        if not self.system.verileri_yukle("data.json"):
            self.load_sample_data()
            
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._active_btn = None
        self.create_ui()

    def on_closing(self):
        """Uygulama kapanırken verileri JSON'a kaydet."""
        self.system.verileri_kaydet("data.json")
        self.destroy()

    # ─────────────────────────────────────────────
    #  ARAYÜZ YAPISI (Değişiklik yok)
    # ─────────────────────────────────────────────
    def create_ui(self):
        root = ctk.CTkFrame(self, fg_color=P["bg"], corner_radius=0)
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        self._build_sidebar(root)
        self._build_main(root)
        self.show_dashboard()

    def _build_sidebar(self, parent):
        sb = ctk.CTkFrame(parent, width=260, fg_color=P["sidebar"], corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(8, weight=1)

        logo_frame = ctk.CTkFrame(sb, fg_color=P["bg2"], corner_radius=16)
        logo_frame.grid(row=0, column=0, padx=18, pady=(28, 20), sticky="ew")
        ctk.CTkLabel(logo_frame, text="⚡", font=("Arial", 32)).pack(pady=(14, 2))
        ctk.CTkLabel(logo_frame, text="AutoRent Pro",
                     font=("Arial", 18, "bold"), text_color=P["text"]).pack()
        ctk.CTkLabel(logo_frame, text="Araç Kiralama Yönetim Sistemi",
                     font=("Arial", 10), text_color=P["text2"]).pack(pady=(0, 12))

        self._nav_buttons = {}
        nav = [
            ("📊", "Gösterge Paneli", self.show_dashboard),
            ("🚗", "Araç Filosu",     self.show_vehicles),
            ("👥", "Müşteriler",      self.show_clients),
            ("📋", "Kiralamalar",     self.show_bookings),
            ("💳", "Ödeme Yöntemleri", self.show_payment_methods),
            ("📈", "Raporlar",        self.show_reports),
        ]
        for r, (icon, label, cmd) in enumerate(nav, start=1):
            btn = ctk.CTkButton(
                sb, text=f"  {icon}  {label}",
                command=lambda c=cmd, b=label: self._nav_click(c, b),
                fg_color="transparent", hover_color=P["border"],
                text_color=P["text2"], font=("Arial", 14),
                anchor="w", height=48, corner_radius=12
            )
            btn.grid(row=r, column=0, padx=14, pady=3, sticky="ew")
            self._nav_buttons[label] = btn

        sb.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(sb, text="v2.0 — Profesyonel", font=("Arial", 10),
                     text_color=P["text2"]).grid(row=9, column=0, pady=20)

    def _nav_click(self, cmd, label):
        for l, b in self._nav_buttons.items():
            if l == label:
                b.configure(fg_color=P["accent"], text_color=P["text"])
            else:
                b.configure(fg_color="transparent", text_color=P["text2"])
        cmd()

    def _build_main(self, parent):
        main = ctk.CTkFrame(parent, fg_color=P["bg"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(main, fg_color=P["bg2"], height=72, corner_radius=0)
        topbar.grid(row=0, column=0, sticky="ew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(1, weight=1)

        self.page_title = ctk.CTkLabel(
            topbar, text="Gösterge Paneli",
            font=("Arial", 22, "bold"), text_color=P["text"]
        )
        self.page_title.grid(row=0, column=0, padx=32, pady=20, sticky="w")

        self.page_subtitle = ctk.CTkLabel(
            topbar, text=f"📅  {datetime.now().strftime('%d %B %Y %A')}",
            font=("Arial", 12), text_color=P["text2"]
        )
        self.page_subtitle.grid(row=0, column=2, padx=32, pady=20, sticky="e")

        self.content = ctk.CTkScrollableFrame(
            main, fg_color="transparent", corner_radius=0,
            scrollbar_button_color=P["border"],
            scrollbar_button_hover_color=P["accent"]
        )
        self.content.grid(row=1, column=0, sticky="nsew", padx=28, pady=24)

    # ─────────────────────────────────────────────
    #  YARDIMCI FONKSİYONLAR
    # ─────────────────────────────────────────────
    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _card(self, parent, padx=0, pady=(0, 14)):
        shadow = ctk.CTkFrame(parent, fg_color="#08090F", corner_radius=20)
        shadow.pack(fill="x", padx=padx, pady=pady)
        inner = ctk.CTkFrame(shadow, fg_color=P["card"], corner_radius=18,
                              border_width=1, border_color=P["border"])
        inner.pack(fill="both", expand=True, padx=2, pady=2)
        return inner

    def _section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Arial", 13, "bold"),
                     text_color=P["text2"]).pack(anchor="w", pady=(4, 10))

    def _badge(self, parent, text, color, side="right"):
        f = ctk.CTkFrame(parent, fg_color=color, corner_radius=20)
        f.pack(side=side, padx=14, pady=14)
        ctk.CTkLabel(f, text=text, font=("Arial", 11, "bold"),
                     text_color="#fff").pack(padx=12, pady=4)

    def _action_btn(self, parent, text, cmd, color=None, side="left", width=180):
        color = color or P["accent"]
        b = ctk.CTkButton(
            parent, text=text, command=cmd,
            fg_color=color, hover_color=P["highlight"],
            text_color="#fff", font=("Arial", 13, "bold"),
            height=42, corner_radius=22, width=width
        )
        b.pack(side=side, padx=(0, 12), pady=4)
        return b

    def _parse_float(self, value: str, field_name: str) -> float:
        """Virgül veya nokta ile yazılan ondalık değerleri kabul eder."""
        normalized = value.strip().replace(" ", "").replace(",", ".")
        if not normalized:
            raise ValueError(f"{field_name} alanı boş olamaz.")
        try:
            return float(normalized)
        except ValueError:
            raise ValueError(f"{field_name} için geçerli bir sayı girin. Örn: 12.5 veya 12,5")

    # ─────────────────────────────────────────────
    #  GÖSTERGE PANELİ & DİĞER SAYFALAR (Değişiklik yok)
    # ─────────────────────────────────────────────
    def show_dashboard(self):
        self.clear()
        self.page_title.configure(text="Gösterge Paneli")
        self.page_subtitle.configure(text=f"📅  {datetime.now().strftime('%d %B %Y %A')}")

        self._section_title(self.content, "GENEL BAKIŞ")
        stats_row = ctk.CTkFrame(self.content, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 20))

        stats = [
            ("Toplam Araç",      str(len(self.system.get_araclar())),           "🚗", P["accent"]),
            ("Müsait",           str(len(self.system.get_musait_araclar())),    "✅", P["success"]),
            ("Aktif Kiralamalar",str(len(self.system.get_aktif_kiralamalar())), "🔥", P["warning"]),
            ("Gelir",            f"₺{self.system.toplam_gelir():,.2f}",         "💰", P["gold"]),
        ]
        for i, (label, val, icon, color) in enumerate(stats):
            shadow = ctk.CTkFrame(stats_row, fg_color="#08090F", corner_radius=20)
            shadow.grid(row=0, column=i, padx=8, sticky="ew")
            stats_row.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(shadow, fg_color=P["card"], corner_radius=18,
                                 border_width=1, border_color=P["border"])
            card.pack(fill="both", expand=True, padx=2, pady=2)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=20, pady=(20, 4))
            ctk.CTkLabel(top, text=icon, font=("Arial", 26)).pack(side="left")
            ind = ctk.CTkFrame(top, fg_color=color, corner_radius=8, width=6, height=36)
            ind.pack(side="right")
            ind.pack_propagate(False)

            ctk.CTkLabel(card, text=val, font=("Arial", 34, "bold"),
                         text_color=color).pack(anchor="w", padx=22)
            ctk.CTkLabel(card, text=label, font=("Arial", 13),
                         text_color=P["text2"]).pack(anchor="w", padx=22, pady=(0, 18))

        self._section_title(self.content, "HIZLI İŞLEMLER")
        act_row = ctk.CTkFrame(self.content, fg_color="transparent")
        act_row.pack(fill="x", pady=(0, 20))
        self._action_btn(act_row, "＋  Araç Ekle",    self.add_car_window,     P["accent"])
        self._action_btn(act_row, "＋  Yeni Kiralama",self.add_booking_window, P["accent2"])
        self._action_btn(act_row, "＋  Müşteri Ekle", self.add_client_window,  P["success"])

        self._section_title(self.content, "SON EKLENEN ARAÇLAR")
        for arac in list(self.system.get_araclar().values())[:3]:
            self._render_vehicle_card(arac)

    def show_payment_methods(self):
        self.clear()
        self.page_title.configure(text="Ödeme Yöntemleri")
        self.page_subtitle.configure(text="Sistemde tanımlı tahsilat kanalları")

        hero = self._card(self.content, pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(hero, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 12))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left,
            text="Modern tahsilat deneyimi",
            font=("Arial", 18, "bold"),
            text_color=P["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Ödeme yöntemleri, koddaki enum isminden bağımsız olarak kullanıcıya sade ve kurumsal bir dilde sunulur.",
            font=("Arial", 12),
            text_color=P["text2"],
            wraplength=860,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right")

        for value, label, color in [
            ("4", "Yöntem", P["accent"]),
            ("100%", "Tanımlı", P["success"]),
            ("24/7", "Erişim", P["warning"]),
        ]:
            stat = ctk.CTkFrame(right, fg_color=P["bg2"], corner_radius=18)
            stat.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(stat, text=value, font=("Arial", 14, "bold"), text_color=color).pack(padx=14, pady=(8, 0))
            ctk.CTkLabel(stat, text=label, font=("Arial", 10), text_color=P["text2"]).pack(padx=14, pady=(0, 8))

        steps = ctk.CTkFrame(hero, fg_color="transparent")
        steps.pack(fill="x", padx=20, pady=(6, 18))

        step_data = [
            ("1", "Seç", "Müşteri için uygun ödeme kanalını belirle", P["accent"]),
            ("2", "İşle", "Tahsilatı hızlı ve kontrollü şekilde tamamla", P["accent2"]),
            ("3", "Kayıt", "Sistemde finansal izlenebilirliği koru", P["success"]),
        ]
        for idx, (num, title, desc, color) in enumerate(step_data):
            item = ctk.CTkFrame(steps, fg_color=P["bg2"], corner_radius=18)
            item.pack(side="left", fill="x", expand=True, padx=(0 if idx == 0 else 10, 10 if idx < 2 else 0))
            badge = ctk.CTkFrame(item, fg_color=color, width=34, height=34, corner_radius=17)
            badge.pack(side="left", padx=14, pady=14)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=num, font=("Arial", 12, "bold"), text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")
            body = ctk.CTkFrame(item, fg_color="transparent")
            body.pack(side="left", padx=6, pady=12, fill="x", expand=True)
            ctk.CTkLabel(body, text=title, font=("Arial", 13, "bold"), text_color=P["text"]).pack(anchor="w")
            ctk.CTkLabel(body, text=desc, font=("Arial", 10), text_color=P["text2"], wraplength=260, justify="left").pack(anchor="w", pady=(2, 0))

        pay_grid = ctk.CTkFrame(self.content, fg_color="transparent")
        pay_grid.pack(fill="x", pady=(0, 20))

        pay_cards = [
            {"icon": "💳", "title": "Kredi Kartı", "desc": "Anında onay, pratik tahsilat ve yüksek kullanım oranı.", "tag": "En popüler", "color": P["accent"]},
            {"icon": "💵", "title": "Nakit", "desc": "Basit, hızlı ve saha operasyonlarında kullanılabilen klasik yöntem.", "tag": "Yerinde ödeme", "color": P["success"]},
            {"icon": "🏦", "title": "Havale / EFT", "desc": "Kurumsal müşteriler için banka transferi destekli güvenli akış.", "tag": "Kurumsal", "color": P["accent2"]},
            {"icon": "📱", "title": "Mobil Ödeme", "desc": "Dijital cüzdan ve mobil uygulamalarla modern ödeme deneyimi.", "tag": "Dijital kanal", "color": P["warning"]},
        ]

        for i, item in enumerate(pay_cards):
            row = i // 2
            col = i % 2
            pay_grid.grid_columnconfigure(col, weight=1)
            pay_grid.grid_rowconfigure(row, weight=1)

            shadow = ctk.CTkFrame(pay_grid, fg_color="#08090F", corner_radius=20)
            shadow.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            card = ctk.CTkFrame(shadow, fg_color=P["card"], corner_radius=18, border_width=1, border_color=P["border"])
            card.pack(fill="both", expand=True, padx=2, pady=2)

            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=18, pady=(16, 10))

            icon_box = ctk.CTkFrame(header, fg_color=item["color"], width=48, height=48, corner_radius=24)
            icon_box.pack(side="left")
            icon_box.pack_propagate(False)

            ctk.CTkLabel(icon_box, text=item["icon"], font=("Arial", 18, "bold"), text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")

            title_box = ctk.CTkFrame(header, fg_color="transparent")
            title_box.pack(side="left", padx=14, fill="x", expand=True)

            ctk.CTkLabel(title_box, text=item["title"], font=("Arial", 16, "bold"), text_color=P["text"]).pack(anchor="w")
            ctk.CTkLabel(title_box, text="Sistem tanımlı aktif seçenek", font=("Arial", 11), text_color=P["text2"]).pack(anchor="w", pady=(2, 0))

            ctk.CTkFrame(card, fg_color=item["color"], height=3, corner_radius=2).pack(fill="x", padx=18, pady=(0, 12))

            ctk.CTkLabel(card, text=item["desc"], font=("Arial", 12), text_color=P["text2"], wraplength=360, justify="left").pack(anchor="w", padx=18, pady=(0, 14))

            tag = ctk.CTkFrame(card, fg_color=P["bg2"], corner_radius=14)
            tag.pack(anchor="w", padx=18, pady=(0, 16))
            ctk.CTkLabel(tag, text=f"• {item['tag']}", font=("Arial", 10, "bold"), text_color=item["color"]).pack(padx=12, pady=5)

    def show_vehicles(self):
        self.clear()
        self.page_title.configure(text="Araç Filosu Yönetimi")
        self.page_subtitle.configure(text=f"{len(self.system.get_araclar())} araç kayıtlı")

        hdr = ctk.CTkFrame(self.content, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        self._section_title(hdr, "TÜM ARAÇLAR")
        self._action_btn(hdr, "＋  Araç Kaydet", self.add_car_window,
                         P["accent"], side="right", width=170)

        note = ctk.CTkLabel(
            self.content,
            text="Not: Silme işlemi sadece müsait araçlarda ve kiralama geçmişi olmayanlarda çalışır.",
            font=("Arial", 11),
            text_color=P["text2"]
        )
        note.pack(anchor="w", pady=(0, 10))

        for arac in self.system.get_araclar().values():
            self._render_vehicle_card(arac, allow_delete=True)

    def _render_vehicle_card(self, arac, allow_delete=False):
        card = self._card(self.content)
        card.grid_columnconfigure(1, weight=1)

        strip = ctk.CTkFrame(card, fg_color=P["accent"], width=5, corner_radius=3)
        strip.grid(row=0, column=0, rowspan=2, padx=(14, 12), pady=14, sticky="ns")
        strip.grid_propagate(False)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", pady=10)
        ctk.CTkLabel(info, text=f"[{arac.get_arac_id()}] {arac.get_tam_ad()}",
                     font=("Arial", 16, "bold"), text_color=P["text"]).pack(anchor="w")
        ctk.CTkLabel(info, text=f"Tip: {arac.get_tip()}   •   {arac.get_kilometre():,.1f} km",
                     font=("Arial", 12), text_color=P["text2"]).pack(anchor="w")

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=2, padx=20, sticky="e")
        avail = arac.get_musait_mi()
        avail_color = P["success"] if avail else P["danger"]
        avail_text  = "● Müsait" if avail else "● Kirada"
        ctk.CTkLabel(right, text=avail_text, font=("Arial", 12, "bold"),
                     text_color=avail_color).pack(anchor="e")
        ctk.CTkLabel(right, text=f"₺{arac.get_saatlik_ucret():,.2f}/saat",
                     font=("Arial", 20, "bold"), text_color=P["gold"]).pack(anchor="e")

        if allow_delete:
            ctk.CTkButton(
                right,
                text="🗑  Sil",
                command=lambda arac_id=arac.get_arac_id(): self.delete_vehicle(arac_id),
                fg_color=P["danger"],
                hover_color="#DC2626",
                text_color="#fff",
                font=("Arial", 12, "bold"),
                height=34,
                corner_radius=16,
                width=110
            ).pack(anchor="e", pady=(10, 0))

    def delete_vehicle(self, arac_id):
        arac = self.system.get_araclar().get(arac_id)
        if not arac:
            messagebox.showerror("Hata", "Araç bulunamadı.")
            return

        confirm = messagebox.askyesno(
            "Araç Sil",
            f"[{arac_id}] {arac.get_tam_ad()} aracını silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz."
        )
        if not confirm:
            return

        ok, msg = self.system.arac_sil(arac_id)
        if ok:
            if not self.system.verileri_kaydet("data.json"):
                messagebox.showwarning("Uyarı", f"{msg}\n\nAraç silindi ama kayıt dosyasına yazılamadı.")
            else:
                messagebox.showinfo("Başarılı", msg)
            self.show_vehicles()
        else:
            messagebox.showerror("Silme Başarısız", msg)

    def delete_client(self, kullanici_id):
        kullanici = self.system.get_kullanicilar().get(kullanici_id)
        if not kullanici:
            messagebox.showerror("Hata", "Müşteri bulunamadı.")
            return

        confirm = messagebox.askyesno(
            "Müşteri Sil",
            f"[{kullanici_id}] {kullanici.get_ad()} müşterisini silmek istediğinize emin misiniz?\n\nBu işlem geri alınamaz."
        )
        if not confirm:
            return

        ok, msg = self.system.kullanici_sil(kullanici_id)
        if ok:
            if not self.system.verileri_kaydet("data.json"):
                messagebox.showwarning("Uyarı", f"{msg}\n\nMüşteri silindi ama kayıt dosyasına yazılamadı.")
            else:
                messagebox.showinfo("Başarılı", msg)
            self.show_clients()
        else:
            messagebox.showerror("Silme Başarısız", msg)

    def show_clients(self):
        self.clear()
        self.page_title.configure(text="Müşteri Yönetimi")
        self.page_subtitle.configure(text=f"{len(self.system.get_kullanicilar())} müşteri kayıtlı")

        hdr = ctk.CTkFrame(self.content, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        self._section_title(hdr, "TÜM MÜŞTERİLER")
        self._action_btn(hdr, "＋  Müşteri Ekle", self.add_client_window,
                         P["success"], side="right", width=150)

        for user in self.system.get_kullanicilar().values():
            card = self._card(self.content)
            card.grid_columnconfigure(1, weight=1)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=20, pady=16)

            # الصورة الرمزية (Avatar)
            avatar = ctk.CTkFrame(left, fg_color=P["accent2"], width=46, height=46, corner_radius=23)
            avatar.pack(side="left", padx=(0, 14))
            avatar.pack_propagate(False)
            ctk.CTkLabel(avatar, text=user.get_ad()[0].upper(),
                         font=("Arial", 18, "bold"), text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")

            # النصوص
            txt = ctk.CTkFrame(left, fg_color="transparent")
            txt.pack(side="left")
            ctk.CTkLabel(txt, text=user.get_ad(), font=("Arial", 15, "bold"),
                         text_color=P["text"]).pack(anchor="w")
            ctk.CTkLabel(txt, text=f"Müşteri ID: {user.get_kullanici_id()}",
                         font=("Arial", 11), text_color=P["text2"]).pack(anchor="w")

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=24, pady=16)

            license_frame = ctk.CTkFrame(right, fg_color="transparent")
            license_frame.pack(anchor="e")

            ctk.CTkLabel(license_frame, text=f"🪪 Ehliyet: {user.get_ehliyet_no()}",
                         font=("Arial", 12, "bold"), text_color=P["text"]).pack(anchor="e")
            ctk.CTkLabel(license_frame, text="Doğrulandı",
                         font=("Arial", 10), text_color=P["success"]).pack(anchor="e")

            ctk.CTkButton(
                right,
                text="🗑  Sil",
                command=lambda kullanici_id=user.get_kullanici_id(): self.delete_client(kullanici_id),
                fg_color=P["danger"],
                hover_color="#DC2626",
                text_color="#fff",
                font=("Arial", 12, "bold"),
                height=34,
                corner_radius=16,
                width=110
            ).pack(anchor="e", pady=(10, 0))

    def show_bookings(self):
        self.clear()
        self.page_title.configure(text="Kiralamalar ve Rezervasyonlar")
        self.page_subtitle.configure(
            text=f"{len(self.system.get_aktif_kiralamalar())} aktif kiralama")

        hdr = ctk.CTkFrame(self.content, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        self._section_title(hdr, "TÜM KİRALAMALAR")
        self._action_btn(hdr, "＋  Yeni Kiralama", self.add_booking_window,
                         P["accent2"], side="right", width=160)

        rentals = self.system.get_kiralamalar()
        if not rentals:
            ctk.CTkLabel(self.content, text="Henüz kiralama bulunmuyor.",
                         font=("Arial", 16), text_color=P["text2"]).pack(pady=60)
            return

        for k in rentals:
            info = k.kiralama_bilgisi()
            card = self._card(self.content)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=20, pady=16, fill="y")
            ctk.CTkLabel(left, text=f"Kiralama #{info['id']} | Araç: [{info['arac_id']}] {info['arac']}",
                         font=("Arial", 16, "bold"), text_color=P["text"]).pack(anchor="w")
            ctk.CTkLabel(left, text=f"Müşteri: {info['kullanici']} | Süre: {info['sure']}",
                         font=("Arial", 13), text_color=P["text2"]).pack(anchor="w")

            cost_frame = ctk.CTkFrame(card, fg_color="transparent")
            cost_frame.pack(side="left", padx=20, pady=16)
            # Backend'den string olarak '₺123.45' formatında ucret geliyor
            if info["ucret"] != "₺0.00":
                ctk.CTkLabel(cost_frame, text=info["ucret"],
                             font=("Arial", 18, "bold"), text_color=P["gold"]).pack()

            active = info.get("aktif", False)
            
            if active:
                self._action_btn(card, "Kiralamayı Bitir", 
                                 lambda k_id=info["id"]: self.end_booking_window(k_id), 
                                 color=P["danger"], side="right", width=130)
                                 
            self._badge(card, "⚡ AKTİF" if active else "✓ TAMAMLANDI",
                        P["warning"] if active else P["success"])

    def show_reports(self):
        self.clear()
        self.page_title.configure(text="Raporlar ve Analizler")
        self.page_subtitle.configure(text="Finansal genel bakış")

        self._section_title(self.content, "FİNANSAL ÖZET")

        total_rev = self.system.toplam_gelir()
        total_cars = len(self.system.get_araclar())
        avail_cars = len(self.system.get_musait_araclar())
        rentals_count = len(self.system.get_kiralamalar())
        occ_rate = ((total_cars - avail_cars) / total_cars * 100) if total_cars else 0

        metrics = [
            ("💰 Toplam Gelir",         f"₺{total_rev:,.2f}",      P["gold"]),
            ("📦 Toplam Kiralama",       str(rentals_count),        P["accent"]),
            ("🔄 Doluluk Oranı",         f"%{occ_rate:.1f}",        P["warning"]),
            ("🚗 Filo Büyüklüğü",        str(total_cars),           P["text"]),
        ]
        for label, val, color in metrics:
            card = self._card(self.content)
            ctk.CTkLabel(card, text=label, font=("Arial", 13),
                         text_color=P["text2"]).pack(side="left", padx=24, pady=20)
            ctk.CTkLabel(card, text=val, font=("Arial", 22, "bold"),
                         text_color=color).pack(side="right", padx=24)

        self._section_title(self.content, "FİLO DURUMU")
        bar_card = self._card(self.content)
        ctk.CTkLabel(bar_card, text="Filo Kullanım Oranı",
                     font=("Arial", 13), text_color=P["text2"]).pack(anchor="w", padx=20, pady=(16, 4))
        bar = ctk.CTkProgressBar(bar_card, width=400, height=14,
                                  fg_color=P["border"], progress_color=P["accent"],
                                  corner_radius=8)
        bar.set(occ_rate / 100)
        bar.pack(anchor="w", padx=20, pady=(0, 16))
        ctk.CTkLabel(bar_card, text=f"%{occ_rate:.1f} kirada  |  {avail_cars} müsait / {total_cars} toplam",
                     font=("Arial", 12), text_color=P["text2"]).pack(anchor="w", padx=20, pady=(0, 14))

    # ─────────────────────────────────────────────
    #  MODAL PENCERELER
    # ─────────────────────────────────────────────
    def _toplevel(self, title, w=440, h=520):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(fg_color=P["bg2"])
        win.attributes("-topmost", True)
        win.resizable(False, False)
        return win

    def _modal_title(self, win, text):
        ctk.CTkLabel(win, text=text, font=("Arial", 22, "bold"),
                     text_color=P["text"]).pack(pady=(30, 20))

    def _form_field(self, win, label):
        ctk.CTkLabel(win, text=label, font=("Arial", 12),
                     text_color=P["text2"]).pack(anchor="w", padx=40, pady=(6, 0))
        ent = ctk.CTkEntry(
            win, fg_color=P["card"], border_color=P["border"],
            border_width=2, text_color=P["text"],
            placeholder_text_color=P["text2"],
            font=("Arial", 13), height=40, corner_radius=10
        )
        ent.pack(fill="x", padx=40, pady=(2, 0))
        return ent

    def add_car_window(self):
        win = self._toplevel("Araç Kayıt", 440, 580)
        self._modal_title(win, "🚗  Yeni Araç")

        arac_ids = [int(k[1:]) for k in self.system.get_araclar().keys() if k.startswith("V") and k[1:].isdigit()]
        next_id_num = max(arac_ids, default=0) + 1
        auto_id = f"V{next_id_num:02d}"

        ctk.CTkLabel(win, text=f"Araç ID: {auto_id}", font=("Arial", 14, "bold"), 
                     text_color=P["accent"]).pack(pady=(0, 10))

        e_brand = self._form_field(win, "Marka")
        e_model = self._form_field(win, "Model")
        e_type  = self._form_field(win, "Tip (Lüks / Spor / Ekonomi)")
        e_km    = self._form_field(win, "Kilometre (km)")
        e_price = self._form_field(win, "Saatlik Ücret (₺)")

        def save():
            try:
                brand = e_brand.get().strip()
                model = e_model.get().strip()
                typ = e_type.get().strip()
                km_str = e_km.get().strip()
                price_str = e_price.get().strip()
                
                if not all([brand, model, typ, km_str, price_str]):
                    raise ValueError("Lütfen tüm alanları doldurun.")
                    
                km = self._parse_float(km_str, "Kilometre")
                price = self._parse_float(price_str, "Saatlik Ücret")
                if km < 0 or price < 0:
                    raise ValueError("Kilometre ve Ücret negatif olamaz.")
                    
                car = Arac(auto_id, brand, model, typ, km, price)
                self.system.arac_ekle(car)
                messagebox.showinfo("✅ Başarılı", f"Araç {auto_id} başarıyla kaydedildi!")
                win.destroy()
                self.show_vehicles()
            except ValueError as ve:
                messagebox.showerror("Geçersiz Veri", str(ve))
            except Exception as ex:
                messagebox.showerror("Hata", str(ex))

        ctk.CTkButton(win, text="Aracı Kaydet", command=save,
                    fg_color=P["accent"], hover_color=P["highlight"],
                    text_color="#fff", font=("Arial", 14, "bold"),
                    height=44, corner_radius=22
                    ).pack(fill="x", padx=40, pady=24)

    # ============================================================
    # 🔥 DEĞİŞİKLİK: MÜŞTERİ EKLEME PENCERESİ (Otomatik ID + Ayrı Ehliyet)
    # ============================================================
    def add_client_window(self):
        win = self._toplevel("Müşteri Kayıt", 440, 420)
        self._modal_title(win, "👤  Yeni Müşteri")

        kull_ids = [int(k[1:]) for k in self.system.get_kullanicilar().keys() if k.startswith("U") and k[1:].isdigit()]
        next_id_num = max(kull_ids, default=0) + 1
        auto_id = f"U{next_id_num:02d}"

        ctk.CTkLabel(win, text=f"Müşteri ID: {auto_id}", font=("Arial", 14, "bold"), 
                     text_color=P["accent"]).pack(pady=(0, 10))

        e_name    = self._form_field(win, "Ad Soyad")
        e_license = self._form_field(win, "Ehliyet Numarası")

        def save():
            try:
                name = e_name.get().strip()
                license = e_license.get().strip()
                if not name or not license:
                    raise ValueError("Lütfen tüm alanları doldurun.")
                    
                user = Kullanici(auto_id, name, license)
                self.system.kullanici_ekle(user)
                messagebox.showinfo("✅ Başarılı", f"Müşteri {auto_id} başarıyla kaydedildi!")
                win.destroy()
                self.show_clients()
            except ValueError as ve:
                messagebox.showerror("Geçersiz Veri", str(ve))
            except Exception as ex:
                messagebox.showerror("Hata", str(ex))

        ctk.CTkButton(win, text="Müşteriyi Kaydet", command=save,
                      fg_color=P["success"], hover_color=P["highlight"],
                      text_color="#fff", font=("Arial", 14, "bold"),
                      height=44, corner_radius=22
                      ).pack(fill="x", padx=40, pady=28)
    def end_booking_window(self, kiralama_id):
        win = self._toplevel("Kiralama Bitir", 440, 320)
        self._modal_title(win, "🛑 Kiralamayı Bitir")

        ctk.CTkLabel(win, text="🎁 Kampanya: 3 Gün (72 Saat) ve üzeri %30 İndirim!", 
                     font=("Arial", 12, "bold"), text_color=P["success"]).pack(pady=(0, 10))

        e_hours = self._form_field(win, "Geçen Süre (Saat) - Örn: 75")
        
        def save():
            try:
                hours_str = e_hours.get().strip()
                if not hours_str:
                    raise ValueError("Lütfen geçen süreyi saat cinsinden girin.")
                
                hours = self._parse_float(hours_str, "Geçen Süre")
                if hours <= 0:
                    raise ValueError("Süre 0'dan büyük olmalıdır.")
                    
                k = next((k for k in self.system.get_aktif_kiralamalar() if k.get_kiralama_id() == kiralama_id), None)
                if not k:
                    raise ValueError("Aktif kiralama bulunamadı.")
                
                from datetime import timedelta
                bitis = k.get_baslangic_saati() + timedelta(hours=hours)
                
                ok, msg = self.system.kiralama_bitir(kiralama_id, bitis)
                if ok:
                    messagebox.showinfo("✅ Kiralama Bitti", msg)
                    win.destroy()
                    self.show_bookings()
                else:
                    messagebox.showerror("Hata", msg)
            except ValueError as ve:
                messagebox.showerror("Geçersiz Veri", str(ve))
            except Exception as ex:
                messagebox.showerror("Hata", str(ex))

        ctk.CTkButton(win, text="Kiralamayı Sonlandır", command=save,
                      fg_color=P["danger"], hover_color=P["highlight"],
                      text_color="#fff", font=("Arial", 14, "bold"),
                      height=44, corner_radius=22
                      ).pack(fill="x", padx=40, pady=28)

    def add_booking_window(self):
        win = self._toplevel("Yeni Kiralama", 440, 480)
        self._modal_title(win, "📋  Yeni Kiralama")

        e_user  = self._form_field(win, "Müşteri ID")
        e_car   = self._form_field(win, "Araç ID")
        e_hours = self._form_field(win, "Tahmini Süre (saat)")

        ctk.CTkLabel(win, text="🎁 Kampanya: 72 Saat (3 Gün) ve üzeri\nkiralamalarda %30 anında indirim!", 
                     font=("Arial", 12, "bold"), text_color=P["success"]).pack(pady=(15, 0))

        def save():
            try:
                uid   = e_user.get().strip()
                vid   = e_car.get().strip()
                hours_str = e_hours.get().strip()
                
                if not all([uid, vid, hours_str]):
                    raise ValueError("Lütfen tüm alanları doldurun.")
                    
                hours = self._parse_float(hours_str, "Tahmini Süre")
                if hours <= 0:
                    raise ValueError("Süre 0'dan büyük olmalıdır.")
                
                kullanicilar = self.system.get_kullanicilar()
                araclar      = self.system.get_araclar()
                
                if uid not in kullanicilar:
                    raise ValueError(f"'{uid}' ID'li müşteri bulunamadı")
                if vid not in araclar:
                    raise ValueError(f"'{vid}' ID'li araç bulunamadı")
                    
                from datetime import timedelta
                baslangic = datetime.now()
                
                ok, msg = self.system.kiralama_baslat(vid, uid, baslangic)
                if ok:
                    messagebox.showinfo("✅ Başarılı", "Kiralama başarıyla başlatıldı!\n(İndirim kiralama bitişinde hesaplanacaktır.)")
                    win.destroy()
                    self.show_bookings()
                else:
                    messagebox.showerror("Hata", msg)
            except ValueError as ve:
                messagebox.showerror("Geçersiz Veri", str(ve))
            except Exception as ex:
                messagebox.showerror("Hata", str(ex))

        ctk.CTkButton(win, text="Kiralamayı Onayla", command=save,
                      fg_color=P["accent2"], hover_color=P["highlight"],
                      text_color="#fff", font=("Arial", 14, "bold"),
                      height=44, corner_radius=22
                      ).pack(fill="x", padx=40, pady=28)

    # ─────────────────────────────────────────────
    #  ÖRNEK VERİLER
    # ─────────────────────────────────────────────
    def load_sample_data(self):
        self.system.arac_ekle(Arac("V01", "Mercedes", "S-Class",  "Lüks",     15000, 1200))
        self.system.arac_ekle(Arac("V02", "BMW",      "M4",       "Spor",      8000, 1500))
        self.system.arac_ekle(Arac("V03", "Tesla",    "Model 3",  "Elektrikli",5000, 900))
        self.system.arac_ekle(Arac("V04", "Porsche",  "Cayenne",  "SUV",      20000, 1800))
        
        # Örnek kullanıcılar (ID, Ad, Ehliyet No)
        self.system.kullanici_ekle(Kullanici("U01", "Ahmet Yılmaz",    "A1234567"))
        self.system.kullanici_ekle(Kullanici("U02", "Ayşe Demir",      "B9876543"))


if __name__ == "__main__":
    app = PremiumVehicleGUI()
    app.mainloop()
