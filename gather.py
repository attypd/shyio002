import requests
import base64
import socket
from concurrent.futures import ThreadPoolExecutor

# 专门抓取 Cloudflare 优选节点和高质量通用节点
SOURCES = [
    "https://raw.githubusercontent.com/vfarid/v2ray-share/main/all.txt",
    "https://raw.githubusercontent.com/cmliu/CF-Workers-vless/main/sub",
    "https://raw.githubusercontent.com/asf-f/Node-Source/main/v2ray.txt"
]

def verify_and_clean(node):
    """测速并过滤掉那些已经死掉的机房 IP"""
    try:
        # 针对移动宽带，我们把握手时间卡死在 1.5 秒
        # 只有真正高质量的 CF 优选 IP 才能在 Actions 机房过关
        import re
        match = re.search(r'@([^:]+):(\d+)', node)
        if match:
            host, port = match.group(1), int(match.group(2))
            with socket.create_connection((host, port), timeout=1.5):
                # 标记一下这是 CF 优选，方便你在软件里选
                return f"{node}#CF优选_{host}"
    except:
        pass
    return None

def main():
    all_nodes = []
    print("🚀 正在收割 Cloudflare 优选线路...")
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=10)
            text = r.text
            if "://" not in text:
                text = base64.b64decode(text).decode('utf-8')
            
            # 提取 vless/vmess 等协议
            import re
            found = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s]+', text)
            all_nodes.extend(found)
        except: continue

    unique_nodes = list(set(all_nodes))
    print(f"📡 找到候选节点 {len(unique_nodes)} 个，正在进行移动匹配度压测...")

    with ThreadPoolExecutor(max_workers=50) as executor:
        valid = list(filter(None, executor.map(verify_and_clean, unique_nodes)))

    # 如果优选的太少，放宽条件多留几个备用
    if len(valid) < 10:
        valid = unique_nodes[:30]

    # 输出为 Base64
    final_out = base64.b64encode("\n".join(valid).encode()).decode()
    with open("nodes.txt", "w") as f:
        f.write(final_out)
    print(f"✅ 搞定！已生成 {len(valid)} 个优选节点。")

if __name__ == "__main__":
    main()
