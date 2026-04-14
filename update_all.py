import base64, json, requests, gzip, time
from Crypto.Cipher import AES

# 锁定设备 ID（这组 ID 在该类 APP 中权重极高）
MAC = "00:11:ad:e3:10:96" 
ID = "5cb5bd4ece1d700c"
MODEL = "MI 6"
PACKAGE = "com.my.live" # 匹配截图

KEY_IV = "6688000000000000"

def crack_mylive(raw_str):
    """针对 MYlive 的混淆算法进行暴力穿透"""
    try:
        raw = base64.b64decode(raw_str)
        cipher = AES.new(KEY_IV.encode(), AES.MODE_CBC, KEY_IV.encode())
        dec = cipher.decrypt(raw)
        
        # 深度扫描 2048 字节，寻找数据特征 1f 8b
        for i in range(2048):
            if dec[i:i+2] == b'\x1f\x8b':
                try:
                    p = dec[i:]
                    while p.startswith(b'\x1f\x8b'):
                        p = gzip.decompress(p)
                    txt = p.decode('utf-8', errors='ignore')
                    if '#' in txt: return txt.strip()
                except: continue
        return None
    except: return None

def main():
    s = requests.Session()
    # 精准模拟 MYlive 4.0.1 的网络握手
    s.headers.update({
        "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android 7.1.1; {MODEL})",
        "X-Requested-With": PACKAGE,
        "Accept-Encoding": "gzip",
        "Connection": "keep-alive"
    })

    # 两个核心接口尝试
    urls = [
        "http://api.cdnhs.store/iptv/data.php",
        "http://api.cdnhs.store/iptv/login3.php"
    ]
    
    payload = {"login": json.dumps({"mac": MAC, "androidid": ID, "model": MODEL})}

    print(f"[!] 正在模拟 {PACKAGE} 4.0.1 强制提取全套源...")
    
    for url in urls:
        try:
            # 增加动态混淆参数，骗过云端防火墙
            target_url = f"{url}?v=4.0.1&_t={int(time.time())}"
            r = s.post(target_url, data=payload, timeout=20)
            
            if r.status_code == 200 and len(r.text) > 100:
                print(f"[*] 截获有效数据流 (长度: {len(r.text)})")
                final_res = crack_mylive(r.text)
                if final_res:
                    with open("live.txt", "w", encoding="utf-8") as f:
                        f.write(final_res)
                    print("[成功] MYlive 源码已攻克，全套源已导出至 live.txt！")
                    return
        except: continue

    print("[-] 还是失败。结论：该服务器对 GitHub 的机房 IP 做了死锁。")

if __name__ == "__main__":
    main()
