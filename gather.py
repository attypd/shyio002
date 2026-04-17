import requests
import base64
import re

# 使用聚合类的超级源，这些源后台会自动汇总几千个节点
SOURCES = [
    "https://raw.githubusercontent.com/mfen625/free_node/main/v2ray.txt",
    "https://raw.githubusercontent.com/vless-free/free/main/v2",
    "https://raw.githubusercontent.com/ripaojiedian/freenode/main/v2ray",
    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml"
]

def main():
    raw_nodes = []
    print("🚀 启动超级收割模式...")
    
    for url in SOURCES:
        try:
            # 增加超时时间，防止空手而归
            r = requests.get(url, timeout=20)
            content = r.text
            
            # 自动尝试 Base64 解码
            if "://" not in content:
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: pass
            
            # 暴力抓取所有 vmess, vless, ss, trojan 链接
            found = re.findall(r'(?:vmess|vless|ss|trojan)://[^\s]+', content)
            raw_nodes.extend(found)
        except:
            print(f"⚠️ 源 {url[:30]} 暂时无法访问")
            continue

    # 去重并只保留前 150 个，太多了软件加载也慢
    unique_nodes = list(dict.fromkeys(raw_nodes))
    final_list = unique_nodes[:150]
    
    print(f"📡 成功抓取到 {len(final_list)} 个节点！")

    if final_list:
        out_str = base64.b64encode("\n".join(final_list).encode()).decode()
        with open("nodes.txt", "w") as f:
            f.write(out_str)
        print(f"✅ nodes.txt 已保存。")
    else:
        # 如果实在抓不到，写个假的提示一下，别让 nodes.txt 为空
        print("❌ 依然没抓到，请检查网络源是否被屏蔽。")

if __name__ == "__main__":
    main()
