import os
import sys
import random
import customtkinter as ctk
from models import Database, ProductManager, CategoryManager, SaleManager, ReportManager


def resource_path(relative_path):
    """PyInstaller ile paketlenmiş dosyaları bulmak için yardımcı fonksiyon."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), relative_path)

# ── Dark Mode Tema Ayarları ──────────────────────────────────────────────
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ── Renk Paleti ──────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":       "#0f1117",      # Ana arka plan
    "bg_secondary":     "#161b22",      # Panel arka planı
    "bg_card":          "#1c2333",      # Kart arka planı
    "bg_input":         "#21283b",      # Input arka planı
    "bg_hover":         "#2a3346",      # Hover arka planı
    "border":           "#30363d",      # Border rengi
    "text_primary":     "#e6edf3",      # Ana metin
    "text_secondary":   "#8b949e",      # İkincil metin
    "text_muted":       "#6e7681",      # Soluk metin
    "accent_blue":      "#58a6ff",      # Mavi vurgu
    "accent_purple":    "#bc8cff",      # Mor vurgu
    "accent_green":     "#3fb950",      # Yeşil (başarı)
    "accent_red":       "#f85149",      # Kırmızı (hata/sil)
    "accent_orange":    "#d29922",      # Turuncu (uyarı/satış)
    "accent_cyan":      "#39d2c0",      # Cyan (arama)
    "accent_yellow":    "#e3b341",      # Sarı (yenile)
    "header_gradient":  "#1f6feb",      # Header
    "btn_save":         "#238636",      # Kaydet butonu
    "btn_save_hover":   "#2ea043",
    "btn_edit":         "#1f6feb",      # Düzenle butonu
    "btn_edit_hover":   "#388bfd",
    "btn_delete":       "#da3633",      # Sil butonu
    "btn_delete_hover": "#f85149",
    "btn_sell":         "#9e6a03",      # Satış butonu
    "btn_sell_hover":   "#bb8009",
    "btn_search":       "#1b7c83",      # Arama butonu
    "btn_search_hover": "#238b92",
    "btn_category":     "#6e40c9",      # Kategori butonu
    "btn_category_hover": "#8957e5",
    "btn_neutral":      "#30363d",      # Nötr buton
    "btn_neutral_hover":"#484f58",
    "scrollbar":        "#484f58",
    "warning_bg":       "#2a1f00",      # Uyarı arka plan
    "warning_text":     "#d29922",      # Uyarı metin
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mağaza Stok Takip v1.0.0")
        self.geometry("1100x680")
        self.minsize(1100, 680)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_primary"])

        # ── Pencere İkonu ────────────────────────────────────────────────
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            self.after(200, lambda: self.iconbitmap(icon_path))

        # ── MongoDB Bağlantısı ───────────────────────────────────────────
        self.db = Database()
        if not self.db.connect():
            self._show_connection_error()
            return

        self.cm = CategoryManager(self.db)
        self.cm.load_categories()

        self.pm = ProductManager(self.db, self.cm)
        self.pm.load_products()

        self.sm = SaleManager(self.db)
        self.rm = ReportManager(self.pm, self.cm, self.sm)

        # ── Header ───────────────────────────────────────────────────────
        self.header = ctk.CTkFrame(self, fg_color=COLORS["header_gradient"], corner_radius=0, height=56)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        self.header.grid_propagate(False)
        ctk.CTkLabel(
            self.header,
            text="  🛒  Mağaza Stok Takip Sistemi",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#ffffff",
        ).pack(side="left", padx=20, pady=12)

        # ── Layout Grid ─────────────────────────────────────────────────
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Sol Panel: Ürün Listesi ──────────────────────────────────────
        self.left_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=(16, 8), pady=(12, 16))

        # Sol panel başlık
        left_header = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        left_header.pack(fill="x", padx=14, pady=(14, 6))
        ctk.CTkLabel(
            left_header,
            text="📦  Ürünler",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(side="left")
        self.product_count_label = ctk.CTkLabel(
            left_header,
            text="0 ürün",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
        )
        self.product_count_label.pack(side="right")

        # Ürün listesi (scrollable frame — kartlarla)
        self.product_scroll = ctk.CTkScrollableFrame(
            self.left_frame,
            width=360,
            fg_color=COLORS["bg_card"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8,
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["bg_hover"],
        )
        self.product_scroll.pack(fill="both", expand=True, padx=14, pady=6)
        self.product_cards = []  # ürün kart widget referansları


        self._make_button(self.left_frame, "➕ Yeni Ürün Ekle", COLORS["btn_save"], COLORS["btn_save_hover"],
                          self.add_product, height=36).pack(fill="x", padx=14, pady=(2, 14))

        # ── Sağ Panel: Detaylar ve Aksiyonlar ────────────────────────────
        self.right_frame = ctk.CTkFrame(
            self, fg_color=COLORS["bg_secondary"], corner_radius=12, border_width=1,
            border_color=COLORS["border"]
        )
        self.right_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 16), pady=(12, 16))

        # Üst araç çubuğu
        self.toolbar = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.toolbar.pack(fill="x", padx=14, pady=(14, 6))

        toolbar_buttons = [
            ("📂 Kategoriler", COLORS["btn_category"], COLORS["btn_category_hover"], self.manage_categories),
            ("🔍 Ara", COLORS["btn_search"], COLORS["btn_search_hover"], self.search_products),
            ("📊 Raporlar", COLORS["accent_cyan"], COLORS["btn_search_hover"], self.show_reports),
            ("🗒️ Tümü", COLORS["btn_neutral"], COLORS["btn_neutral_hover"], self.show_all_products),
            ("🔄 Yenile", COLORS["btn_neutral"], COLORS["btn_neutral_hover"], self.reload_data),
            ("🧪 Mock", COLORS["accent_orange"], COLORS["btn_sell_hover"], self.generate_mock_data),
        ]
        for i, (text, fg, hover, cmd) in enumerate(toolbar_buttons):
            self.toolbar.grid_columnconfigure(i, weight=1)
            self._make_button(self.toolbar, text, fg, hover, cmd, height=32,
                              font_size=12).grid(row=0, column=i, padx=3, sticky="ew")

        # Ayırıcı çizgi
        separator = ctk.CTkFrame(self.right_frame, fg_color=COLORS["border"], height=1)
        separator.pack(fill="x", padx=14, pady=8)

        # Detay paneli
        self.details_box = ctk.CTkFrame(
            self.right_frame, fg_color=COLORS["bg_card"], corner_radius=10,
            border_width=1, border_color=COLORS["border"]
        )
        self.details_box.pack(fill="both", expand=True, padx=14, pady=(4, 14))

        self.details_title = ctk.CTkLabel(
            self.details_box,
            text="📋 Ürün Detayları",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=COLORS["accent_blue"],
        )
        self.details_title.pack(anchor="nw", padx=16, pady=(14, 4))

        self.details_content = ctk.CTkFrame(self.details_box, fg_color="transparent")
        self.details_content.pack(fill="both", expand=True, padx=16, pady=(4, 14))

        # ── State ────────────────────────────────────────────────────────
        self.last_selected_index = None

        # İlk yükleme
        self.refresh_product_list()

    # ══════════════════════════════════════════════════════════════════════
    # UI Yardımcı Fonksiyonları
    # ══════════════════════════════════════════════════════════════════════

    def _make_button(self, parent, text, fg_color, hover_color, command,
                     height=34, font_size=13, text_color="#ffffff"):
        """Stillenmiş buton oluşturur."""
        return ctk.CTkButton(
            parent, text=text, command=command,
            fg_color=fg_color, hover_color=hover_color,
            text_color=text_color,
            font=ctk.CTkFont(family="Segoe UI", size=font_size, weight="bold"),
            corner_radius=8, height=height, border_width=0,
        )

    def _make_label(self, parent, text, size=13, bold=False, color=None):
        """Stillenmiş etiket oluşturur."""
        return ctk.CTkLabel(
            parent, text=text,
            font=ctk.CTkFont(family="Segoe UI", size=size,
                             weight="bold" if bold else "normal"),
            text_color=color or COLORS["text_primary"],
        )

    def _make_entry(self, parent, textvariable=None, width=None, placeholder=None):
        """Stillenmiş input oluşturur."""
        return ctk.CTkEntry(
            parent, textvariable=textvariable,
            width=width or 200,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            placeholder_text=placeholder,
        )

    def _make_combobox(self, parent, values, variable):
        """Stillenmiş combobox oluşturur."""
        return ctk.CTkComboBox(
            parent, values=values, variable=variable,
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"],
            button_color=COLORS["accent_blue"],
            button_hover_color=COLORS["btn_edit_hover"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_primary"],
            dropdown_hover_color=COLORS["bg_hover"],
            border_width=1,
            corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )

    def clear_details_content(self):
        for widget in self.details_content.winfo_children():
            widget.destroy()

    # ══════════════════════════════════════════════════════════════════════
    # Modal / Mesaj Kutuları
    # ══════════════════════════════════════════════════════════════════════

    def _modal(self, title, body, buttons, icon="ℹ️"):
        win = ctk.CTkToplevel(self)
        win.title(title)
        win.transient(self)
        win.grab_set()
        win.configure(fg_color=COLORS["bg_secondary"])
        win.geometry("420x180")
        win.resizable(False, False)

        # İkon ve mesaj
        msg_frame = ctk.CTkFrame(win, fg_color="transparent")
        msg_frame.pack(fill="x", padx=24, pady=(24, 12))
        ctk.CTkLabel(
            msg_frame, text=icon,
            font=ctk.CTkFont(size=28),
        ).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(
            msg_frame, text=body,
            wraplength=320,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_primary"],
            justify="left",
        ).pack(side="left", fill="x", expand=True)

        # Butonlar
        res = {"value": None}
        btn_frame = ctk.CTkFrame(win, fg_color="transparent")
        btn_frame.pack(pady=(8, 20))

        def mkcb(v):
            def cb():
                res["value"] = v
                win.destroy()
            return cb

        for btext, bval in buttons:
            self._make_button(btn_frame, btext, COLORS["accent_blue"], COLORS["btn_edit_hover"],
                              mkcb(bval), height=32, font_size=12).pack(side="left", padx=6)

        self.wait_window(win)
        return res["value"]

    def show_info(self, title, message):
        self._modal(title, message, [("Tamam", True)], icon="✅")

    def show_warning(self, title, message):
        self._modal(title, message, [("Tamam", True)], icon="⚠️")

    def show_error(self, title, message):
        self._modal(title, message, [("Tamam", True)], icon="❌")

    def ask_yes_no(self, title, message):
        return bool(self._modal(title, message, [("Evet", True), ("Hayır", False)], icon="❓"))

    def _show_connection_error(self):
        """MongoDB bağlantı hatası ekranı."""
        err_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=16)
        err_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(
            err_frame, text="❌", font=ctk.CTkFont(size=48),
        ).pack(padx=40, pady=(30, 10))
        ctk.CTkLabel(
            err_frame,
            text="MongoDB Bağlantı Hatası",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["accent_red"],
        ).pack(padx=40)
        ctk.CTkLabel(
            err_frame,
            text="MongoDB sunucusuna bağlanılamadı.\nLütfen MongoDB'nin çalıştığından emin olun.\n\nVarsayılan: mongodb://localhost:27017",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS["text_secondary"],
            justify="center",
        ).pack(padx=40, pady=(8, 20))
        self._make_button(err_frame, "Tekrar Dene", COLORS["accent_blue"], COLORS["btn_edit_hover"],
                          self._retry_connection).pack(padx=40, pady=(0, 30))

    def _retry_connection(self):
        if self.db.connect():
            # Tüm widget'ları temizle ve yeniden başlat
            for w in self.winfo_children():
                w.destroy()
            self.__init__()
        else:
            self.show_error("Hata", "MongoDB'ye hâlâ bağlanılamıyor!")

    # ══════════════════════════════════════════════════════════════════════
    # Ürün Listesi
    # ══════════════════════════════════════════════════════════════════════

    def refresh_product_list(self, filtered=None):
        self._build_product_cards(filtered)
        self.clear_details_content()
        self.last_selected_index = None

    def _refresh_product_list_silent(self, filtered=None):
        """Ürün listesini günceller ama detay panelini temizlemez."""
        self._build_product_cards(filtered)
        self.last_selected_index = None

    def _build_product_cards(self, filtered=None):
        """Ürün kartlarını oluşturur."""
        # Mevcut kartları temizle
        for card in self.product_cards:
            card.destroy()
        self.product_cards = []

        source = filtered if filtered is not None else self.pm.products
        self.product_count_label.configure(text=f"{len(source)} ürün")
        self._current_source = source  # seçim için referans tut

        for idx, p in enumerate(source):
            cat_name = self.pm.get_category_name(p)
            is_critical = p.stock <= p.critical_stock

            # Kart frame
            card = ctk.CTkFrame(
                self.product_scroll,
                fg_color=COLORS["bg_input"] if idx % 2 == 0 else COLORS["bg_card"],
                corner_radius=6,
                border_width=1,
                border_color=COLORS["accent_red"] if is_critical else COLORS["border"],
                cursor="hand2",
            )
            card.pack(fill="x", padx=6, pady=2)

            # Üst satır: ürün adı
            name_color = COLORS["accent_red"] if is_critical else COLORS["text_primary"]
            warn_prefix = "⚠️ " if is_critical else ""
            name_label = ctk.CTkLabel(
                card,
                text=f"{warn_prefix}{p.name}",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=name_color,
                anchor="w",
            )
            name_label.pack(fill="x", padx=10, pady=(6, 0))

            # Alt satır: kategori | stok | fiyat
            info_text = f"{cat_name}  •  Stok: {p.stock}  •  {p.price:.2f} ₺"
            info_label = ctk.CTkLabel(
                card,
                text=info_text,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS["text_muted"],
                anchor="w",
            )
            info_label.pack(fill="x", padx=10, pady=(0, 6))

            # Tıklama eventi
            def on_click(event, i=idx):
                self._select_product_card(i)

            card.bind("<Button-1>", on_click)
            name_label.bind("<Button-1>", on_click)
            info_label.bind("<Button-1>", on_click)

            # Hover efekti
            def on_enter(event, c=card):
                c.configure(fg_color=COLORS["bg_hover"])

            def on_leave(event, c=card, i=idx):
                if self.last_selected_index == i:
                    c.configure(fg_color=COLORS["accent_blue"])
                else:
                    c.configure(fg_color=COLORS["bg_input"] if i % 2 == 0 else COLORS["bg_card"])

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            info_label.bind("<Enter>", on_enter)
            info_label.bind("<Leave>", on_leave)

            self.product_cards.append(card)

    def _select_product_card(self, index):
        """Bir ürün kartını seç ve vurgula."""
        # Önceki seçimi temizle
        if self.last_selected_index is not None and self.last_selected_index < len(self.product_cards):
            old_card = self.product_cards[self.last_selected_index]
            old_card.configure(
                fg_color=COLORS["bg_input"] if self.last_selected_index % 2 == 0 else COLORS["bg_card"]
            )

        self.last_selected_index = index
        source = getattr(self, '_current_source', self.pm.products)

        if index < len(self.product_cards):
            self.product_cards[index].configure(fg_color=COLORS["accent_blue"])

        if index < len(source):
            product = source[index]
            self.show_product_details(product)

    def show_all_products(self):
        self.pm.load_products()
        self._refresh_product_list_silent()

    def show_product_details(self, product):
        self.clear_details_content()
        self.details_title.configure(text="📋 Ürün Detayları")

        cat_name = self.pm.get_category_name(product)

        # Bilgi kartı
        info_frame = ctk.CTkFrame(self.details_content, fg_color=COLORS["bg_input"], corner_radius=8,
                                  border_width=1, border_color=COLORS["border"])
        info_frame.pack(fill="x", pady=(0, 10))

        info_items = [
            ("Ürün Adı", product.name, COLORS["text_primary"]),
            ("Kategori", cat_name, COLORS["accent_purple"]),
            ("Fiyat", f"{product.price:.2f} ₺", COLORS["accent_green"]),
            ("Stok", str(product.stock), COLORS["accent_orange"] if product.stock <= product.critical_stock else COLORS["accent_cyan"]),
            ("Kritik Stok", str(product.critical_stock), COLORS["text_muted"]),
        ]
        for i, (label, value, color) in enumerate(info_items):
            row_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=12, pady=3)
            self._make_label(row_frame, f"{label}:", size=12, color=COLORS["text_secondary"]).pack(side="left")
            self._make_label(row_frame, value, size=12, bold=True, color=color).pack(side="right")

        # Kritik stok uyarısı
        if product.stock <= product.critical_stock:
            warn_frame = ctk.CTkFrame(self.details_content, fg_color=COLORS["warning_bg"], corner_radius=6)
            warn_frame.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(
                warn_frame, text="⚠️  Stok kritik seviyede!",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["warning_text"],
            ).pack(padx=12, pady=6)

        # Stok güncelleme
        stock_section = ctk.CTkFrame(self.details_content, fg_color="transparent")
        stock_section.pack(fill="x", pady=(0, 6))
        self._make_label(stock_section, "Stok Güncelle:", size=12, color=COLORS["text_secondary"]).pack(side="left")
        stock_var = ctk.IntVar(value=product.stock)
        self._make_entry(stock_section, textvariable=stock_var, width=90).pack(side="left", padx=8)

        def update_stock():
            try:
                self.pm.update_stock(product, int(stock_var.get()))
                self.pm.load_products()
                self.refresh_product_list()
                # Ürünü tekrar bul
                for p in self.pm.products:
                    if p._id == product._id:
                        self.show_product_details(p)
                        break
            except Exception:
                self.show_error("Hata", "Geçersiz değer girdiniz.")

        self._make_button(stock_section, "Güncelle", COLORS["btn_save"], COLORS["btn_save_hover"],
                          update_stock, height=30, font_size=12).pack(side="left")

        # Satış
        sale_section = ctk.CTkFrame(self.details_content, fg_color="transparent")
        sale_section.pack(fill="x", pady=(0, 6))
        self._make_label(sale_section, "Satış Miktarı:", size=12, color=COLORS["text_secondary"]).pack(side="left")
        sale_var = ctk.IntVar(value=1)
        self._make_entry(sale_section, textvariable=sale_var, width=90).pack(side="left", padx=8)

        def do_sale():
            try:
                qty = int(sale_var.get())
                self.pm.sell_product(product, qty)
                # Satış kaydını oluştur
                self.sm.record_sale(product, qty)
                self.show_info("Satış", f"{qty} adet {product.name} satıldı.")
                self.pm.load_products()
                self.refresh_product_list()
                for p in self.pm.products:
                    if p._id == product._id:
                        self.show_product_details(p)
                        break
            except ValueError as e:
                self.show_error("Hata", str(e))
            except Exception:
                self.show_error("Hata", "Geçersiz değer.")

        self._make_button(sale_section, "Satış Yap", COLORS["btn_sell"], COLORS["btn_sell_hover"],
                          do_sale, height=30, font_size=12).pack(side="left")

        # Alt butonlar
        bottom_btns = ctk.CTkFrame(self.details_content, fg_color="transparent")
        bottom_btns.pack(fill="x", pady=(10, 0))
        self._make_button(bottom_btns, "✏️ Düzenle", COLORS["btn_edit"], COLORS["btn_edit_hover"],
                          lambda: self.show_edit_product_form(product), height=32).pack(side="left", padx=(0, 8))
        self._make_button(bottom_btns, "🗑️ Sil", COLORS["btn_delete"], COLORS["btn_delete_hover"],
                          lambda: self.show_delete_product(product), height=32).pack(side="left")

    # ══════════════════════════════════════════════════════════════════════
    # Ürün CRUD İşlemleri
    # ══════════════════════════════════════════════════════════════════════

    def add_product(self):
        self.clear_details_content()
        self.details_title.configure(text="➕ Yeni Ürün Ekle")

        name_var = ctk.StringVar()
        price_var = ctk.StringVar()
        stock_var = ctk.StringVar()
        critical_var = ctk.StringVar()
        cat_names = [c.name for c in self.cm.categories]
        cat_var = ctk.StringVar(value=cat_names[0] if cat_names else "")

        fields = [
            ("Ürün Adı", name_var, "Ürün adını girin..."),
            ("Fiyat (₺)", price_var, "0.00"),
            ("Stok Miktarı", stock_var, "0"),
            ("Kritik Stok", critical_var, "0"),
        ]
        for row, (label, var, placeholder) in enumerate(fields):
            self._make_label(self.details_content, f"{label}:", size=12,
                             color=COLORS["text_secondary"]).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
            self._make_entry(self.details_content, textvariable=var,
                             placeholder=placeholder).grid(row=row, column=1, sticky="ew", pady=5)

        row = len(fields)
        self._make_label(self.details_content, "Kategori:", size=12,
                         color=COLORS["text_secondary"]).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
        if cat_names:
            self._make_combobox(self.details_content, cat_names, cat_var).grid(row=row, column=1, sticky="ew", pady=5)
        else:
            self._make_label(self.details_content, "Kategori yok — önce oluşturun", size=11,
                             color=COLORS["accent_red"]).grid(row=row, column=1, sticky="w", pady=5)
        row += 1

        self.details_content.grid_columnconfigure(1, weight=1)

        def submit():
            try:
                name = name_var.get().strip()
                if not name:
                    self.show_warning("Uyarı", "Ürün adı boş olamaz.")
                    return
                price = float(price_var.get())
                stock = int(stock_var.get())
                critical = int(critical_var.get())
                cat = self.cm.get_category_by_name(cat_var.get())
                cat_id = cat._id if cat else None
                self.pm.create_product(name, cat_id, price, stock, critical)
                self.pm.load_products()
                self.refresh_product_list()
                self.show_info("Başarılı", f"'{name}' ürünü eklendi.")
            except ValueError:
                self.show_warning("Uyarı", "Geçersiz değer girdiniz.")

        self._make_button(self.details_content, "💾 Kaydet", COLORS["btn_save"], COLORS["btn_save_hover"],
                          submit).grid(row=row, column=0, columnspan=2, pady=14, sticky="ew")

    def edit_product(self):
        if self.last_selected_index is None:
            self.show_warning("Uyarı", "Önce bir ürün seçin.")
            return
        product = self.pm.products[self.last_selected_index]
        self.show_edit_product_form(product)

    def show_edit_product_form(self, product):
        self.clear_details_content()
        self.details_title.configure(text="✏️ Ürün Düzenle")

        name_var = ctk.StringVar(value=product.name)
        price_var = ctk.StringVar(value=str(product.price))
        stock_var = ctk.StringVar(value=str(product.stock))
        critical_var = ctk.StringVar(value=str(product.critical_stock))
        cat_names = [c.name for c in self.cm.categories]
        current_cat = self.pm.get_category_name(product)
        cat_var = ctk.StringVar(value=current_cat)

        fields = [
            ("Ürün Adı", name_var),
            ("Fiyat (₺)", price_var),
            ("Stok Miktarı", stock_var),
            ("Kritik Stok", critical_var),
        ]
        for row, (label, var) in enumerate(fields):
            self._make_label(self.details_content, f"{label}:", size=12,
                             color=COLORS["text_secondary"]).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
            self._make_entry(self.details_content, textvariable=var).grid(row=row, column=1, sticky="ew", pady=5)

        row = len(fields)
        self._make_label(self.details_content, "Kategori:", size=12,
                         color=COLORS["text_secondary"]).grid(row=row, column=0, sticky="w", pady=5, padx=(0, 12))
        self._make_combobox(self.details_content, cat_names, cat_var).grid(row=row, column=1, sticky="ew", pady=5)
        row += 1

        self.details_content.grid_columnconfigure(1, weight=1)

        def submit():
            try:
                name = name_var.get().strip()
                if not name:
                    self.show_warning("Uyarı", "Ürün adı boş olamaz.")
                    return
                product.name = name
                product.price = float(price_var.get())
                product.stock = int(stock_var.get())
                product.critical_stock = int(critical_var.get())
                cat = self.cm.get_category_by_name(cat_var.get())
                product.category_id = cat._id if cat else None
                self.pm.update_product(product)
                self.pm.load_products()
                self.refresh_product_list()
                self.show_info("Başarılı", f"'{name}' güncellendi.")
            except ValueError:
                self.show_warning("Uyarı", "Geçersiz değer girdiniz.")

        self._make_button(self.details_content, "💾 Kaydet", COLORS["btn_edit"], COLORS["btn_edit_hover"],
                          submit).grid(row=row, column=0, columnspan=2, pady=14, sticky="ew")

    def delete_product(self):
        if self.last_selected_index is None:
            self.show_warning("Uyarı", "Önce bir ürün seçin.")
            return
        product = self.pm.products[self.last_selected_index]
        self.show_delete_product(product)

    def show_delete_product(self, product):
        self.clear_details_content()
        self.details_title.configure(text="🗑️ Ürün Sil")

        # Uyarı mesajı
        warn_frame = ctk.CTkFrame(self.details_content, fg_color=COLORS["warning_bg"], corner_radius=8)
        warn_frame.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(
            warn_frame,
            text=f"⚠️  '{product.name}' ürünü kalıcı olarak silinecek.\nBu işlem geri alınamaz!",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["warning_text"],
            justify="left",
        ).pack(padx=16, pady=12)

        btn_row = ctk.CTkFrame(self.details_content, fg_color="transparent")
        btn_row.pack(pady=8)

        def do_delete():
            self.pm.delete_product(product)
            self.pm.load_products()
            self.refresh_product_list()
            self.show_info("Silindi", f"'{product.name}' silindi.")

        self._make_button(btn_row, "Evet, Sil", COLORS["btn_delete"], COLORS["btn_delete_hover"],
                          do_delete, height=34).pack(side="left", padx=6)
        self._make_button(btn_row, "Vazgeç", COLORS["btn_neutral"], COLORS["btn_neutral_hover"],
                          self.clear_details_content, height=34).pack(side="left", padx=6)

    def sell_product(self):
        if self.last_selected_index is None:
            self.show_warning("Uyarı", "Önce bir ürün seçin.")
            return
        product = self.pm.products[self.last_selected_index]
        self.show_product_details(product)

    # ══════════════════════════════════════════════════════════════════════
    # Arama
    # ══════════════════════════════════════════════════════════════════════

    def search_products(self):
        self.clear_details_content()
        self.details_title.configure(text="🔍 Ürün Ara")

        name_var = ctk.StringVar()
        cat_names = ["(Hepsi)"] + [c.name for c in self.cm.categories]
        cat_var = ctk.StringVar(value=cat_names[0])
        min_var = ctk.StringVar()
        max_var = ctk.StringVar()

        fields = [
            ("Ürün Adı (kısmî)", name_var, "Ürün adı girin..."),
            ("Fiyat Min (₺)", min_var, "0.00"),
            ("Fiyat Max (₺)", max_var, "9999.99"),
        ]
        r = 0
        for label, var, placeholder in fields:
            self._make_label(self.details_content, f"{label}:", size=12,
                             color=COLORS["text_secondary"]).grid(row=r, column=0, sticky="w", pady=5, padx=(0, 12))
            self._make_entry(self.details_content, textvariable=var,
                             placeholder=placeholder).grid(row=r, column=1, sticky="ew", pady=5)
            r += 1

        self._make_label(self.details_content, "Kategori:", size=12,
                         color=COLORS["text_secondary"]).grid(row=r, column=0, sticky="w", pady=5, padx=(0, 12))
        self._make_combobox(self.details_content, cat_names, cat_var).grid(row=r, column=1, sticky="ew", pady=5)
        r += 1

        self.details_content.grid_columnconfigure(1, weight=1)

        def do_search():
            name_q = name_var.get().strip() or None
            cat_name = cat_var.get()
            cat_id = None
            if cat_name != "(Hepsi)":
                cat = self.cm.get_category_by_name(cat_name)
                if cat:
                    cat_id = cat._id

            min_p = None
            max_p = None
            try:
                if min_var.get().strip():
                    min_p = float(min_var.get())
                if max_var.get().strip():
                    max_p = float(max_var.get())
            except ValueError:
                self.show_warning("Uyarı", "Fiyat aralığı geçersiz.")
                return

            results = self.pm.search_products(name_q, cat_id, min_p, max_p)
            self._refresh_product_list_silent(filtered=results)

        btn_row = ctk.CTkFrame(self.details_content, fg_color="transparent")
        btn_row.grid(row=r, column=0, columnspan=2, pady=12)
        self._make_button(btn_row, "🔍 Ara", COLORS["btn_search"], COLORS["btn_search_hover"],
                          do_search, height=34).pack(side="left", padx=6)
        self._make_button(btn_row, "Temizle", COLORS["btn_neutral"], COLORS["btn_neutral_hover"],
                          lambda: self.show_all_products(), height=34).pack(side="left", padx=6)

    # ══════════════════════════════════════════════════════════════════════
    # Kategori Yönetimi
    # ══════════════════════════════════════════════════════════════════════

    def manage_categories(self):
        self.clear_details_content()
        self.details_title.configure(text="📂 Kategori Yönetimi")

        # Kategori listesi
        cat_list = ctk.CTkTextbox(
            self.details_content, height=130,
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            border_width=1, border_color=COLORS["border"], corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        cat_list.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        def populate():
            cat_list.configure(state="normal")
            cat_list.delete("1.0", "end")
            for c in self.cm.categories:
                cat_list.insert("end", f"  •  {c.name}\n")
            if not self.cm.categories:
                cat_list.insert("end", "  Henüz kategori yok.")
            cat_list.configure(state="disabled")

        populate()

        # Yeni kategori
        name_var = ctk.StringVar()
        self._make_label(self.details_content, "Kategori Adı:", size=12,
                         color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w", pady=6, padx=(0, 12))
        self._make_entry(self.details_content, textvariable=name_var,
                         placeholder="Yeni kategori adı...").grid(row=1, column=1, sticky="ew", pady=6)

        self.details_content.grid_columnconfigure(1, weight=1)

        btn_row = ctk.CTkFrame(self.details_content, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=6)
        btn_row.grid_columnconfigure((0, 1), weight=1)

        def add_cat():
            name = name_var.get().strip()
            if not name:
                self.show_warning("Uyarı", "Kategori adı boş olamaz.")
                return
            self.cm.create_category(name)
            self.pm.load_products()
            self._refresh_product_list_silent()
            self.manage_categories()

        def delete_cat():
            del_name = name_var.get().strip()
            if not del_name:
                self.show_warning("Uyarı", "Silinecek kategori adını girin.")
                return
            cat = self.cm.get_category_by_name(del_name)
            if not cat:
                self.show_warning("Uyarı", "Kategori bulunamadı.")
                return
            if not self.ask_yes_no("Sil", f"'{del_name}' kategorisi silinsin mi?"):
                return
            self.cm.delete_category(cat)
            self.pm.load_products()
            self._refresh_product_list_silent()
            self.manage_categories()

        self._make_button(btn_row, "➕ Ekle", COLORS["btn_save"], COLORS["btn_save_hover"],
                          add_cat, height=32).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self._make_button(btn_row, "🗑️ Sil", COLORS["btn_delete"], COLORS["btn_delete_hover"],
                          delete_cat, height=32).grid(row=0, column=1, padx=(4, 0), sticky="ew")

    # ══════════════════════════════════════════════════════════════════════
    # Raporlama Ekranı
    # ══════════════════════════════════════════════════════════════════════

    def show_reports(self):
        """Raporlama ekranını gösterir — tüm istatistikleri özetler."""
        self.clear_details_content()
        self.details_title.configure(text="📊 Raporlar")

        try:
            report = self.rm.generate_full_report()
        except Exception as e:
            self.show_error("Hata", f"Rapor oluşturulurken hata: {e}")
            return

        # Scrollable rapor alanı
        report_scroll = ctk.CTkScrollableFrame(
            self.details_content,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"],
        )
        report_scroll.pack(fill="both", expand=True)

        def add_section(parent, title, icon="📌"):
            """Rapor bölüm başlığı ekler."""
            frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_input"], corner_radius=8,
                                 border_width=1, border_color=COLORS["border"])
            frame.pack(fill="x", pady=(0, 8))
            ctk.CTkLabel(
                frame, text=f"{icon}  {title}",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLORS["accent_blue"],
            ).pack(anchor="w", padx=12, pady=(10, 4))
            return frame

        def add_stat_row(parent, label, value, color=None):
            """İstatistik satırı ekler."""
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)
            self._make_label(row, f"{label}:", size=12, color=COLORS["text_secondary"]).pack(side="left")
            self._make_label(row, str(value), size=12, bold=True,
                             color=color or COLORS["text_primary"]).pack(side="right")

        # ── 1. Genel Özet ────────────────────────────────────────────────
        sec1 = add_section(report_scroll, "Genel Özet", "📦")
        add_stat_row(sec1, "Toplam Ürün Sayısı", report["total_products"], COLORS["accent_cyan"])
        add_stat_row(sec1, "Toplam Kategori Sayısı", report["total_categories"], COLORS["accent_purple"])
        add_stat_row(sec1, "Toplam Stok Değeri", f"{report['total_stock_value']:,.2f} ₺", COLORS["accent_green"])
        # Alt padding
        ctk.CTkFrame(sec1, fg_color="transparent", height=6).pack()

        # ── 2. Satış İstatistikleri ──────────────────────────────────────
        sec2 = add_section(report_scroll, "Satış İstatistikleri", "💰")
        add_stat_row(sec2, "Toplam Satış Geliri", f"{report['total_revenue']:,.2f} ₺", COLORS["accent_green"])
        add_stat_row(sec2, "Toplam Satılan Adet", report["total_items_sold"], COLORS["accent_cyan"])
        if report["best_selling_product"]:
            add_stat_row(sec2, "En Çok Satılan Ürün",
                         f"{report['best_selling_product']} ({report['best_selling_qty']} adet)",
                         COLORS["accent_yellow"])
        else:
            add_stat_row(sec2, "En Çok Satılan Ürün", "Henüz satış yok", COLORS["text_muted"])
        ctk.CTkFrame(sec2, fg_color="transparent", height=6).pack()

        # ── 3. Fiyat Analizi ─────────────────────────────────────────────
        sec3 = add_section(report_scroll, "Fiyat Analizi", "💎")
        if report["most_expensive"]:
            add_stat_row(sec3, "En Pahalı Ürün",
                         f"{report['most_expensive'].name} — {report['most_expensive'].price:.2f} ₺",
                         COLORS["accent_orange"])
        if report["cheapest"]:
            add_stat_row(sec3, "En Ucuz Ürün",
                         f"{report['cheapest'].name} — {report['cheapest'].price:.2f} ₺",
                         COLORS["accent_green"])
        ctk.CTkFrame(sec3, fg_color="transparent", height=6).pack()

        # ── 4. Kategori Dağılımı ─────────────────────────────────────────
        sec4 = add_section(report_scroll, "Kategori Dağılımı", "📂")
        if report["most_products_category"]:
            add_stat_row(sec4, "En Çok Ürüne Sahip Kategori",
                         f"{report['most_products_category']} ({report['most_products_category_count']} ürün)",
                         COLORS["accent_purple"])
        if report["sales_by_category"]:
            # Kategori bazlı satış tablosu
            ctk.CTkLabel(
                sec4, text="  Kategorilere Göre Satışlar:",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["text_secondary"],
            ).pack(anchor="w", padx=12, pady=(6, 2))
            for cat_data in report["sales_by_category"]:
                row = ctk.CTkFrame(sec4, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=1)
                self._make_label(row, f"• {cat_data['category']}", size=11,
                                 color=COLORS["text_primary"]).pack(side="left")
                self._make_label(row,
                                 f"{cat_data['total_qty']} adet — {cat_data['total_revenue']:,.2f} ₺",
                                 size=11, color=COLORS["accent_green"]).pack(side="right")
        ctk.CTkFrame(sec4, fg_color="transparent", height=6).pack()

        # ── 5. Kritik Stok Uyarıları ─────────────────────────────────────
        sec5 = add_section(report_scroll, "Kritik Stok Uyarıları", "⚠️")
        critical = report["critical_stock"]
        out_of_stock = report["out_of_stock"]

        add_stat_row(sec5, "Kritik Stoktaki Ürün Sayısı", len(critical), COLORS["accent_red"])
        add_stat_row(sec5, "Stokta Olmayan Ürün Sayısı", len(out_of_stock), COLORS["accent_red"])

        if critical:
            ctk.CTkLabel(
                sec5, text="  Kritik Stoktaki Ürünler:",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS["warning_text"],
            ).pack(anchor="w", padx=12, pady=(6, 2))
            for p in critical[:15]:  # En fazla 15 ürün göster
                row = ctk.CTkFrame(sec5, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=1)
                self._make_label(row, f"⚠️ {p.name}", size=11,
                                 color=COLORS["accent_red"]).pack(side="left")
                self._make_label(row, f"Stok: {p.stock} / Kritik: {p.critical_stock}",
                                 size=11, color=COLORS["warning_text"]).pack(side="right")
            if len(critical) > 15:
                self._make_label(sec5, f"  ... ve {len(critical) - 15} ürün daha",
                                 size=11, color=COLORS["text_muted"]).pack(anchor="w", padx=12)
        ctk.CTkFrame(sec5, fg_color="transparent", height=6).pack()

    # ══════════════════════════════════════════════════════════════════════
    # Veritabanı İşlemleri
    # ══════════════════════════════════════════════════════════════════════

    def reload_data(self):
        """Veritabanından tüm verileri yeniden yükle."""
        self.cm.load_categories()
        self.pm.load_products()
        self._refresh_product_list_silent()
        self.show_info("Yenilendi", "Veriler MongoDB'den yeniden yüklendi.")
    def generate_mock_data(self):
        """8 kategori ve her kategoride 10 ürün olmak üzere mock veri oluşturur."""
        if not self.ask_yes_no("Mock Veri", "Mevcut verilere ek olarak 8 kategori ve 80 ürün oluşturulacak.\nDevam edilsin mi?"):
            return

        mock_categories = {
            "Atıştırmalık": [
                ("Çikolatalı Gofret", 8.50, 120, 15),
                ("Fıstıklı Çikolata", 12.75, 85, 10),
                ("Patates Cipsi", 15.00, 200, 25),
                ("Mısır Cipsi", 10.50, 150, 20),
                ("Bisküvi Paketi", 6.25, 300, 30),
                ("Kuruyemiş Karışık", 45.00, 60, 8),
                ("Çubuk Kraker", 5.75, 180, 20),
                ("Kek Dilimi", 7.00, 90, 12),
                ("Jelibon", 4.50, 250, 30),
                ("Gofret Bar", 9.25, 110, 15),
            ],
            "İçecekler": [
                ("Maden Suyu", 5.00, 500, 50),
                ("Ayran", 8.00, 300, 40),
                ("Portakal Suyu", 18.50, 120, 15),
                ("Elma Suyu", 16.75, 100, 15),
                ("Limonata", 12.00, 180, 20),
                ("Buzlu Çay", 14.50, 200, 25),
                ("Enerji İçeceği", 22.00, 80, 10),
                ("Soda", 4.50, 400, 50),
                ("Gazlı İçecek", 10.00, 350, 40),
                ("Süt 1L", 20.00, 150, 20),
            ],
            "Temizlik": [
                ("Bulaşık Deterjanı", 35.00, 80, 10),
                ("Çamaşır Deterjanı", 85.00, 50, 8),
                ("Cam Temizleyici", 28.00, 60, 10),
                ("Yüzey Temizleyici", 32.00, 70, 10),
                ("Tuvalet Temizleyici", 25.00, 90, 12),
                ("Sünger Seti", 12.00, 150, 20),
                ("Çöp Poşeti", 18.50, 200, 25),
                ("Islak Mendil", 15.00, 180, 20),
                ("El Sabunu", 22.00, 100, 15),
                ("Kağıt Havlu", 30.00, 120, 15),
            ],
            "Kırtasiye": [
                ("Kurşun Kalem", 3.50, 500, 50),
                ("Tükenmez Kalem", 5.00, 400, 40),
                ("Silgi", 2.50, 300, 30),
                ("Cetvel 30cm", 8.00, 150, 20),
                ("Defter A4", 15.00, 200, 25),
                ("Yapıştırıcı", 10.00, 180, 20),
                ("Makas", 12.50, 100, 15),
                ("Boya Kalemi Seti", 25.00, 80, 10),
                ("Dosya Klasör", 18.00, 120, 15),
                ("Kalem Açacağı", 4.00, 250, 30),
            ],
            "Elektronik": [
                ("USB Kablo", 35.00, 100, 12),
                ("Kulaklık", 75.00, 60, 8),
                ("Mouse Pad", 45.00, 80, 10),
                ("Şarj Adaptörü", 120.00, 40, 5),
                ("Powerbank", 250.00, 30, 5),
                ("Bluetooth Hoparlör", 350.00, 25, 3),
                ("USB Bellek 32GB", 85.00, 50, 8),
                ("Ekran Temizleyici", 40.00, 70, 10),
                ("Telefon Kılıfı", 55.00, 90, 12),
                ("LED Masa Lambası", 180.00, 20, 3),
            ],
            "Gıda": [
                ("Ekmek", 10.00, 200, 30),
                ("Yumurta 15'li", 45.00, 100, 15),
                ("Peynir 500g", 65.00, 60, 8),
                ("Zeytin 1kg", 80.00, 50, 8),
                ("Makarna 500g", 12.00, 300, 40),
                ("Pirinç 1kg", 35.00, 150, 20),
                ("Un 2kg", 28.00, 120, 15),
                ("Şeker 1kg", 22.00, 180, 25),
                ("Tuz 750g", 8.00, 250, 30),
                ("Salça 700g", 30.00, 100, 12),
            ],
            "Kişisel Bakım": [
                ("Şampuan", 55.00, 80, 10),
                ("Saç Kremi", 48.00, 60, 8),
                ("Diş Macunu", 28.00, 150, 20),
                ("Diş Fırçası", 18.00, 200, 25),
                ("Deodorant", 42.00, 90, 12),
                ("Tıraş Köpüğü", 35.00, 70, 10),
                ("Tıraş Bıçağı", 65.00, 50, 8),
                ("El Kremi", 30.00, 100, 15),
                ("Dudak Bakım", 22.00, 120, 15),
                ("Pamuk", 15.00, 180, 20),
            ],
            "Ev & Yaşam": [
                ("Mum Seti", 25.00, 60, 8),
                ("Çerçeve", 40.00, 45, 5),
                ("Saksı", 35.00, 50, 8),
                ("Vazo", 55.00, 30, 5),
                ("Masa Örtüsü", 70.00, 40, 5),
                ("Yastık Kılıfı", 45.00, 80, 10),
                ("Havlu Seti", 85.00, 60, 8),
                ("Perde Askısı", 30.00, 50, 8),
                ("Ayakkabılık", 120.00, 20, 3),
                ("Askı Seti", 18.00, 100, 15),
            ],
        }

        created_cats = 0
        created_products = 0

        for cat_name, products in mock_categories.items():
            # Kategoriyi oluştur
            cat = self.cm.create_category(cat_name)
            created_cats += 1

            for prod_name, base_price, base_stock, critical in products:
                # Fiyat ve stokta hafif rastgele varyasyon
                price = round(base_price * random.uniform(0.9, 1.1), 2)
                stock = int(base_stock * random.uniform(0.7, 1.3))
                self.pm.create_product(prod_name, cat._id, price, stock, critical)
                created_products += 1

        # Verileri yeniden yükle
        self.cm.load_categories()
        self.pm.load_products()
        self._refresh_product_list_silent()
        self.show_info("Mock Veri", f"{created_cats} kategori ve {created_products} ürün oluşturuldu!")


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except ModuleNotFoundError as e:
        print(f"Modül bulunamadı: {e}")
        print("Lütfen 'pip install -r requirements.txt' çalıştırın.")
