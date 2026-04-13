import base64
import json
import requests
import zlib
from Crypto.Cipher import AES

# 16位钥匙：6688补零
AES_KEY = "6688000000000000"

def decrypt_iptv(encrypted_text):
    try:
        key_bytes = AES_KEY.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 1. Base64 解码并解密
        decoded_data = base64.b64decode(encrypted_text.strip())
        decrypted = cipher.decrypt(decoded_data)
        
        # 2. 去除填充
        padding_len = decrypted[-1]
        raw_data = decrypted[:-padding_len]
        
        # 3. 【核心修正】尝试 Gzip/Zlib 解压，如果不行再直接转码
        try:
            # 很多接口为了省流量会压缩内容，0xd8 这种字节通常是压缩流的特征
            return zlib.decompress(raw_data, 16+zlib.MAX_WBITS).decode('utf-8')
        except:
            try:
                return raw_data.decode('utf-8')
            except:
                return raw_data.hex() # 实在不行打印 16 进制看看
    except Exception as e:
        print(f"[-] 解密逻辑崩溃: {e}")
        return None

def main():
    # 固化的登录地址和参数
    url = "http://api.cdnhs.store/iptv/login3.php"
    params = {
        "login": json.dumps({
            "region": "",
            "mac": "d8:45:65:5c:8d:4b",
            "androidid": "d879d7610bc68a18",
            "model": "23078RKD5C",
            "nettype": "",
            "appname": "MYlive"
        })
    }
    
    headers = {"User-Agent": "MSIE", "Content-Type": "application/x-www-form-urlencoded"}

    print(f"[+] 正在获取数据...")
    r = requests.post(url, data=params, headers=headers, timeout=15)
    
    if r.status_code == 200:
        print(f"[*] 密文长度: {len(r.text)}")
        result = decrypt_iptv(r.text)
        
        if result:
            # 如果结果包含 http 说明是我们要的 M3U 列表
            if "http" in result:
                print("[+] 解密并解压成功！")
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                print(f"[!] 内容不包含链接，可能是加密的 JSON: {result[:100]}")
        else:
            print("[-] 解密结果为空")

if __name__ == "__main__":
    main()

