import base64
import json
import requests
from Crypto.Cipher import AES

# 1. 自动补全后的 AES 密钥：由基础 Key "6688" 补零至 16 位
AES_KEY = "6688000000000000"

# 2. 从抓包数据中提取的真实接口地址
LOGIN_URL = "http://api.cdnhs.store/iptv/login3.php"

# 3. 抓包到的真实登录请求参数
LOGIN_PARAMS = {
    "login": json.dumps({
        "region": "",
        "mac": "d8:45:65:5c:8d:4b",
        "androidid": "d879d7610bc68a18",
        "model": "23078RKD5C",
        "nettype": "",
        "appname": "MYlive"
    })
}

def decrypt_iptv(encrypted_data):
    """
    根据 Smali 逻辑实现的解密函数
    """
    try:
        key_bytes = AES_KEY.encode('utf-8')
        # APP 使用 AES/CBC/PKCS5Padding，且 IV 与 Key 相同
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # Base64 解码 -> AES 解密
        raw_data = base64.b64decode(encrypted_data)
        decrypted = cipher.decrypt(raw_data)
        
        # 去除 PKCS5 填充
        padding_len = decrypted[-1]
        result = decrypted[:-padding_len].decode('utf-8')
        return result
    except Exception as e:
        print(f"[-] 解密失败: {e}")
        return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    print(f"[+] 正在请求登录接口: {LOGIN_URL}")
    try:
        # 发送 POST 请求获取密文
        response = requests.post(LOGIN_URL, data=LOGIN_PARAMS, headers=headers, timeout=15)
        
        if response.status_code == 200:
            encrypted_text = response.text.strip()
            print(f"[*] 成功获取密文，长度: {len(encrypted_text)}")
            
            # 执行解密
            decrypted_content = decrypt_iptv(encrypted_text)
            
            if decrypted_content and "http" in decrypted_content:
                print("[+] 解密成功！正在保存 live.m3u 文件...")
                # 将解密后的直播源内容写入文件
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(decrypted_content)
                print("[+] 任务完成，文件已生成。")
            else:
                print("[!] 解密后的内容无效或不包含直播链接。")
        else:
            print(f"[-] 服务器请求失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"[-] 运行出错: {e}")

if __name__ == "__main__":
    main()
