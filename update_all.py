import base64
import json
import requests
import gzip
import re
from Crypto.Cipher import AES

# 登录地址与请求参数
API_URL = "http://api.cdnhs.store/iptv/login3.php"
KEY_IV = "6688000000000000"  # 严格匹配 Smali 源码

PAYLOAD = {
    "login": json.dumps({
        "region": "",
        "mac": "d8:45:65:5c:8d:4b",
        "androidid": "d879d7610bc68a18",
        "model": "23078RKD5C",
        "nettype": "",
        "appname": "MYlive"
    })
}

def decrypt_core(encoded_text):
    try:
        # 1. Base64 解码
        encrypted_bytes = base64.b64decode(encoded_text)
        
        # 2. AES-CBC 解密
        key_bytes = KEY_IV.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        decrypted = cipher.decrypt(encrypted_bytes)
        
        # 3. 移除 Padding 并处理 Gzip
        pad_len = decrypted[-1]
        if 0 < pad_len <= 16:
            decrypted = decrypted[:-pad_len]
            
        gz_flag = decrypted.find(b'\x1f\x8b')
        if gz_flag != -1:
            decrypted = gzip.decompress(decrypted[gz_flag:])
        
        # 4. 强制转码并清洗
        text = decrypted.decode('utf-8', errors='ignore')
        match = re.search(r'[\u4e00-\u9fa5a-zA-Z#]', text)
        return text[match.start():].strip() if match else text.strip()
    except Exception as e:
        print(f"[-] 解密异常: {e}")
        return None

def main():
    headers = {"User-Agent": "MSIE", "Content-Type": "application/x-www-form-urlencoded"}
    try:
        response = requests.post(API_URL, data=PAYLOAD, headers=headers, timeout=15)
        if response.status_code == 200:
            final_txt = decrypt_core(response.text)
            if final_txt:
                # 确定只输出 live.txt
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(final_txt)
                print("[+] 成功！live.txt 已生成。")
    except Exception as e:
        print(f"[-] 运行报错: {e}")

if __name__ == "__main__":
    main()
