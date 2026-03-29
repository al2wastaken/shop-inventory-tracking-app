import os
import platform
from models import Database
from models import ProductManager
from models import CategoryManager

db = Database()
db.loadDatabase()

data = db.data

cm = CategoryManager()
cm.loadCategories(data)

pm = ProductManager()
pm.loadProducts(data, cm)


def clearScreen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        print("\033c", end="")

while True:
    clearScreen()
    print("Mağaza Stok Takip Uygulaması")
    print("[0] Çıkış yap\n[1] Satış İşlemleri\n[2] Arama İşlemleri\n[3] Ürün İşlemleri\n[4] Kategori İşlemleri\n[5] Veritabanı İşlemleri")
    
    choice = input("Yapmak istediğiniz işlemi seçin: ")
    

    
    if choice == "0":
        break
    


    elif choice == "1":
        clearScreen()
        print("Mağaza Stok Takip Uygulaması > Satış İşlemleri")
        print("[0] Geri Dön\n[1] Ürün Satışı Yapma")
        subChoice = input("Yapmak istediğiniz işlemi seçin: ")
        if subChoice == "0":
            continue
        elif subChoice == "1":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Satış İşlemleri > Ürün Satışı Yapma")
            for i, p in enumerate(pm.products):
                print(f"[{i}] {p.name} - Stok: {p.stock}")
            productIndex = int(input("Satışını yapmak istediğiniz ürünü seçin: "))
            selectedProduct = pm.products[productIndex]
            print(f"Seçilen Ürün: {selectedProduct.name}")
            quantity = int(input("Satılan Miktar: "))
            if quantity > selectedProduct.stock:
                print("Yeterli stok yok!")
            else:
                selectedProduct.removeStock(quantity)
                print(f"{quantity} adet {selectedProduct.name} satıldı.")
            input("Devam etmek için Enter'a basın...")
    


    elif choice == "2":
        clearScreen()
        print("Mağaza Stok Takip Uygulaması > Arama İşlemleri")
        print("[0] Geri Dön\n[1] Arama Yap")
        subChoice = input("Yapmak istediğiniz işlemi seçin: ")
        if subChoice == "0":
            continue
        elif subChoice == "1":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Arama İşlemleri > Arama Yap")
            nameQuery = input("Ürün Adı (Enter'a basarak atla): ")
            categoryQuery = input("Kategori Adı (Enter'a basarak atla): ")
            priceRangeQuery = input("Fiyat Aralığı (min-max, Enter'a basarak atla): ")
            minPrice, maxPrice = None, None
            if priceRangeQuery:
                try:
                    minPrice, maxPrice = map(float, priceRangeQuery.split("-"))
                except:
                    print("Geçersiz fiyat aralığı formatı!")
                    input("Devam etmek için Enter'a basın...")
                    continue
            results = []
            for p in pm.products:
                if nameQuery and nameQuery.lower() not in p.name.lower():
                    continue
                if categoryQuery and categoryQuery.lower() not in p.getCategoryName().lower():
                    continue
                if minPrice is not None and p.price < minPrice:
                    continue
                if maxPrice is not None and p.price > maxPrice:
                    continue
                results.append(p)
            clearScreen()
            print("Arama Sonuçları:")
            for p in results:
                print(str(p))
            input("Devam etmek için Enter'a basın...")



    elif choice == "3":
        clearScreen()
        print("Mağaza Stok Takip Uygulaması > Ürün İşlemleri")
        print("[0] Geri Dön\n[1] Ürünleri Görüntüle\n[2] Yeni Ürün Ekle\n[3] Ürün Düzenle\n[4] Ürün Sil")

        subChoice = input("Yapmak istediğiniz işlemi seçin: ")
        if subChoice == "0":
            continue
        if subChoice == "1":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Ürün İşlemleri > Ürünleri Görüntüleme")
            print("Ürünler:")

            for p in pm.products:
                print(str(p))
            input("Devam etmek için Enter'a basın...")

        elif subChoice == "2":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Ürün İşlemleri > Yeni Ürün Ekleme")
            name = input("Ürün Adı: ")
            price = float(input("Ürün Fiyatı: "))
            stock = int(input("Ürün Stoğu: "))
            criticalStock = int(input("Kritik Stok Miktarı: "))
            print("Mevcut Kategoriler:")
            for i, c in enumerate(cm.categories):
                print(f"[{i}] {c.name}")
            categoryIndex = int(input("Kategori Seçin: "))
            pm.createNewProduct(name, categoryIndex, price, stock, criticalStock, cm)

        elif subChoice == "3":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Ürün İşlemleri > Ürün Düzenleme")
            for i, p in enumerate(pm.products):
                print(f"[{i}] {p.name}")
            productIndex = int(input("Düzenlemek istediğiniz ürünü seçin: "))
            selectedProduct = pm.products[productIndex]
            print(f"Seçilen Ürün: {selectedProduct.name}")
            newName = input("Yeni Ürün Adı (Enter'a basarak atla): ")
            if newName:
                selectedProduct.rename(newName)
            newPrice = input("Yeni Ürün Fiyatı (Enter'a basarak atla): ")
            if newPrice:
                selectedProduct.setPrice(float(newPrice))
            newStock = input("Yeni Ürün Stoğu (Enter'a basarak atla): ")
            if newStock:
                selectedProduct.setStock(int(newStock))
            newCriticalStock = input("Yeni Kritik Stok Miktarı (Enter'a basarak atla): ")
            if newCriticalStock:
                selectedProduct.setcriticalStock(int(newCriticalStock))
            print("Mevcut Kategoriler:")
            for i, c in enumerate(cm.categories):
                print(f"[{i}] {c.name}")
            categoryIndex = input("Yeni Kategori Seçin (Enter'a basarak atla): ")
            if categoryIndex:
                selectedProduct.setCategory(int(categoryIndex))

        elif subChoice == "4":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Ürün İşlemleri > Ürün Silme")
            for i, p in enumerate(pm.products):
                print(f"[{i}] {p.name}")
            productIndex = int(input("Silmek istediğiniz ürünü seçin: "))
            del pm.products[productIndex]
    


    elif choice == "4":
        clearScreen()
        print("Mağaza Stok Takip Uygulaması > Kategori İşlemleri")
        print("[0] Geri Dön\n[1] Kategorileri Görüntüle\n[2] Yeni Kategori Ekle\n[3] Kategori Düzenle\n[4] Kategori Sil")

        subChoice = input("Yapmak istediğiniz işlemi seçin: ")
        if subChoice == "0":
            continue
        elif subChoice == "1":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Kategori İşlemleri > Kategorileri Görüntüleme")
            print("Kategoriler:")
            for c in cm.categories:
                print(f"- {c.name}")
            input("Devam etmek için Enter'a basın...")

        elif subChoice == "2":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Kategori İşlemleri > Yeni Kategori Ekleme")
            name = input("Kategori Adı: ")
            cm.createNewCategory(name)

        elif subChoice == "3":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Kategori İşlemleri > Kategori Düzenleme")
            for i, c in enumerate(cm.categories):
                print(f"[{i}] {c.name}")
            categoryIndex = int(input("Düzenlemek istediğiniz kategoriyi seçin: "))
            newName = input("Yeni Kategori Adı: ")
            cm.categories[categoryIndex].rename(newName)

        elif subChoice == "4":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Kategori İşlemleri > Kategori Silme")
            for i, c in enumerate(cm.categories):
                print(f"[{i}] {c.name}")
            categoryIndex = int(input("Silmek istediğiniz kategoriyi seçin: "))
            del cm.categories[categoryIndex]



    elif choice == "5":
        clearScreen()
        print("Mağaza Stok Takip Uygulaması > Veritabanı İşlemleri")
        print("[0] Geri Dön\n[1] Veritabanını Görüntüle\n[2] Veritabanını Kaydet")

        subChoice = input("Yapmak istediğiniz işlemi seçin: ")
        if subChoice == "0":
            continue
        elif subChoice == "1":
            clearScreen()
            print("Mağaza Stok Takip Uygulaması > Veritabanı İşlemleri > Veritabanı Görüntüleme")
            print(db.data)
            input("Devam etmek için Enter'a basın...")

        elif subChoice == "2":
            clearScreen()
            db.saveToDatabase(pm.getJsonObjects(), cm.getJsonObjects())
            print("Mağaza Stok Takip Uygulaması > Veritabanı İşlemleri > Veritabanı Kaydetme")
            print("Veritabanı kaydedildi.")
            input("Devam etmek için Enter'a basın...")
