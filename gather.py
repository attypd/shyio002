import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# 换成目前全球更新最勤、节点最多的源
SOURCES = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/vless-free/free/main/v2",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/snakem9/Free-Proxy/main/clash.yaml",
    "https://raw.githubusercontent.com/PeiPeiP/Free-Proxy/main/dist/v2ray.txt"
]

def test_connection(node):
    """测速逻辑：只要能连上就行，先保证『有』"""
    try:
        # 尝试提取主机和端口
        host_port = re.search(r'@([^:]+):(\d+)', node)
        if host_port:
            host, port = host_port.group(1), int(host_port.group(2))
            # 宽限到 2.5 秒，因为 Actions 机房连接国内 IP 可能会慢
            with socket.create_connection((host, port), timeout=2.5):
                return node
    except:
        pass
    return None

def main():
    raw_list = []
    print("🚀 正在从全球聚合站收割节点...")
    
    for url in SOURCES:
        try:
            r = requests.get(url, timeout=15)
            content = r.text
            # 自动处理可能存在的 Base64 加密
            if "://" not in content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: continue
            
            # 正则抓取所有主流协议
            found = re.findall(r'(?:vmess|vless|ss|ssr|trojan)://[^\s]+', content)
            raw_list.extend(found)
        except: continue

    # 去重
    unique_nodes = list(set(raw_list))
    print(f"📡 原始节点总数: {len(unique_nodes)}，开始可用性筛选...")

    # 如果节点太多，只测前 200 个，提高成功率
    test_pool = unique_nodes[:200]

    with ThreadPoolExecutor(max_workers=50) as executor:
        valid = list(filter(None, executor.map(test_connection, test_pool)))

    # 保底机制：如果测速全挂了（可能是机房网络问题），就强行带走前 30 个
    if len(valid) < 5:
        print("⚠️ 测速通过率低，执行保底策略...")
        valid = unique_nodes[:30]

    # 最终打包
    final_str = base64.b64encode("\n".join(valid).encode()).decode()
    with open("nodes.txt", "w") as f:
        f.write(final_str)
    print(f"✅ 任务完成！已成功保存 {len(valid)} 个节点到 nodes.txt")

if __name__ == "__main__":
    main()
