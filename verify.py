"""
Цей модуль перевіряє наявність та коректність цифрового підпису зображення
"""

from typing import Optional
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from PIL import Image

# Шляхи до файлів
PUBLIC_KEY_PATH = 'keys/public_key.pem'
SIGNED_IMAGE_PATH = 'images/signed.png'

def get_image_pixel_hash(image_path: str) -> bytes:
    """
    Ця функція обчислює хеш зображення на основі пікселів
    Input:
        image_path (str): шлях до зображення
    Output:
        bytes: хеш зображення у вигляді байтів
    """
    img = Image.open(image_path).convert('RGB')
    pixel_bytes = b''.join(bytes([r, g, b]) for r, g, b in img.getdata())
    return hashlib.sha256(pixel_bytes).digest()

def extract_signature_png_chunk(image_path: str) -> Optional[bytes]:
    """
    Ця функція витягує підпис з PNG зображення
    Input:
        image_path (str): шлях до зображення
    Output:
        Optional[bytes]: підпис у вигляді байтів, якщо він є, або None
    """
    img = Image.open(image_path)
    if "signature" in img.info:
        return bytes.fromhex(img.info["signature"])
    return None

def verify_signature(image_path: str, signature: bytes, public_key_path: str) -> bool:
    """
    Ця функція перевіряє цифровий підпис на зображення
    Input:
        image_path (str): шлях до зображення
        signature (bytes): підпис
        public_key_path (str): шлях до публічного ключа
    Output:
        bool: True, якщо підпис правильний, False — якщо ні.
    """
    image_hash = get_image_pixel_hash(image_path)
    with open(public_key_path, 'rb') as f:
        public_key = serialization.load_pem_public_key(f.read())
    try:
        public_key.verify(
            signature,
            image_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False
    except ValueError:
        return False
    except TypeError:
        return False

def main():
    """
    Основна функція, яка поєднує в собі усі етапи перевірки підпису:
    витягування підпису з зображення та перевірку його правильності
    Input:
        None
    Output:
        None
    """
    print("Витягуємо підпис із зображення")
    signature = extract_signature_png_chunk(SIGNED_IMAGE_PATH)
    if signature is None:
        print("Підпис не знайдено в зображенні")
        return
    print("Перевіряємо підпис")
    is_valid = verify_signature(SIGNED_IMAGE_PATH, signature, PUBLIC_KEY_PATH)
    if is_valid:
        print("Підпис правильний!")
    else:
        print("Підпис не співпадає! Можливо, зображення змінене")

if __name__ == '__main__':
    main()
