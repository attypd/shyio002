import base64
import json
import requests
import re
from Crypto.Cipher import AES

# 1. 钥匙：固化的 16 位补零 Key
AES_KEY = "6688000000000000"

# 2. 登录地址：已直接写死
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 3. 登录参数：从你的抓包数据完整复刻
LOGIN_DATA = {
    "login": json.dumps({
        "region": "",
        "mac": "d8:45:65:5c:8d:4b",
        "androidid": "d879d7610bc68a18",
        "model": "23078RKD5C",
        "nettype": "",
        "appname": "MYlive"
    })
}

def decrypt_iptv(data):
    """
    针对 1000069029.jpg 报错优化的解密逻辑：强力清洗乱码
    """
    try:
        data = data.strip()
        key_bytes = AES_KEY.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 自动判断 Hex 或 Base64
        raw_data = bytes.fromhex(data) if all(c in "0123456789abcdefABCDEF" for c in data[:10]) else base64.b64decode(data)
        
        # AES 解密
        decrypted = cipher.decrypt(raw_data)
        
        # 去除 PKCS5 填充
        padding_len = decrypted[-1]
        if 0 < padding_len <= 16:
            decrypted = decrypted[:-padding_len]
        
        # 强制转换为字符串并清洗掉开头的乱码字符
        result = decrypted.decode('utf-8', errors='ignore')
        
        # 关键修复：从解密内容中提取第一个 http 开始的所有内容，扔掉前面的乱码头
        if "http" in result:
            result = result[result.find("http"):]
            
        return result
    except Exception as e:
        print(f"[-] 解密内部出错: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "api.cdnhs.store"
    }
    
    print(f"[+] 正在连接接口: {LOGIN_URL}")
    try:
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text
            print(f"[*] 收到数据长度: {len(content)}")
            
            result = decrypt_iptv(content)
            
            # 只要有数据，就强制生成文件，防止 Deploy 步骤报错
            if result:
                print("[+] 数据解析完成，正在写入文件...")
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
                print("[+] live.m3u 已强制生成。")
            else:
                print("[!] 解密完全失败，无法写入文件。")
        else:
            print(f"[-] 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[-] 脚本运行异常: {e}")

if __name__ == "__main__":
    main()
