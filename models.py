from pymongo import MongoClient
from bson import ObjectId


class Database:
    """MongoDB veritabanı bağlantısı ve işlemleri."""

    def __init__(self, connection_string="mongodb://localhost:27017", db_name="shop_inventory"):
        self.client = None
        self.db = None
        self.connection_string = connection_string
        self.db_name = db_name

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
        """Yeni ürün oluştur ve MongoDB'ye kaydet."""
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
        if quantity > product.stock:
            raise ValueError("Yeterli stok yok!")
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