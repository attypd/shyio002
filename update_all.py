import base64
import json
import requests
import gzip
from Crypto.Cipher import AES

# 1. 配置信息 (从你的抓包和源码中提取)
AES_KEY_IV = "6688000000000000"
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"
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

def decrypt_data(encrypted_str):
    """
    针对你提供的 Base64 数据进行三重处理：AES解密 -> 寻找Gzip头 -> 解压
    """
    try:
        # Base64 解码
        raw_encrypted = base64.b64decode(encrypted_str)
        
        # AES 解密 (CBC 模式)
        key_bytes = AES_KEY_IV.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        decrypted = cipher.decrypt(raw_encrypted)
        
        # 移除填充 (PKCS5Padding)
        pad_val = decrypted[-1]
        if 0 < pad_val <= 16:
            decrypted = decrypted[:-pad_val]

        # 核心修复：寻找 Gzip 压缩包的起始标志 \x1f\x8b
        gzip_start = decrypted.find(b'\x1f\x8b')
        if gzip_start != -1:
            print("[+] 检测到 Gzip 压缩流，正在解压...")
            real_data = gzip.decompress(decrypted[gzip_start:])
            return real_data.decode('utf-8')
        
        # 如果不是压缩包，尝试直接转码并清洗乱码头
        text = decrypted.decode('utf-8', errors='ignore')
        if "http" in text:
            return text[text.find("http"):]
        return text
        
    except Exception as e:
        print(f"[-] 处理失败: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip"
    }
    
    print("[+] 正在请求最新数据...")
    try:
        # 1. 获取最新密文
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        if response.status_code == 200:
            print(f"[*] 成功获取密文 (长度: {len(response.text)})")
            
            # 2. 调用解密逻辑
            result = decrypt_data(response.text)
            
            # 3. 强制保存结果
            if result:
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
                print("[+] 恭喜！live.m3u 已成功生成。")
                if "http" in result:
                    print("[#] 验证：内容包含有效直播链接。")
            else:
                print("[-] 无法从密文中提取有效信息。")
    except Exception as e:
        print(f"[-] 运行异常: {e}")

if __name__ == "__main__":
    main()
