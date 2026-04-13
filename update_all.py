import requests
import base64
import json
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- 配置区 ---
API_URL = "http://api.cdnhs.store/iptv//login3.php"
# 基于抓包图 1000068984.jpg 的身份信息
LOGIN_DATA = {
    'login': '{"region":"","mac":"d8:45:65:5c:8d:4b","androidid":"d879d7610bc68a18","model":"23078RKD5C","nettype":"","appname":"MYlive"}'
}

# 模拟 MT 搜索出的潜在 Key
KEYS = ["6688cool_key_668", "1234567890123456", "MYlive6688cool_!"]

def decrypt_payload(cipher_text):
    try:
        raw_bytes = base64.b64decode(cipher_text)
    except:
        return None

    for k in KEYS:
        k_b = k.encode('utf-8')
        try:
            # 严格匹配 MT 中的 CBC 模式
            # 大部分骆驼壳 IV 与 Key 相同
            cipher = AES.new(k_b, AES.MODE_CBC, iv=k_b)
            decrypted = cipher.decrypt(raw_bytes)
            
            # 容错解码逻辑
            try:
                plain = unpad(decrypted, AES.block_size).decode('utf-8')
            except:
                plain = decrypted.decode('utf-8', errors='ignore')

            if '"data"' in plain:
                print(f"[*] 成功碰撞出密钥: {k}")
                return plain
        except:
            continue
    return None

def main():
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "api.cdnhs.store"
    }
    print("[*] 正在请求云端数据...")
    try:
        resp = requests.post(API_URL, data=LOGIN_DATA, headers=headers, timeout=15)
        if resp.status_code != 200:
            print(f"[!] 服务器响应错误: {resp.status_code}")
            return

        # 对应图 1000068992.jpg 中的超长密文处理
        json_str = decrypt_payload(resp.text.strip())
        
        if json_str:
            # 提取 JSON 核心部分
            match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if match:
                res_data = json.loads(match.group(0))
                channels = res_data.get('data', [])
                
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write("#EXTM3U name=\"Auto_Update\"\n")
                    for ch in channels:
                        f.write(f"#EXTINF:-1,{ch.get('name')}\n{ch.get('url')}\n")
                print(f"[+] 成功！已更新 {len(channels)} 个频道。")
        else:
            print("[!] 破解失败，请检查 Key 是否有变动。")
    except Exception as e:
        print(f"[!] 运行异常: {e}")

if __name__ == "__main__":
    main()
