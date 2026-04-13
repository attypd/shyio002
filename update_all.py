import base64
import json
import requests
import gzip
import re
from Crypto.Cipher import AES

# 核心接口
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"
DATA_URL = "http://api.cdnhs.store/iptv/data.php"
AES_KEY_IV = "6688000000000000"

# 授权设备指纹
DEVICE_INFO = {
    "login": json.dumps({
        "region": "",
        "mac": "c1:bd:92:03:55:bc",
        "androidid": "5cb5bd4ece1d700c",
        "model": "TAL-AN000",
        "nettype": "WIFI",
        "appname": "MYlive"
    })
}

def decrypt_core(encoded_text):
    """万无一失解密流：处理 Base64 -> AES -> 强制 Gzip 穿透"""
    try:
        raw_cipher = base64.b64decode(encoded_text)
        key = AES_KEY_IV.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, key)
        decrypted = cipher.decrypt(raw_cipher)
        
        # 暴力搜索 Gzip 头，解决 1000069040.jpg 乱码问题
        gz_header = b'\x1f\x8b'
        for i in range(min(len(decrypted), 128)):
            if decrypted[i:i+2] == gz_header:
                try:
                    data = gzip.decompress(decrypted[i:])
                    text = data.decode('utf-8', errors='ignore')
                    if '#' in text or ',' in text: # 验证 TXT 特征
                        return text.strip()
                except: continue
        return None
    except: return None

def main():
    # 使用 Session 保持登录状态
    session = requests.Session()
    session.headers.update({
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip"
    })

    print("[1/2] 正在请求登录接口进行设备授权...")
    try:
        login_resp = session.post(LOGIN_URL, data=DEVICE_INFO, timeout=15)
        print(f"[*] 登录响应码: {login_resp.status_code}")
        
        print("[2/2] 正在请求数据接口提取全套源...")
        # 即使 login 没返回内容，只要 session 建立了，就立刻请求 data.php
        data_resp = session.post(DATA_URL, data=DEVICE_INFO, timeout=20)
        
        if data_resp.status_code == 200 and len(data_resp.text) > 100:
            print(f"[*] 抓取到密文，长度: {len(data_resp.text)}，开始解密...")
            final_txt = decrypt_core(data_resp.text)
            
            if final_txt:
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(final_txt)
                print("[+] 成功！标准的 TXT 格式全套源已保存到 live.txt。")
                return
        
        print("[-] 提取失败：data.php 未返回有效加密数据。")
    except Exception as e:
        print(f"[-] 运行报错: {e}")

if __name__ == "__main__":
    main()
