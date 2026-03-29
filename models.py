import json

class Database:
    def __init__(self):
        self.data = {}

    def loadDatabase(self):
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {"products": [], "categories": []}
    
    def saveToDatabase(self, products, categories):
        """Writes the in-memory data back to the JSON file."""
        try:
            with open("data.json", "w", encoding="utf-8") as file:
                # ensure_ascii=False prevents Turkish character corruption
                json.dump({"products": products, "categories": categories}, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Save Error: {e}")





class Category:
    def __init__(self, index, name):
        self.index = index
        self.name = name

    def __str__(self):
        return f"Kategori Adı: {self.name}"
    
    def setName(self, newName, data):
        data["categories"][self.index] = newName

    def getJsonObject(self):
        return {"name": self.name}



class CategoryManager:
    def __init__(self):
        self.categories = []

    def loadCategories(self, data):
        categoriesInDatabase = data["categories"]
        for c in categoriesInDatabase:
            self.categories.append(Category(categoriesInDatabase.index(c), c["name"]))
    
    def createNewCategory(self, name):
        newCategory = Category(len(self.categories), name)
        self.categories.append(newCategory)

    def getJsonObjects(self):
        jsonObjects = []
        for c in self.categories:
            jsonObjects.append(c.getJsonObject())
        return jsonObjects





class Product:
    def __init__(self, name, category, price, stock, criticalStock, categoryManager):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.criticalStock = criticalStock
        self.categoryManager = categoryManager

    def __str__(self):
        return f"""
Ürün Adı: {self.name}
Kategori Adı: {self.getCategoryName()}
Ürün Fiyatı: {self.price}
Ürün Stoğu: {self.stock}
Kritik Stok Miktarı: {self.criticalStock}
"""

    def rename(self, newName):
        self.name = newName

    def setCategory(self, category):
        self.category = category

    def getCategoryName(self):
        cm = self.categoryManager
        return cm.categories[self.category].name

    def setPrice(self, newPrice):
        self.price = newPrice

    def increasePrice(self, percentage):
        self.price *= (1 + percentage / 100)

    def decreasePrice(self, percentage):
        self.price *= (1 - percentage / 100)

    def addStock(self, amount):
        self.stock += amount

    def removeStock(self, amount):
        self.stock -= amount

    def setStock(self, amount):
        self.stock = amount

    def setcriticalStock(self, amount):
        self.criticalStock = amount

    def getJsonObject(self):
        return {
            "name": self.name,
            "category": self.category,
            "price": self.price,
            "stock": self.stock,
            "criticalStock": self.criticalStock
        }



class ProductManager:
    def __init__ (self):
        self.products = []

    def loadProducts(self, data, categoryManager):
        productsInDatabase = data["products"]

        for p in productsInDatabase:
            self.products.append(Product(p["name"], p["category"], p["price"], p["stock"], p["criticalStock"], categoryManager))

    def createNewProduct(self, name, category, price, stock, criticalStock, categoryManager):
        newProduct = Product(name, category, price, stock, criticalStock, categoryManager)
        self.products.append(newProduct)
    
    def sellProduct(self, productIndex, amount):
        self.products[productIndex].removeStock(amount)
        

    def getProductsByCategory(self, categoryIndex):
        filteredProducts = []
        for p in self.products:
            if p.category == categoryIndex:
                filteredProducts.append(p)
        return filteredProducts

    def getJsonObjects(self):
        jsonObjects = []
        for p in self.products:
            jsonObjects.append(p.getJsonObject())
        return jsonObjects