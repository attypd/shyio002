import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# 这些是目前 GitHub 上更新最稳、质量最好的开源节点源
NODE_SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/vless-free/free/main/v2",
    "https://raw.githubusercontent.com/Pawpieee/Free-Proxies/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tovade/Sources/main/GZ/sub_merge.txt",
    "https://raw.githubusercontent.com/snakem9/Free-Proxy/main/clash.yaml" # 这种需要额外解析
]

def is_target_line(node_str):
    """筛选：只要美国节点，或者标注了电信、联通优选的节点"""
    keywords = ['US', '美国', '电信', '联通', 'CN2', '4837', '9929', 'GIA']
    return any(k.upper() in node_str.upper() for k in keywords)

def test_node(node):
    """测速：1秒内能通的才是好节点"""
    try:
        # 提取 IP 和 端口
        match = re.search(r'@([^:]+):(\d+)', node)
        if match:
            host, port = match.group(1), int(match.group(2))
            with socket.create_connection((host, port), timeout=1.0):
                return node
    except:
        pass
    return None

def main():
    all_raw_nodes = []
    print("🚀 开始全网同步大佬们的节点...")
    
    for url in NODE_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            content = r.text
            # 自动处理 Base64 编码
            if "://" not in content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: continue
            
            # 提取协议节点
            found = re.findall(r'(?:vmess|vless|ss|ssr|trojan)://[^\s]+', content)
            all_raw_nodes.extend(found)
        except:
            continue

    # 1. 过滤：目标线路
    target_nodes = [n for n in all_raw_nodes if is_target_line(n)]
    # 2. 去重
    unique_nodes = list(set(target_nodes))
    print(f"📡 筛选出候选节点 {len(unique_nodes)} 个，开始针对移动网络进行筛选...")

    # 3. 测速
    with ThreadPoolExecutor(max_workers=80) as executor:
        valid_nodes = list(filter(None, executor.map(test_node, unique_nodes)))

    # 4. 输出
    final_data = base64.b64encode("\n".join(valid_nodes).encode()).decode()
    with open("nodes.txt", "w") as f:
        f.write(final_data)
    print(f"✅ 大功告成！已为你准备好 {len(valid_nodes)} 个高质量节点。")

if __name__ == "__main__":
    main()
