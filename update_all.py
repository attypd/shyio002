import base64, json, requests, gzip, time, random
from Crypto.Cipher import AES

# 锁定 MYlive 关键指纹
MAC = "00:11:ad:e3:10:96" 
ID = "5cb5bd4ece1d700c"
MODEL = "MI 6"
PACKAGE = "com.my.live"
KEY = "6688000000000000"

def final_crack(data):
    try:
        raw = base64.b64decode(data)
        c = AES.new(KEY.encode(), AES.MODE_CBC, KEY.encode())
        dec = c.decrypt(raw)
        # 针对 1196 字节混淆，强制搜索 2048 字节范围
        for i in range(2048):
            if dec[i:i+2] == b'\x1f\x8b':
                p = dec[i:]
                while p.startswith(b'\x1f\x8b'): p = gzip.decompress(p)
                res = p.decode('utf-8', errors='ignore')
                if '#' in res: return res.strip()
    except: return None
    return None

def main():
    s = requests.Session()
    # --- 核心惩罚：注入虚假住宅 IP 绕过机房封锁 ---
    fake_ip = f"112.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    s.headers.update({
        "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android 7.1.1; {MODEL})",
        "X-Requested-With": PACKAGE,
        "X-Forwarded-For": fake_ip,  # 伪造来源 IP
        "Client-IP": fake_ip,        # 伪造客户端 IP
        "Connection": "close"
    })

    url = "http://api.cdnhs.store/iptv/data.php"
    payload = {"login": json.dumps({"mac": MAC, "androidid": ID, "model": MODEL})}

    print(f"[!] 启动“强制穿透”协议：伪装 IP 为 {fake_ip}...")
    try:
        # 增加随机参数干扰服务器特征识别
        r = s.post(f"{url}?v=4.0.1&_r={random.random()}", data=payload, timeout=20)
        
        if r.status_code == 200:
            print(f"[*] 拦截数据流 (长度: {len(r.text)})")
            # 如果长度还是 1196，说明 IP 伪造被识破
            if len(r.text) == 1196:
                print("[-] 警告：服务器依然返回混淆包，IP 伪装可能未穿透防火墙。")
            
            result = final_crack(r.text)
            if result:
                with open("live.txt", "w", encoding="utf-8") as f: f.write(result)
                print("[成功] 攻破云端拦截！全套源已同步。")
                return
    except Exception as e: print(f"[-] 异常: {e}")
    print("[-] 最终结论：该服务器已开启“严格 IP 地理位置校验”，GitHub 彻底没戏。")

if __name__ == "__main__":
    main()

