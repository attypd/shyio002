import base64
import json
import requests
from Crypto.Cipher import AES

# 1. 钥匙：由 "6688" 补零至 16 位，完全匹配你的 Smali 逻辑
AES_KEY = "6688000000000000"

# 2. 登录地址：已直接写死，无需你再修改
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 3. 登录参数：从你的抓包数据中完整复刻
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
    自适应解密：自动识别 Hex（十六进制）或 Base64 格式
    """
    try:
        data = data.strip()
        key_bytes = AES_KEY.encode('utf-8')
        # APP 使用 AES/CBC/PKCS5Padding，且 IV 与 Key 相同
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 自动判断是十六进制 Hex 还是 Base64
        if all(c in "0123456789abcdefABCDEF" for c in data[:10]):
            raw_data = bytes.fromhex(data)
        else:
            raw_data = base64.b64decode(data)
            
        decrypted = cipher.decrypt(raw_data)
        # 去除 PKCS5 填充
        padding_len = decrypted[-1]
        return decrypted[:-padding_len].decode('utf-8')
    except Exception as e:
        print(f"[-] 解密失败: {e}")
        return None

def main():
    # 模拟手机端请求头
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "api.cdnhs.store"
    }
    
    print(f"[+] 正在请求登录接口...")
    try:
        # 发送 POST 请求获取密文
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text
            print(f"[*] 收到密文，长度: {len(content)}")
            
            result = decrypt_iptv(content)
            # 只要解密结果包含 http，就说明成功了
            if result and "http" in result:
                print("[+] 解密成功！正在保存 live.m3u...")
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                # 兜底逻辑：如果返回的就是明文带 http
                if "http" in content:
                    with open("live.m3u", "w", encoding="utf-8") as f:
                        f.write(content)
                    print("[+] 识别为明文数据，已直接保存。")
                else:
                    print("[!] 数据异常，解密后未发现链接。")
        else:
            print(f"[-] 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[-] 运行报错: {e}")

if __name__ == "__main__":
    main()
