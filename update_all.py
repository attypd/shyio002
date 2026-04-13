import requests
import base64
import json
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# --- 配置 ---
API_URL = "http://api.cdnhs.store/iptv//login3.php"
# 身份指纹
LOGIN_PAYLOAD = {
    'login': '{"region":"","mac":"d8:45:65:5c:8d:4b","androidid":"d879d7610bc68a18","model":"23078RKD5C","nettype":"","appname":"MYlive"}'
}

# 密钥爆破库 (基于骆驼NEW及cdnhs常见特征)
KEYS = [
    "6688cool_key_668", 
    "1234567890123456", 
    "6688cool_key_888",
    "6688cool-key-668"
]

def try_decrypt(cipher_data, key_str):
    kb = key_str.encode('utf-8')
    # 尝试多种可能的 IV 组合
    possible_ivs = [kb[:16], b'0000000000000000', b'0123456789abcdef']
    
    for iv in possible_ivs:
        try:
            # 严格对应 MT 中的 CBC 模式
            cipher = AES.new(kb, AES.MODE_CBC, iv=iv)
            decrypted = cipher.decrypt(cipher_data)
            
            # 尝试多种填充剥离方式
            for pad_size in [16, 32]:
                try:
                    plain = unpad(decrypted, pad_size).decode('utf-8')
                    if '"data"' in plain: return plain
                except: continue
            
            # 强行解码看是否有 JSON 特征
            plain_raw = decrypted.decode('utf-8', errors='ignore')
            if '"data"' in plain_raw: return plain_raw
        except: continue
    return None

def main():
    headers = {"User-Agent": "MSIE", "Content-Type": "application/x-www-form-urlencoded"}
    print("[+] 正在请求云端密文...")
    try:
        r = requests.post(API_URL, data=LOGIN_PAYLOAD, headers=headers, timeout=15)
        cipher_text = r.text.strip()
        print(f"[*] 密文长度: {len(cipher_text)}")
        
        raw_bytes = base64.b64decode(cipher_text)
        success_json = None
        
        for k in KEYS:
            res = try_decrypt(raw_bytes, k)
            if res:
                print(f"[*] 密钥匹配成功: {k}")
                success_json = res
                break
        
        if success_json:
            # 提取 JSON 边界
            match = re.search(r'\{.*\}', success_json, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n")
                    for item in data.get('data', []):
                        f.write(f"#EXTINF:-1,{item.get('name')}\n{item.get('url')}\n")
                print(f"[+] 任务完成！共提取 {len(data.get('data', []))} 个频道。")
                return
        print("[!] 破解失败。说明密钥不在常用库中。")
    except Exception as e:
        print(f"[-] 运行异常: {e}")

if __name__ == "__main__":
    main()
