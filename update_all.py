import base64
import json
import requests
import gzip
import re
from Crypto.Cipher import AES

# 1. 登录地址：已根据抓包图固化
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 2. 核心密钥：严格对齐 Smali 的 16 位补零 Key
AES_KEY_IV = "6688000000000000"

# 3. 登录请求参数
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

def decrypt_to_txt(encoded_str):
    """
    全套源解密：Base64解码 -> AES解密 -> Gzip解压
    """
    try:
        # 第一层：Base64 解码
        raw_enc = base64.b64decode(encoded_str)
        
        # 第二层：AES/CBC 解密
        key_bytes = AES_KEY_IV.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        decrypted = cipher.decrypt(raw_enc)
        
        # 移除 AES 填充字节
        pad_len = decrypted[-1]
        if 0 < pad_len <= 16:
            decrypted = decrypted[:-pad_len]
            
        # 第三层：Gzip 判定与解压缩（解决乱码关键）
        try:
            gz_head = decrypted.find(b'\x1f\x8b')
            if gz_head != -1:
                decrypted = gzip.decompress(decrypted[gz_head:])
        except:
            pass

        # 第四层：清洗转码为标准 TXT
        text = decrypted.decode('utf-8', errors='ignore')
        
        # 针对 TXT 特征，跳过头部的非打印乱码字节
        match = re.search(r'[\u4e00-\u9fa5a-zA-Z#]', text)
        if match:
            text = text[match.start():]
            
        return text.strip()

    except Exception as e:
        print(f"[-] 链路解密失败: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"[+] 正在访问全套源接口...")
    try:
        resp = requests.post(LOGIN_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        
        if resp.status_code == 200:
            print(f"[*] 密文获取成功。正在执行深度解密...")
            final_txt = decrypt_to_txt(resp.text)
            
            if final_txt:
                # 确定只输出 live.txt
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(final_txt)
                print("[+] 全套源解密完成！已生成 live.txt。")
                print(f"[预览]\n{final_txt[:120]}...")
            else:
                print("[-] 错误：未能解出有效文本。")
        else:
            print(f"[-] 接口响应失败: {resp.status_code}")
            
    except Exception as e:
        print(f"[-] 运行异常: {e}")

if __name__ == "__main__":
    main()
