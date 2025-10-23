"""
加密工具 - 用于加密敏感数据如API密钥
"""
from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


def get_cipher():
    """获取加密器"""
    # 使用JWT密钥派生加密密钥
    key = hashlib.sha256(settings.JWT_SECRET_KEY.encode()).digest()
    key_base64 = base64.urlsafe_b64encode(key)
    return Fernet(key_base64)


def encrypt_api_key(api_key: str) -> str:
    """加密API密钥"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """解密API密钥"""
    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted_key.encode())
    return decrypted.decode()
