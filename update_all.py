import requests
import base64
import json
import re
from Crypto.Cipher import AES

# --- 核心配置 ---
API_URL = "http://api.cdnhs.store/iptv//login3.php"
# 身份指纹
LOGIN_PAYLOAD = {
    'login': '{"region":"","mac":"d8:45:65:5c:8d:4b","androidid":"d879d7610bc68a18","model":"23078RKD5C","nettype":"","appname":"MYlive"}'
}

# 扩充 Key 库 (根据常见骆驼壳变体)
KEYS = [
    "6688cool_key_668", 
    "1234567890123456", 
    "6688cool_key_888",
    "cdnhs_store_6688"
]

def force_decode(raw_str):
    """强行提取 JSON 部分，防止解密后带尾巴"""
    match = re.search(r'\{.*\}', raw_str, re.DOTALL)
    return match.group(0) if match else None

def crack():
    headers = {"User-Agent": "MSIE", "Content-Type": "application/x-www-form-urlencoded"}
    print("[+] 正在请求云端密文...")
    try:
        r = requests.post(API_URL, data=LOGIN_PAYLOAD, headers=headers, timeout=15)
        cipher_text = r.text.strip()
        print(f"[*] 获取密文长度: {len(cipher_text)}")
        
        raw_bytes = base64.b64decode(cipher_text)
        for k in KEYS:
            kb = k.encode('utf-8')
            try:
                # 严格执行截图中的 CBC 模式
                cipher = AES.new(kb, AES.MODE_CBC, iv=kb[:16])
                decrypted = cipher.decrypt(raw_bytes).decode('utf-8', errors='ignore')
                
                json_str = force_decode(decrypted)
                if json_str and '"data"' in json_str:
                    print(f"[*] 爆破成功！Key: {k}")
                    data = json.loads(json_str)
                    with open("live.m3u", "w", encoding="utf-8") as f:
                        f.write("#EXTM3U\n")
                        for item in data.get('data', []):
                            f.write(f"#EXTINF:-1,{item['name']}\n{item['url']}\n")
                    return True
            except: continue
        return False
    except Exception as e:
        print(f"[-] 错误: {e}")
        return False

if __name__ == "__main__":
    if crack():
        print("[+] 同步成功，live.m3u 已生成。")
    else:
        print("[!] 破解失败。请去 MT 搜索 const-string 并贴给我。")
