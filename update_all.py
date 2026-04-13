import base64
import json
import requests
import gzip
import re
from Crypto.Cipher import AES

# 1. 核心解密参数 (根据骆驼工具截图和Smali源码还原)
API_URL = "http://api.cdnhs.store/iptv/login3.php"
AES_KEY_IV = "6688000000000000"

# 2. 深度模拟真机设备指纹
# 必须使用这组特定的 ID，这是解开“全套源”的授权钥匙
DEVICE_INFO = {
    "login": json.dumps({
        "region": "",
        "mac": "c1:bd:92:03:55:bc",          # 匹配工具中的授权MAC
        "androidid": "5cb5bd4ece1d700c",    # 匹配工具中的Android ID
        "model": "TAL-AN000",               # 模拟真机型号
        "nettype": "WIFI",
        "appname": "MYlive"
    })
}

def force_decrypt(encoded_text):
    """
    万无一失解密流：Base64 -> AES -> 多层Gzip
    """
    try:
        # 第一步：处理 Base64
        raw_cipher = base64.b64decode(encoded_text)
        
        # 第二步：AES/CBC 解密
        key = AES_KEY_IV.encode('utf-8')
        cipher = AES.new(key, AES.MODE_CBC, key)
        decrypted = cipher.decrypt(raw_cipher)
        
        # 移除 Padding
        pad_len = decrypted[-1]
        if 0 < pad_len <= 16:
            decrypted = decrypted[:-pad_len]
            
        # 第三步：解决 1000069040.jpg 乱码的关键——多层强制解压
        # 只要头部符合 Gzip 特征 (1f 8b)，就持续解压直到露出 TXT 真相
        for _ in range(3):
            if decrypted.startswith(b'\x1f\x8b'):
                try:
                    decrypted = gzip.decompress(decrypted)
                except:
                    break
            else:
                break
        
        # 第四步：清洗转码
        # 尝试 UTF-8 和 GBK，确保中文不乱码
        for encoding in ['utf-8', 'gbk']:
            try:
                content = decrypted.decode(encoding)
                if '#' in content:  # 只有包含分类符才判定为成功
                    # 剔除解密后头部的脏字符
                    start_pos = re.search(r'[\u4e00-\u9fa5a-zA-Z#]', content)
                    if start_pos:
                        return content[start_pos.start():].strip()
            except:
                continue
        return None
    except Exception as e:
        print(f"[-] 解密链路异常: {e}")
        return None

def main():
    # 模拟 APP 发包头
    headers = {
        "User-Agent": "MSIE",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Host": "api.cdnhs.store"
    }
    
    print(f"[+] 正在绕过第三方网站，直接从源头提取全套源...")
    try:
        # 直接向服务器请求密文
        resp = requests.post(API_URL, data=DEVICE_INFO, headers=headers, timeout=20)
        
        if resp.status_code == 200:
            print(f"[*] 密文抓取成功 (长度: {len(resp.text)})，正在执行本地深度还原...")
            final_txt = force_decrypt(resp.text)
            
            if final_txt:
                # 确定只生成 live.txt
                with open("live.txt", "w", encoding="utf-8") as f:
                    f.write(final_txt)
                print("[+] 解密成功！标准的 TXT 格式全套源已生成到 live.txt。")
            else:
                print("[-] 错误：解密失败，内容依旧为乱码。请检查设备 ID 是否被服务器屏蔽。")
        else:
            print(f"[-] 服务器连接失败，状态码: {resp.status_code}")
    except Exception as e:
        print(f"[-] 执行过程报错: {e}")

if __name__ == "__main__":
    main()
