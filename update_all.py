import base64
import json
import requests
import gzip
import re
from Crypto.Cipher import AES

# --- 配置区 ---
# 1. 登录地址
API_URL = "http://api.cdnhs.store/iptv/login3.php"

# 2. 解密密钥 (补零至 16 位)
KEY_IV = "6688000000000000"

# 3. 登录参数
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

def get_pure_txt(raw_data):
    """
    处理 AES 解密后的数据：判定 Gzip -> 强转 UTF-8 -> 清洗 TXT 特征
    """
    try:
        # 自动识别并解压 Gzip
        gz_flag = raw_data.find(b'\x1f\x8b')
        if gz_flag != -1:
            raw_data = gzip.decompress(raw_data[gz_flag:])
        
        # 转码为文本，忽略无法解码的脏字节
        text = raw_data.decode('utf-8', errors='ignore')
        
        # 锁定 TXT 频道列表的真实起始点 (跳过解密残留的垃圾头)
        # 寻找第一个汉字、字母或 # 号
        start_match = re.search(r'[\u4e00-\u9fa5a-zA-Z#]', text)
        if start_match:
            text = text[start_match.start():]
            
        return text.strip()
    except Exception as e:
        print(f"[-] 文本清洗失败: {e}")
        return None

def decrypt_core(encoded_text):
    """
    Base64 解码 -> AES 解密
    """
    try:
        # 1. Base64 解码
        encrypted_bytes = base64.b64decode(encoded_text)
        
        # 2. AES-CBC 解密
        key_bytes = KEY_IV.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        decrypted = cipher.decrypt(encrypted_bytes)
        
        # 3. 移除 Padding (PKCS5)
        pad_len = decrypted[-1]
        if 0 < pad_len <= 16:
            decrypted = decrypted[:-pad_len]
            
        return get_pure_txt(decrypted)
    except Exception as e:
        print(f"[-] 解密链路崩溃: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"[+] 正在请求接口: {API_URL}")
    try:
        response = requests.post(API_URL, data=PAYLOAD, headers=headers, timeout=15)
        if response.status_code == 200:
            print(f"[*] 收到密文，开始全自动解密 (Base64+AES+Gzip)...")
            final_result = decrypt_core(response.text)
            
            if final_result:
                # 严格执行：只输出 live.txt
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(final_result)
                print("[+] 成功！live.txt 已生成。")
                print(f"[数据摘要]\n{final_result[:80]}...")
            else:
                print("[-] 错误：解密后无有效内容。")
        else:
            print(f"[-] 接口响应异常，状态码: {response.status_code}")
    except Exception as e:
        print(f"[-] 运行报错: {e}")

if __name__ == "__main__":
    main()
