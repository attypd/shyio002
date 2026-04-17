import requests
import base64
import re

# 换成目前最能打、更新最勤、且包含大量 VLESS Reality（移动救星）的源
SOURCES = [
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub1.txt",
    "https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/Sub2.txt",
    "https://raw.githubusercontent.com/cmliu/CF-Workers-vless/main/sub",
    "https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/base64"
]

def main():
    raw_nodes = []
    print("🚀 正在针对移动宽带锁定『Reality & VLESS』抗封锁线路...")
    
    for url in SOURCES:
        try:
            # 增加 User-Agent 模拟浏览器，防止被源站拦截
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(url, headers=headers, timeout=15)
            content = r.text
            
            # 如果是 Base64 加密格式，尝试解码
            if "://" not in content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: continue
            
            # 只要 vless 和 vmess 协议，ss/ssr 直接扔掉，移动宽带秒封
            found = re.findall(r'(?:vless|vmess)://[^\s]+', content)
            raw_nodes.extend(found)
        except: continue

    # 关键：去重并只拿最新的 50 个
    # 节点不是越多越好，新鲜度才是移动宽带下活命的关键
    unique_nodes = list(dict.fromkeys(raw_nodes))
    final_list = unique_nodes[:60]
    
    print(f"📡 已为您捕获 {len(final_list)} 个新鲜抗封锁节点。")

    if final_list:
        out_str = base64.b64encode("\n".join(final_list).encode()).decode()
        with open("nodes.txt", "w") as f:
            f.write(out_str)
        print(f"✅ 搞定！nodes.txt 已更新。")
    else:
        print("❌ 没抓到货，可能是网络环境导致源请求失败。")

if __name__ == "__main__":
    main()
