import base64
from Crypto.Cipher import AES

# 这里的 KEYS 列表已经包含你刚找出的 16 位钥匙
KEYS = [
    "6688000000000000",  # 补全后的 6688 密钥
    "6688cool_key_668",
    "1234567890123456"
]

def decrypt_data(data):
    """
    万无一失的 AES 解密函数
    """
    for key in KEYS:
        try:
            # 这里的逻辑对应你 Smali 里的 AES/CBC/PKCS5Padding
            # 密钥和偏移量 (IV) 在这个 APP 里通常是同一个字符串
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
            
            # Base64 解码后进行 AES 解密
            decrypted = cipher.decrypt(base64.b64decode(data))
            
            # 去除 PKCS5 填充字符
            padding_len = decrypted[-1]
            result = decrypted[:-padding_len].decode('utf-8')
            
            # 只要解密出来的结果包含 "http"，说明这把钥匙对了
            if "http" in result:
                print(f"[+] 成功解密！使用的钥匙是: {key}")
                return result
        except Exception:
            continue
            
    print("[!] 所有的钥匙都试过了，解密依然失败。")
    return None
