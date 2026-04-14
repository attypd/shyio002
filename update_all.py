import base64, json, requests, gzip
from Crypto.Cipher import AES

# --- 【必杀技】挖掘出的全网最稳授权 ID (直接锁定) ---
MAC = "00:11:ad:e3:10:96"  # 经过算法匹配的特定授权地址
ID = "5cb5bd4ece1d700c"    # 安卓底层指纹
MODEL = "MI 6"              # 经典高兼容型号
# -----------------------------------------------

KEY_IV = "6688000000000000" # 核心密钥

def deep_extract(raw):
    """暴力扫描算法：不相信服务器返回的任何偏移量，全量搜索 Gzip"""
    try:
        data = base64.b64decode(raw)
        cipher = AES.new(KEY_IV.encode(), AES.MODE_CBC, KEY_IV.encode())
        dec = cipher.decrypt(data)
        
        # 扫描 0-512 字节的所有偏移位，寻找 Gzip 特征头
        for i in range(512):
            if dec[i:i+2] == b'\x1f\x8b':
                try:
                    p = dec[i:]
                    while p.startswith(b'\x1f\x8b'): # 处理多重压缩
                        p = gzip.decompress(p)
                    txt = p.decode('utf-8', errors='ignore')
                    if '#' in txt: return txt.strip()
                except: continue
        return None
    except: return None

def main():
    s = requests.Session()
    # 模拟真实移动端网络握手
    s.headers.update({
        "User-Agent": f"Dalvik/2.1.0 (Linux; U; Android 7.1.1; {MODEL} Build/NMF26X)",
        "X-Requested-With": "com.vv.test",
        "Content-Type": "application/x-www-form-urlencoded"
    })

    api = "http://api.cdnhs.store/iptv/data.php"
    payload = {"login": json.dumps({"mac": MAC, "androidid": ID, "model": MODEL})}

    print(f"[!] 正在强制从服务器挖掘全套源 (ID: {MAC})...")
    try:
        r = s.post(api, data=payload, timeout=20)
        # 即使返回 200，内容也可能是混淆的，强制执行解密
        if r.status_code == 200:
            res = deep_extract(r.text)
            if res:
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(res)
                print("[成功] 攻破云端校验！全套源已导出到 live.txt。")
                return
    except Exception as e: print(f"[-] 异常: {e}")
    print("[失败] 服务器拒绝了这组 ID。请确认 api.cdnhs.store 目前是否还在维护。")

if __name__ == "__main__":
    main()
