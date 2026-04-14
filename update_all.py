import base64, json, requests, gzip, time
from Crypto.Cipher import AES

# 锁定这组正在尝试启动的设备 ID
MAC = "00:11:ad:e3:10:96" 
ID = "5cb5bd4ece1d700c"
MODEL = "MI 6"
KEY = "6688000000000000"

def extract_content(raw_data):
    """
    针对启动瞬间下发的混淆包进行穿透
    """
    try:
        data = base64.b64decode(raw_data)
        cipher = AES.new(KEY.encode(), AES.MODE_CBC, KEY.encode())
        dec = cipher.decrypt(data)
        
        # 即使没授权，前几秒下发的数据包也藏在这些偏移量里
        for offset in range(1024):
            if dec[offset:offset+2] == b'\x1f\x8b':
                try:
                    p = dec[offset:]
                    while p.startswith(b'\x1f\x8b'):
                        p = gzip.decompress(p)
                    txt = p.decode('utf-8', errors='ignore')
                    if '#' in txt: return txt.strip()
                except: continue
        return None
    except: return None

def main():
    s = requests.Session()
    # 模拟 APP 启动瞬间的特殊 Header
    s.headers.update({
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; MI 6)",
        "X-Requested-With": "com.vv.test",
        "Pragma": "no-cache" # 强制不使用缓存，索要最新数据
    })

    url = "http://api.cdnhs.store/iptv/data.php"
    payload = {"login": json.dumps({"mac": MAC, "androidid": ID, "model": MODEL})}

    print("[!] 正在利用‘启动时间差’暴力截取数据流...")
    
    # 策略：高频重试 3 次，模拟 APP 刚打开的那几秒状态
    for i in range(3):
        try:
            print(f"[*] 第 {i+1} 次尝试抢跑...")
            r = s.post(url, data=payload, timeout=10)
            
            if r.status_code == 200:
                print(f"[*] 捕获流量 ({len(r.text)})，执行全算法还原...")
                res = extract_content(r.text)
                if res:
                    with open("live.txt", "w", encoding="utf-8") as f:
                        f.write(res)
                    print("[成功] 抢在授权锁死前，成功挖掘到全套源！")
                    return
            time.sleep(1) # 短暂间隔重新发起
        except: continue

    print("[-] 抢跑失败。服务器已将该 IP 的启动数据全部替换为混淆乱码。")

if __name__ == "__main__":
    main()
