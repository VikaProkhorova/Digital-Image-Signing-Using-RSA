"""
Цей модуль поєднує одразу генерацію підпису на зображенні (main.py) та 
перевірку підписаного зображення (verify.py)
"""

import os
import subprocess

# Створюємо папки для ключів та зображень, якщо їх немає
os.makedirs('keys', exist_ok=True)
os.makedirs('images', exist_ok=True)

# Перевіряємо чи вже є зображення у папці
ORIGINAL_IMAGE_PATH = 'images/original.png'
if not os.path.exists(ORIGINAL_IMAGE_PATH):
    print("Будь ласка, скопіюйте своє зображення у папку images/ під назвою 'original.png'")
    exit()

# Запускаємо генерацію ключів
subprocess.run(['python', 'main.py'], check=True)

# Підписуємо зображення
subprocess.run(['python', 'main.py'], check=True)

# Перевіряємо підпис
subprocess.run(['python', 'verify.py'], check=True)
