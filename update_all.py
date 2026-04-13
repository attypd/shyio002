import base64
import json
import requests
import gzip
from Crypto.Cipher import AES

# 1. 钥匙：固定的 16 位补零 Key
AES_KEY = "6688000000000000"

# 2. 接口地址：固化抓包地址
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 3. 登录参数：复刻抓包 JSON
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
    终极解密逻辑：AES解密 + 自动解压 + 容错编码
    """
    try:
        data = data.strip()
        key_bytes = AES_KEY.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 兼容 Hex 或 Base64 格式
        raw_data = bytes.fromhex(data) if all(c in "0123456789abcdefABCDEF" for c in data[:10]) else base64.b64decode(data)
        
        # 执行 AES 解密
        decrypted = cipher.decrypt(raw_data)
        
        # 去除 PKCS5 填充
        padding_len = decrypted[-1]
        if 0 < padding_len <= 16:
            decrypted = decrypted[:-padding_len]
        
        # --- 解决 1000069027.jpg 报错的核心步骤 ---
        # 尝试 1：如果是 Gzip 压缩的数据，先解压
        try:
            return gzip.decompress(decrypted).decode('utf-8')
        except:
            pass

        # 尝试 2：直接 UTF-8 解码，忽略无法解析的错误字符
        try:
            return decrypted.decode('utf-8', errors='ignore')
        except:
            return None
            
    except Exception as e:
        print(f"[-] 解密失败: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip" # 告诉服务器我们可以处理压缩
    }
    
    print(f"[+] 正在连接接口并获取数据...")
    try:
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=20)
        if response.status_code == 200:
            content = response.text
            print(f"[*] 收到密文，长度: {len(content)}")
            
            result = decrypt_iptv(content)
            
            # 只要包含 http 或者是 JSON 格式就保存
            if result and ("http" in result or result.strip().startswith("{")):
                print("[+] 解密成功！正在保存 live.m3u...")
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                print(f"[!] 解密后的内容异常，预览: {repr(result)[:100]}")
        else:
            print(f"[-] 服务器状态异常: {response.status_code}")
    except Exception as e:
        print(f"[-] 运行出错: {e}")

if __name__ == "__main__":
    main()
