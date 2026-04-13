import base64
import json
import requests
import gzip
from Crypto.Cipher import AES

# 1. 钥匙：由 "6688" 补零至 16 位，完全匹配 Smali 逻辑
AES_KEY = "6688000000000000"

# 2. 登录地址：已直接写死
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
        
        # 兼容 Hex（十六进制）或 Base64 格式
        if all(c in "0123456789abcdefABCDEF" for c in data[:10]):
            raw_data = bytes.fromhex(data)
        else:
            raw_data = base64.b64decode(data)
        
        # 执行 AES 解密
        decrypted = cipher.decrypt(raw_data)
        
        # 去除 AES 填充
        padding_len = decrypted[-1]
        if 0 < padding_len <= 16:
            decrypted = decrypted[:-padding_len]
        
        # 核心环节：尝试 Gzip 解压（应对 1000069027.jpg 中的乱码报错）
        try:
            return gzip.decompress(decrypted).decode('utf-8')
        except:
            # 如果不是压缩包，尝试强制转码并忽略非法字节
            return decrypted.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"[-] 解密出现异常: {e}")
        return None

def main():
    # 模拟手机端 Header，声明支持 Gzip
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip"
    }
    
    print(f"[+] 正在请求接口: {LOGIN_URL}")
    try:
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=20)
        if response.status_code == 200:
            content = response.text
            print(f"[*] 收到密文，长度: {len(content)}")
            
            result = decrypt_iptv(content)
            
            # 只要解析出 http 链接就视为成功并保存
            if result and "http" in result:
                print("[+] 解密成功！正在保存 live.m3u...")
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
            else:
                # 最后的兜底：如果服务器直接返明文
                if "http" in content:
                    with open("live.m3u", "w", encoding="utf-8") as f:
                        f.write(content)
                    print("[+] 直接保存明文数据。")
                else:
                    print(f"[!] 解析结果不含链接。预览: {repr(result)[:50]}")
        else:
            print(f"[-] 请求失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"[-] 脚本运行异常: {e}")

if __name__ == "__main__":
    main()
