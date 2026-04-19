import os
import re
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# .env dosyasını yükle
load_dotenv()


class Database:
    """MongoDB veritabanı bağlantısı ve işlemleri."""

    def __init__(self):
        self.client = None
        self.db = None
        self.connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("MONGODB_DB_NAME", "shop_inventory")

    def connect(self):
        """MongoDB'ye bağlan."""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=3000)
            # Bağlantıyı test et
            self.client.server_info()
            self.db = self.client[self.db_name]
            return True
        except Exception as e:
            print(f"MongoDB bağlantı hatası: {e}")
            return False

    def close(self):
        """Bağlantıyı kapat."""
        if self.client:
            self.client.close()

    def get_products_collection(self):
        return self.db["products"]

    def get_categories_collection(self):
        return self.db["categories"]

    def get_sales_collection(self):
        """Satış kayıtları koleksiyonunu döndürür."""
        return self.db["sales"]


class Category:
    def __init__(self, name, _id=None):
        self._id = _id
        self.name = name

    def __str__(self):
        return f"Kategori Adı: {self.name}"

    def to_dict(self):
        return {"name": self.name}


class CategoryManager:
    def __init__(self, db: Database):
        self.db = db
        self.categories = []

    def load_categories(self):
        """MongoDB'den kategorileri yükle."""
        self.categories = []
        collection = self.db.get_categories_collection()
        for doc in collection.find():
            cat = Category(name=doc["name"], _id=doc["_id"])
            self.categories.append(cat)

    def create_category(self, name):
        """Yeni kategori oluştur ve MongoDB'ye kaydet."""
        collection = self.db.get_categories_collection()
        result = collection.insert_one({"name": name})
        new_cat = Category(name=name, _id=result.inserted_id)
        self.categories.append(new_cat)
        return new_cat

    def delete_category(self, category):
        """Kategoriyi MongoDB'den sil."""
        collection = self.db.get_categories_collection()
        collection.delete_one({"_id": category._id})
        self.categories.remove(category)

    def rename_category(self, category, new_name):
        """Kategori adını güncelle."""
        collection = self.db.get_categories_collection()
        collection.update_one({"_id": category._id}, {"$set": {"name": new_name}})
        category.name = new_name

    def get_category_by_id(self, _id):
        """ID ile kategori bul."""
        for c in self.categories:
            if c._id == _id:
                return c
        return None

    def get_category_by_name(self, name):
        """İsim ile kategori bul."""
        for c in self.categories:
            if c.name == name:
                return c
        return None


class Product:
    def __init__(self, name, category_id, price, stock, critical_stock, _id=None):
        self._id = _id
        self.name = name
        self.category_id = category_id  # MongoDB ObjectId referansı
        self.price = price
        self.stock = stock
        self.critical_stock = critical_stock

    def __str__(self):
        return (
            f"Ürün Adı: {self.name}\n"
            f"Ürün Fiyatı: {self.price:.2f} ₺\n"
            f"Ürün Stoğu: {self.stock}\n"
            f"Kritik Stok: {self.critical_stock}"
        )

    def to_dict(self):
        return {
            "name": self.name,
            "category_id": self.category_id,
            "price": self.price,
            "stock": self.stock,
            "critical_stock": self.critical_stock,
        }


def validate_product_name(name):
    """Ürün adını regex ile doğrular.
    Kurallar:
      - En az 2 karakter olmalı
      - Sadece harf, rakam, boşluk ve bazı özel karakterler (., -, ', &, /) içerebilir
      - Sadece rakamlardan oluşamaz
    """
    pattern = r'^[a-zA-ZçÇğĞıİöÖşŞüÜ0-9][a-zA-ZçÇğĞıİöÖşŞüÜ0-9\s.\-\'&/]{1,99}$'
    if not re.match(pattern, name):
        return False, "Ürün adı en az 2 karakter olmalı ve geçerli karakterler içermelidir."
    if re.match(r'^[0-9\s]+$', name):
        return False, "Ürün adı sadece rakamlardan oluşamaz."
    return True, ""


class Sale:
    """Satış kaydı sınıfı."""
    def __init__(self, product_id, product_name, category_id, quantity, unit_price, total_price, date=None, _id=None):
        self._id = _id
        self.product_id = product_id
        self.product_name = product_name
        self.category_id = category_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price
        self.date = date or datetime.now()

    def __str__(self):
        return (
            f"Satış: {self.product_name} x{self.quantity} = "
            f"{self.total_price:.2f} ₺ ({self.date.strftime('%d.%m.%Y %H:%M')})"
        )

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "category_id": self.category_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price,
            "date": self.date,
        }


class SaleManager:
    """Satış kayıtlarını yöneten sınıf."""
    def __init__(self, db: Database):
        self.db = db

    def record_sale(self, product, quantity):
        """Satış kaydı oluşturur ve MongoDB'ye kaydeder."""
        collection = self.db.get_sales_collection()
        total = round(product.price * quantity, 2)
        sale = Sale(
            product_id=product._id,
            product_name=product.name,
            category_id=product.category_id,
            quantity=quantity,
            unit_price=product.price,
            total_price=total,
        )
        result = collection.insert_one(sale.to_dict())
        sale._id = result.inserted_id
        return sale

    def get_all_sales(self):
        """Tüm satış kayıtlarını döndürür."""
        collection = self.db.get_sales_collection()
        sales = []
        for doc in collection.find().sort("date", -1):
            sale = Sale(
                product_id=doc["product_id"],
                product_name=doc["product_name"],
                category_id=doc.get("category_id"),
                quantity=doc["quantity"],
                unit_price=doc["unit_price"],
                total_price=doc["total_price"],
                date=doc.get("date"),
                _id=doc["_id"],
            )
            sales.append(sale)
        return sales

    def get_total_revenue(self):
        """Toplam satış gelirini hesaplar."""
        collection = self.db.get_sales_collection()
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total_price"}}}]
        result = list(collection.aggregate(pipeline))
        return result[0]["total"] if result else 0.0

    def get_total_items_sold(self):
        """Toplam satılan ürün adedini hesaplar."""
        collection = self.db.get_sales_collection()
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$quantity"}}}]
        result = list(collection.aggregate(pipeline))
        return result[0]["total"] if result else 0

    def get_best_selling_product(self):
        """En çok satılan ürünü döndürür (isim, toplam adet)."""
        collection = self.db.get_sales_collection()
        pipeline = [
            {"$group": {"_id": "$product_name", "total_qty": {"$sum": "$quantity"}}},
            {"$sort": {"total_qty": -1}},
            {"$limit": 1},
        ]
        result = list(collection.aggregate(pipeline))
        if result:
            return result[0]["_id"], result[0]["total_qty"]
        return None, 0

    def get_sales_by_category(self, categories):
        """Kategorilere göre satış dağılımını döndürür."""
        collection = self.db.get_sales_collection()
        pipeline = [
            {"$group": {
                "_id": "$category_id",
                "total_qty": {"$sum": "$quantity"},
                "total_revenue": {"$sum": "$total_price"},
            }},
            {"$sort": {"total_revenue": -1}},
        ]
        results = list(collection.aggregate(pipeline))
        # Kategori adlarını eşleştir
        cat_map = {c._id: c.name for c in categories}
        enriched = []
        for r in results:
            cat_name = cat_map.get(r["_id"], "Kategorisiz")
            enriched.append({
                "category": cat_name,
                "total_qty": r["total_qty"],
                "total_revenue": round(r["total_revenue"], 2),
            })
        return enriched


class ReportManager:
    """Raporlama işlemlerini yöneten sınıf."""
    def __init__(self, pm, cm, sm):
        self.pm = pm  # ProductManager
        self.cm = cm  # CategoryManager
        self.sm = sm  # SaleManager

    def get_total_product_count(self):
        """Toplam ürün sayısını döndürür."""
        return len(self.pm.products)

    def get_total_category_count(self):
        """Toplam kategori sayısını döndürür."""
        return len(self.cm.categories)

    def get_critical_stock_products(self):
        """Kritik stoktaki ürünleri döndürür."""
        return [p for p in self.pm.products if p.stock <= p.critical_stock]

    def get_most_expensive_product(self):
        """En pahalı ürünü döndürür."""
        if not self.pm.products:
            return None
        return max(self.pm.products, key=lambda p: p.price)

    def get_cheapest_product(self):
        """En ucuz ürünü döndürür."""
        if not self.pm.products:
            return None
        return min(self.pm.products, key=lambda p: p.price)

    def get_total_stock_value(self):
        """Toplam stok değerini (fiyat × stok) hesaplar."""
        return round(sum(p.price * p.stock for p in self.pm.products), 2)

    def get_category_with_most_products(self):
        """En çok ürüne sahip kategoriyi döndürür."""
        if not self.pm.products:
            return None, 0
        cat_counts = {}
        for p in self.pm.products:
            cat_name = self.pm.get_category_name(p)
            cat_counts[cat_name] = cat_counts.get(cat_name, 0) + 1
        if not cat_counts:
            return None, 0
        best = max(cat_counts, key=cat_counts.get)
        return best, cat_counts[best]

    def get_out_of_stock_products(self):
        """Stokta hiç kalmayan ürünleri döndürür."""
        return [p for p in self.pm.products if p.stock == 0]

    def generate_full_report(self):
        """Tüm rapor verilerini bir sözlük olarak döndürür."""
        best_product, best_qty = self.sm.get_best_selling_product()
        most_cat, most_cat_count = self.get_category_with_most_products()

        return {
            "total_products": self.get_total_product_count(),
            "total_categories": self.get_total_category_count(),
            "critical_stock": self.get_critical_stock_products(),
            "out_of_stock": self.get_out_of_stock_products(),
            "most_expensive": self.get_most_expensive_product(),
            "cheapest": self.get_cheapest_product(),
            "total_stock_value": self.get_total_stock_value(),
            "best_selling_product": best_product,
            "best_selling_qty": best_qty,
            "total_revenue": self.sm.get_total_revenue(),
            "total_items_sold": self.sm.get_total_items_sold(),
            "most_products_category": most_cat,
            "most_products_category_count": most_cat_count,
            "sales_by_category": self.sm.get_sales_by_category(self.cm.categories),
        }


class ProductManager:
    def __init__(self, db: Database, cm: CategoryManager):
        self.db = db
        self.cm = cm
        self.products = []

    def load_products(self):
        """MongoDB'den ürünleri yükle."""
        self.products = []
        collection = self.db.get_products_collection()
        for doc in collection.find():
            product = Product(
                name=doc["name"],
                category_id=doc.get("category_id"),
                price=doc["price"],
                stock=doc["stock"],
                critical_stock=doc.get("critical_stock", 0),
                _id=doc["_id"],
            )
            self.products.append(product)

    def create_product(self, name, category_id, price, stock, critical_stock):
        """Yeni ürün oluştur ve MongoDB'ye kaydet.
        Ürün adı regex ile doğrulanır.
        """
        # Regex ile ürün adı doğrulama
        is_valid, error_msg = validate_product_name(name)
        if not is_valid:
            raise ValueError(error_msg)

        collection = self.db.get_products_collection()
        doc = {
            "name": name,
            "category_id": category_id,
            "price": price,
            "stock": stock,
            "critical_stock": critical_stock,
        }
        result = collection.insert_one(doc)
        new_product = Product(
            name=name,
            category_id=category_id,
            price=price,
            stock=stock,
            critical_stock=critical_stock,
            _id=result.inserted_id,
        )
        self.products.append(new_product)
        return new_product

    def update_product(self, product):
        """Ürünü MongoDB'de güncelle."""
        collection = self.db.get_products_collection()
        collection.update_one(
            {"_id": product._id},
            {"$set": product.to_dict()},
        )

    def delete_product(self, product):
        """Ürünü MongoDB'den sil."""
        collection = self.db.get_products_collection()
        collection.delete_one({"_id": product._id})
        self.products.remove(product)

    def sell_product(self, product, quantity):
        """Ürün satışı yap ve stok güncelle."""
        if quantity <= 0:
            raise ValueError("Satış miktarı 0'dan büyük olmalıdır!")
        if quantity > product.stock:
            raise ValueError(f"Yeterli stok yok! Mevcut stok: {product.stock}")
        product.stock -= quantity
        self.update_product(product)

    def update_stock(self, product, new_stock):
        """Stok miktarını güncelle."""
        product.stock = new_stock
        self.update_product(product)

    def search_products(self, name_query=None, category_id=None, min_price=None, max_price=None):
        """Ürün arama — filtreleme MongoDB sorgusu ile yapılır."""
        collection = self.db.get_products_collection()
        query = {}

        if name_query:
            query["name"] = {"$regex": name_query, "$options": "i"}
        if category_id is not None:
            query["category_id"] = category_id
        if min_price is not None or max_price is not None:
            price_filter = {}
            if min_price is not None:
                price_filter["$gte"] = min_price
            if max_price is not None:
                price_filter["$lte"] = max_price
            query["price"] = price_filter

        results = []
        for doc in collection.find(query):
            product = Product(
                name=doc["name"],
                category_id=doc.get("category_id"),
                price=doc["price"],
                stock=doc["stock"],
                critical_stock=doc.get("critical_stock", 0),
                _id=doc["_id"],
            )
            results.append(product)
        return results

    def get_category_name(self, product):
        """Ürünün kategori adını döndür."""
        cat = self.cm.get_category_by_id(product.category_id)
        return cat.name if cat else "Kategorisiz"