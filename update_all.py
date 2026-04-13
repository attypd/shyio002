import base64
import json
import requests
from Crypto.Cipher import AES

# 这里是根据你的 Smali 代码推导出的 16 位钥匙
# 逻辑：基础钥匙 "6688" 不满 16 位，程序会自动在后面补 "0"
AES_KEY = "6688000000000000"

def decrypt(data, key):
    """
    标准的 AES/CBC/PKCS5Padding 解密逻辑
    """
    try:
        # 在这个 APP 中，Key 和 IV (偏移量) 通常使用的是同一个字符串
        key_bytes = key.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        
        # 先进行 Base64 解码，再解密
        decrypted = cipher.decrypt(base64.b64decode(data))
        
        # 去除 PKCS5 填充
        padding_len = decrypted[-1]
        result = decrypted[:-padding_len].decode('utf-8')
        return result
    except Exception as e:
        print(f"解密尝试失败: {e}")
        return None

def main():
    # 模拟你之前的 Action 流程
    # 假设这是从服务器获取到的加密数据 (对应你日志里的 1196 字节内容)
    url = "你的直播源接口地址" 
    payload = {
        "mac": "你的MAC地址",
        "androidid": "你的AndroidID",
        "model": "vm",
    }
    
    print("[+] 正在请求云端密文...")
    try:
        # 这里模拟请求逻辑，实际使用时请保留你原有的 requests 请求部分
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            encrypted_data = response.text
            print(f"[*] 获取密文长度: {len(encrypted_data)}")
            
            # 使用我们找出来的 6688 钥匙进行解密
            decrypted_text = decrypt(encrypted_data, AES_KEY)
            
            if decrypted_text and "http" in decrypted_text:
                print("[+] 成功解密数据！")
                # 这里可以继续写你保存为 live.m3u 的逻辑
                with open("live.m3u", "w", encoding="utf-8") as f:
                    f.write(decrypted_text)
                print("[+] 文件 live.m3u 已生成。")
            else:
                print("[!] 解密后的数据格式不对，请检查 KEY 是否正确。")
    except Exception as e:
        print(f"[-] 请求失败: {e}")

if __name__ == "__main__":
    main()
