import customtkinter as ctk
from models import Database, ProductManager, CategoryManager

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
        self.title("🛒 Mağaza Stok Takip — MongoDB")
        self.geometry("1100x680")
        self.minsize(1100, 680)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_primary"])

        # ── MongoDB Bağlantısı ───────────────────────────────────────────
        self.db = Database()
        if not self.db.connect():
            self._show_connection_error()
            return

        self.cm = CategoryManager(self.db)
        self.cm.load_categories()

        self.pm = ProductManager(self.db, self.cm)
        self.pm.load_products()

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

        # Bağlantı durumu göstergesi
        self.status_label = ctk.CTkLabel(
            self.header,
            text="● MongoDB Bağlı",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["accent_green"],
        )
        self.status_label.pack(side="right", padx=20)

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

        # Ürün listesi
        self.product_listbox = ctk.CTkTextbox(
            self.left_frame,
            width=380, height=400,
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8,
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["bg_hover"],
        )
        self.product_listbox.pack(fill="both", expand=True, padx=14, pady=6)
        self.product_listbox.bind("<ButtonRelease-1>", self.on_product_click)

        # Buton çubuğu
        self.btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=14, pady=(6, 8))
        self.btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._make_button(self.btn_frame, "➕ Ekle", COLORS["btn_save"], COLORS["btn_save_hover"],
                          self.add_product).grid(row=0, column=0, padx=3, sticky="ew")
        self._make_button(self.btn_frame, "✏️ Düzenle", COLORS["btn_edit"], COLORS["btn_edit_hover"],
                          self.edit_product).grid(row=0, column=1, padx=3, sticky="ew")
        self._make_button(self.btn_frame, "🗑️ Sil", COLORS["btn_delete"], COLORS["btn_delete_hover"],
                          self.delete_product).grid(row=0, column=2, padx=3, sticky="ew")

        self._make_button(self.left_frame, "💸 Satış Yap", COLORS["btn_sell"], COLORS["btn_sell_hover"],
                          self.sell_product, height=36).pack(fill="x", padx=14, pady=(2, 14))

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
            ("🗒️ Tümü", COLORS["btn_neutral"], COLORS["btn_neutral_hover"], self.show_all_products),
            ("💾 Kaydet", COLORS["btn_save"], COLORS["btn_save_hover"], self.save_all),
            ("🔄 Yenile", COLORS["btn_neutral"], COLORS["btn_neutral_hover"], self.reload_data),
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
        self.product_listbox.configure(state="normal")
        self.product_listbox.delete("1.0", "end")
        source = filtered if filtered is not None else self.pm.products

        for p in source:
            cat_name = self.pm.get_category_name(p)
            if p.stock <= p.critical_stock:
                label = f"⚠️  {p.name}  │  {cat_name}  │  Stok: {p.stock}  │  {p.price:.2f} ₺\n"
            else:
                label = f"    {p.name}  │  {cat_name}  │  Stok: {p.stock}  │  {p.price:.2f} ₺\n"
            self.product_listbox.insert("end", label)

        self.product_listbox.configure(state="disabled")
        self.product_count_label.configure(text=f"{len(source)} ürün")
        self.clear_details_content()
        self.last_selected_index = None

    def show_all_products(self):
        self.pm.load_products()
        self.refresh_product_list()

    # ══════════════════════════════════════════════════════════════════════
    # Seçim & Detaylar
    # ══════════════════════════════════════════════════════════════════════

    def on_product_click(self, event=None):
        try:
            index = self.product_listbox.index(f"@{event.x},{event.y}")
            line = int(str(index).split(".")[0]) - 1
        except Exception:
            return
        if line < 0 or line >= len(self.pm.products):
            return
        self.last_selected_index = line
        product = self.pm.products[line]
        self.show_product_details(product)

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
            self.refresh_product_list(filtered=results)

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
            populate()
            name_var.set("")
            self.pm.load_products()
            self.refresh_product_list()

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
            populate()
            name_var.set("")
            self.pm.load_products()
            self.refresh_product_list()

        self._make_button(btn_row, "➕ Ekle", COLORS["btn_save"], COLORS["btn_save_hover"],
                          add_cat, height=32).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        self._make_button(btn_row, "🗑️ Sil", COLORS["btn_delete"], COLORS["btn_delete_hover"],
                          delete_cat, height=32).grid(row=0, column=1, padx=(4, 0), sticky="ew")

    # ══════════════════════════════════════════════════════════════════════
    # Veritabanı İşlemleri
    # ══════════════════════════════════════════════════════════════════════

    def save_all(self):
        """Tüm değişiklikler zaten anında MongoDB'ye kaydedilir."""
        self.show_info("Bilgi", "Tüm değişiklikler MongoDB'ye otomatik olarak kaydedilmektedir.")

    def reload_data(self):
        """Veritabanından tüm verileri yeniden yükle."""
        self.cm.load_categories()
        self.pm.load_products()
        self.refresh_product_list()
        self.show_info("Yenilendi", "Veriler MongoDB'den yeniden yüklendi.")


if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except ModuleNotFoundError as e:
        print(f"Modül bulunamadı: {e}")
        print("Lütfen 'pip install -r requirements.txt' çalıştırın.")
