import json

class Database:
    def __init__(self):
        self.data = {}

    def getDatabaseObject(self):
        data = {}
        with open("data.json", "r") as f:
            data = json.load(f)
        return data

class Category:
    def __init__(self, name):
        self.name = name

class CategoryManager:
    def __init__(self, categories):
        self.categories = categories

class Product:
    def __init__(self, name, category, price, stock, maxStock, criticalStock):
        self.name = name
        self.category = category
        self.price = price
        self.stock = stock
        self.maxStock = maxStock
        self.criticalStock = criticalStock
        saveToDatabase()

    def saveToDatabase(self):
        pass

    def rename(self, newName):
        saveToDatabase()
        pass

    def setCategory(self, category):
        pass

    def setPrice(self, newPrice):
        saveToDatabase()
        pass

    def increasePrice(self, percentage):
        saveToDatabase()
        pass

    def addStock(self, amount):
        saveToDatabase()
        pass

    def removeStock(self, amount):
        saveToDatabase()
        pass

    def setStock(self, amount):
        saveToDatabase()
        pass

    def setMaxStock(self, amount):
        saveToDatabase()
        pass

    def setcriticalStock(self, amount):
        saveToDatabase()
        pass

class ProductManager:
    def __init__ (self):
        self.products = []

    def loadProducts(self):
        # veri tabanından ürünler teker teker yüklenecek ve self.products olarak tanımlanacak
        pass

    def addProduct(self, name, price, stock, maxStock, criticalStock):
        pass