import os
import platform
from models import Database, ProductManager, CategoryManager


def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        print("\033c", end="")


def main():
    db = Database()
    if not db.connect():
        print("❌ MongoDB bağlantısı kurulamadı!")
        print("Lütfen MongoDB'nin çalıştığından emin olun.")
        print("Varsayılan bağlantı: mongodb://localhost:27017")
        return

    print("✅ MongoDB'ye bağlanıldı.")

    cm = CategoryManager(db)
    cm.load_categories()

    pm = ProductManager(db, cm)
    pm.load_products()

    while True:
        clear_screen()
        print("═" * 50)
        print("  🛒  Mağaza Stok Takip Uygulaması (MongoDB)")
        print("═" * 50)
        print("[0] Çıkış yap")
        print("[1] Satış İşlemleri")
        print("[2] Arama İşlemleri")
        print("[3] Ürün İşlemleri")
        print("[4] Kategori İşlemleri")
        print("[5] Veritabanı İşlemleri")
        print("─" * 50)

        choice = input("Yapmak istediğiniz işlemi seçin: ")

        if choice == "0":
            db.close()
            print("Hoşça kalın!")
            break

        elif choice == "1":
            clear_screen()
            print("🛒 Satış İşlemleri")
            print("[0] Geri Dön\n[1] Ürün Satışı Yapma")
            sub = input("Seçin: ")
            if sub == "0":
                continue
            elif sub == "1":
                clear_screen()
                print("Ürün Satışı")
                for i, p in enumerate(pm.products):
                    print(f"  [{i}] {p.name} — Stok: {p.stock}")
                try:
                    idx = int(input("Ürün seçin: "))
                    product = pm.products[idx]
                    qty = int(input(f"Satılacak miktar (mevcut: {product.stock}): "))
                    pm.sell_product(product, qty)
                    print(f"✅ {qty} adet {product.name} satıldı.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

        elif choice == "2":
            clear_screen()
            print("🔍 Arama İşlemleri")
            name_q = input("Ürün adı (Enter ile atla): ").strip() or None

            cat_q = input("Kategori adı (Enter ile atla): ").strip()
            cat_id = None
            if cat_q:
                cat = cm.get_category_by_name(cat_q)
                if cat:
                    cat_id = cat._id

            price_range = input("Fiyat aralığı (min-max, Enter ile atla): ").strip()
            min_p, max_p = None, None
            if price_range:
                try:
                    parts = price_range.split("-")
                    min_p = float(parts[0])
                    max_p = float(parts[1])
                except (ValueError, IndexError):
                    print("❌ Geçersiz fiyat aralığı!")
                    input("Devam etmek için Enter'a basın...")
                    continue

            results = pm.search_products(name_q, cat_id, min_p, max_p)
            clear_screen()
            print(f"🔍 Arama Sonuçları ({len(results)} ürün):")
            print("─" * 40)
            for p in results:
                cat_name = pm.get_category_name(p)
                print(f"  {p.name} | {cat_name} | {p.price:.2f} ₺ | Stok: {p.stock}")
            if not results:
                print("  Sonuç bulunamadı.")
            input("\nDevam etmek için Enter'a basın...")

        elif choice == "3":
            clear_screen()
            print("📦 Ürün İşlemleri")
            print("[0] Geri Dön\n[1] Ürünleri Görüntüle\n[2] Yeni Ürün Ekle\n[3] Ürün Düzenle\n[4] Ürün Sil")
            sub = input("Seçin: ")

            if sub == "0":
                continue

            elif sub == "1":
                clear_screen()
                print("📦 Tüm Ürünler:")
                print("─" * 40)
                for p in pm.products:
                    cat_name = pm.get_category_name(p)
                    stock_warn = " ⚠️" if p.stock <= p.critical_stock else ""
                    print(f"  {p.name} | {cat_name} | {p.price:.2f} ₺ | Stok: {p.stock}{stock_warn}")
                input("\nDevam etmek için Enter'a basın...")

            elif sub == "2":
                clear_screen()
                print("➕ Yeni Ürün Ekle")
                try:
                    name = input("Ürün adı: ")
                    price = float(input("Fiyat: "))
                    stock = int(input("Stok: "))
                    critical = int(input("Kritik stok: "))
                    print("\nKategoriler:")
                    for i, c in enumerate(cm.categories):
                        print(f"  [{i}] {c.name}")
                    cat_idx = int(input("Kategori seçin: "))
                    cat_id = cm.categories[cat_idx]._id
                    pm.create_product(name, cat_id, price, stock, critical)
                    pm.load_products()
                    print(f"✅ '{name}' eklendi.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

            elif sub == "3":
                clear_screen()
                print("✏️ Ürün Düzenle")
                for i, p in enumerate(pm.products):
                    print(f"  [{i}] {p.name}")
                try:
                    idx = int(input("Düzenlenecek ürün: "))
                    product = pm.products[idx]
                    print(f"Seçilen: {product.name}")
                    new_name = input("Yeni ad (Enter ile atla): ").strip()
                    if new_name:
                        product.name = new_name
                    new_price = input("Yeni fiyat (Enter ile atla): ").strip()
                    if new_price:
                        product.price = float(new_price)
                    new_stock = input("Yeni stok (Enter ile atla): ").strip()
                    if new_stock:
                        product.stock = int(new_stock)
                    new_critical = input("Yeni kritik stok (Enter ile atla): ").strip()
                    if new_critical:
                        product.critical_stock = int(new_critical)
                    print("\nKategoriler:")
                    for i, c in enumerate(cm.categories):
                        print(f"  [{i}] {c.name}")
                    new_cat = input("Yeni kategori (Enter ile atla): ").strip()
                    if new_cat:
                        product.category_id = cm.categories[int(new_cat)]._id
                    pm.update_product(product)
                    pm.load_products()
                    print("✅ Güncellendi.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

            elif sub == "4":
                clear_screen()
                print("🗑️ Ürün Sil")
                for i, p in enumerate(pm.products):
                    print(f"  [{i}] {p.name}")
                try:
                    idx = int(input("Silinecek ürün: "))
                    product = pm.products[idx]
                    confirm = input(f"'{product.name}' silinsin mi? (e/h): ")
                    if confirm.lower() == "e":
                        pm.delete_product(product)
                        pm.load_products()
                        print("✅ Silindi.")
                    else:
                        print("İptal edildi.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

        elif choice == "4":
            clear_screen()
            print("📂 Kategori İşlemleri")
            print("[0] Geri Dön\n[1] Kategorileri Görüntüle\n[2] Yeni Kategori Ekle\n[3] Kategori Düzenle\n[4] Kategori Sil")
            sub = input("Seçin: ")

            if sub == "0":
                continue

            elif sub == "1":
                clear_screen()
                print("📂 Kategoriler:")
                for c in cm.categories:
                    print(f"  •  {c.name}")
                input("\nDevam etmek için Enter'a basın...")

            elif sub == "2":
                name = input("Yeni kategori adı: ").strip()
                if name:
                    cm.create_category(name)
                    print(f"✅ '{name}' kategorisi eklendi.")
                input("Devam etmek için Enter'a basın...")

            elif sub == "3":
                for i, c in enumerate(cm.categories):
                    print(f"  [{i}] {c.name}")
                try:
                    idx = int(input("Düzenlenecek kategori: "))
                    new_name = input("Yeni ad: ").strip()
                    if new_name:
                        cm.rename_category(cm.categories[idx], new_name)
                        print("✅ Güncellendi.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

            elif sub == "4":
                for i, c in enumerate(cm.categories):
                    print(f"  [{i}] {c.name}")
                try:
                    idx = int(input("Silinecek kategori: "))
                    cat = cm.categories[idx]
                    confirm = input(f"'{cat.name}' silinsin mi? (e/h): ")
                    if confirm.lower() == "e":
                        cm.delete_category(cat)
                        print("✅ Silindi.")
                except (ValueError, IndexError) as e:
                    print(f"❌ Hata: {e}")
                input("Devam etmek için Enter'a basın...")

        elif choice == "5":
            clear_screen()
            print("💾 Veritabanı İşlemleri")
            print(f"  Ürün sayısı: {len(pm.products)}")
            print(f"  Kategori sayısı: {len(cm.categories)}")
            print("\n  ℹ️  MongoDB kullanıldığından tüm değişiklikler anında kaydedilir.")
            input("\nDevam etmek için Enter'a basın...")


if __name__ == "__main__":
    main()
