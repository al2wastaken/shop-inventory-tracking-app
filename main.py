import os
import platform
from models import Database

db = Database()
print(db.getDatabaseObject())

def clearScreen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

while True:
    print("Hoş geldiniz")
    input("Değer gir: ")
    clearScreen()
