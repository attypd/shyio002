import base64
import json
import requests
import gzip
import io
from Crypto.Cipher import AES

# 1. 钥匙：由 Smali 逻辑确定的 16 位 Key
AES_KEY = "6688000000000000"

# 2. 真实登录地址
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 3. 完整登录参数
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

def clean_and_decode(raw_bytes):
    """
    处理解密后的二进制数据，尝试还原为正常文本
    """
    # 尝试 1: 检查是否为 Gzip 压缩数据
    try:
        # Gzip 的魔数开头是 1f 8b
        if raw_bytes.startswith(b'\x1f\x8b'):
            return gzip.decompress(raw_bytes).decode('utf-8')
    except:
        pass

    # 尝试 2: 暴力解码并寻找 http 起始点
    try:
        text = raw_bytes.decode('utf-8', errors='ignore')
        if "http" in text:
            # 剪掉 http 之前的任何乱码头
            return text[text.find("http"):]
        return text
    except:
        return str(raw_bytes)

def decrypt_iptv(data):
    try:
        data = data.strip()
        key_bytes = AES_KEY.encode('utf-8')
        # APP 采用 AES/CBC/PKCS5Padding
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 判断是 Hex 还是 Base64
        if all(c in "0123456789abcdefABCDEF" for c in data[:10]):
            raw_data = bytes.fromhex(data)
        else:
            raw_data = base64.b64decode(data)
            
        decrypted = cipher.decrypt(raw_data)
        
        # 去除填充位
        padding_len = decrypted[-1]
        if 0 < padding_len <= 16:
            decrypted = decrypted[:-padding_len]
            
        return clean_and_decode(decrypted)
    except Exception as e:
        print(f"[-] 解密环节出错: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip"
    }
    
    print(f"[+] 正在请求接口...")
    try:
        response = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        if response.status_code == 200:
            content = response.text
            print(f"[*] 收到数据，长度: {len(content)}")
            
            result = decrypt_iptv(content)
            
            if result:
                # 无论结果如何都保存，方便我们看效果
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(result)
                print("[+] live.m3u 写入成功！")
                if "http" in result:
                    print("[#] 检测到有效链接，大功告成！")
                else:
                    print("[!] 写入的内容好像还是有问题，请检查仓库文件。")
            else:
                print("[-] 解析结果为空。")
        else:
            print(f"[-] 服务器响应异常，状态码: {response.status_code}")
    except Exception as e:
        print(f"[-] 脚本执行异常: {e}")

if __name__ == "__main__":
    main()
