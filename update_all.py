import base64
import json
import requests
import gzip
from Crypto.Cipher import AES

# 锁定核心密钥与验证设备
KEY_IV = "6688000000000000"
MAC = "c1:bd:92:03:55:bc"
ANDROID_ID = "5cb5bd4ece1d700c"

def scan_and_crack(raw_data):
    """
    暴力穿透：AES -> 搜寻 Gzip -> 循环还原
    """
    try:
        # 第一层：AES/CBC还原
        cipher_text = base64.b64decode(raw_data)
        key = KEY_IV.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, key)
        decrypted = cipher.decrypt(cipher_text)
        
        # 第二层：雷达式搜索 Gzip 头部标志 (1f 8b)
        for i in range(128):
            if decrypted[i:i+2] == b'\x1f\x8b':
                try:
                    p = decrypted[i:]
                    # 第三层：递归解压处理，直到变成 TXT
                    while p.startswith(b'\x1f\x8b'):
                        p = gzip.decompress(p)
                    
                    text = p.decode('utf-8', errors='ignore')
                    if '#' in text or ',' in text: # 验证是否为标准源格式
                        return text.strip()
                except: continue
        return None
    except: return None

def main():
    session = requests.Session()
    # 模拟最新版 APP 的 User-Agent
    session.headers.update({
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; TAL-AN000 Build/HUAWEITAL-AN000)",
        "Content-Type": "application/x-www-form-urlencoded"
    })

    # 包含数据分发和登录授权的所有可能接口
    urls = [
        "http://api.cdnhs.store/iptv/data.php",
        "http://api.cdnhs.store/iptv/login3.php"
    ]
    
    payload = {"login": json.dumps({"mac": MAC, "androidid": ANDROID_ID, "model": "TAL-AN000"})}

    print("[+] 开始执行全算法库综合突击...")
    for url in urls:
        try:
            print(f"[*] 正在渗透接口: {url}")
            resp = session.post(url, data=payload, timeout=20)
            if resp.status_code == 200 and len(resp.text) > 100:
                print(f"[*] 捕获数据流 (长度: {len(resp.text)})，执行暴力破解...")
                final_result = scan_and_crack(resp.text)
                
                if final_result:
                    with open("live.txt", "w", encoding="utf-8") as f:
                        f.write(final_result)
                    print("[!] 成功！真正的全套源已强行解密输出至 live.txt。")
                    return
            print("[-] 该路径未获得有效密文。")
        except Exception as e:
            print(f"[-] 连接异常: {e}")

if __name__ == "__main__":
    main()
