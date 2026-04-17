import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# 增加更多源，保证底数够大
NODE_SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/vless-free/free/main/v2",
    "https://raw.githubusercontent.com/Pawpieee/Free-Proxies/main/sub/sub_merge.txt",
    "https://raw.githubusercontent.com/tovade/Sources/main/GZ/sub_merge.txt",
    "https://raw.githubusercontent.com/lonre/v2ray-free/master/v2ray",
    "https://raw.githubusercontent.com/Guovv/free-nodes/main/node.txt"
]

def is_target_line(node_str):
    # 只要是美国、电信、联通线路，或者包含 4837/9929 这种移动救星线路都行
    keywords = ['US', '美国', '电信', '联通', 'CN2', '4837', '9929', 'GIA', 'America']
    return any(k.upper() in node_str.upper() for k in keywords)

def test_node(node):
    try:
        match = re.search(r'@([^:]+):(\d+)', node)
        if match:
            host, port = match.group(1), int(match.group(2))
            # 稍微放宽到 2 秒，给移动网络一点容错空间
            with socket.create_connection((host, port), timeout=2.0):
                return node
    except:
        pass
    return None

def main():
    all_raw_nodes = []
    print("🚀 正在从全网收割高质量线路...")
    
    for url in NODE_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            content = r.text
            if "://" not in content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: continue
            found = re.findall(r'(?:vmess|vless|ss|ssr|trojan)://[^\s]+', content)
            all_raw_nodes.extend(found)
        except: continue

    # 1. 线路过滤
    target_nodes = [n for n in all_raw_nodes if is_target_line(n)]
    # 2. 去重
    unique_nodes = list(set(target_nodes))
    print(f"📡 筛选出候选目标 {len(unique_nodes)} 个，开始压测...")

    # 3. 测速
    with ThreadPoolExecutor(max_workers=100) as executor:
        valid_nodes = list(filter(None, executor.map(test_node, unique_nodes)))

    # 4. 如果筛选后太少，就抓几个不限线路的美国节点保底
    if len(valid_nodes) < 5:
        print("⚠️ 优质线路较少，正在补充常规美国节点...")
        us_only = [n for n in all_raw_nodes if 'US' in n.upper()][:20]
        valid_nodes.extend(us_only)

    # 5. 编码输出
    final_data = base64.b64encode("\n".join(list(set(valid_nodes))).encode()).decode()
    with open("nodes.txt", "w") as f:
        f.write(final_data)
    print(f"✅ 任务完成！本次为你找到 {len(set(valid_nodes))} 个可用节点。")

if __name__ == "__main__":
    main()
