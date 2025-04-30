"""
Цей модуль здійснює цифровий RSA підпис зображення PNG 
і приховує цей підпис у файлі зображення
"""

import hashlib
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives import serialization
from PIL import Image, PngImagePlugin

# Шляхи до файлів
PRIVATE_KEY_PATH = 'keys/private_key.pem'
PUBLIC_KEY_PATH = 'keys/public_key.pem'
ORIGINAL_IMAGE_PATH = 'images/original.png'
SIGNED_IMAGE_PATH = 'images/signed.png'

def generate_keys():
    """
    Ця функція генерує приватний і публічний RSA ключі та зберігає у папку /keys
    під назвою private_key.pem і public_key.pem відповідно
    Input:
        None
    Output:
        None
    """
    # Генерація ключів
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )
    public_key = private_key.public_key()
    # Збереження ключів в папку
    with open(PRIVATE_KEY_PATH, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(PUBLIC_KEY_PATH, 'wb') as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

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

def sign_image(image_path: str, private_key_path: str) -> bytes:
    """
    Ця функція створює цифровий підпис для зображення
    Input:
        image_path (str): шлях до зображення
        private_key_path (str): шлях до приватного ключа
    Output:
        bytes: цифровий підпис для зображення
    """
    image_hash = get_image_pixel_hash(image_path)
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    signature = private_key.sign(
        image_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def embed_signature_png_chunk(input_path, output_path, signature: bytes):
    """
    Ця функція вбудовує цифровий підпис у PNG зображення як метадані, 
    та зберігає як окреме зображення під назвою signed.png в папці /images
    Input:
        input_path (str): шлях до оригінального зображення
        output_path (str): шлях до підписаного зображення
        signature (bytes): підпис, який потрібно вбудувати
    Output:
        None 
    """
    img = Image.open(input_path)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("signature", signature.hex())
    img.save(output_path, "PNG", pnginfo=meta)

def main():
    """
    Основна функція, яка поєднує усі етапи: генерація ключів, підписування зображення 
    та вбудовування підпису в зображення
    Input:
        None
    Output:
        None
    """
    if not os.path.exists('keys'):
        os.makedirs('keys')
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("Генеруємо ключі")
        generate_keys()
    print("Підписуємо зображення")
    signature = sign_image(ORIGINAL_IMAGE_PATH, PRIVATE_KEY_PATH)
    print("Вбудовуємо підпис у зображення")
    embed_signature_png_chunk(ORIGINAL_IMAGE_PATH, SIGNED_IMAGE_PATH, signature)
    print(f"Підписане зображення збережено в {SIGNED_IMAGE_PATH}")

if __name__ == '__main__':
    main()
