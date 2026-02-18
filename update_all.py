import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"   # 原始标准分组格式文件
TOTAL_FILE = "total_live.txt"     # 全套直播源 (私密在后)
PRIVATE_FILE = "private_only.txt"  # 仅私密频道

def check_port(port):
    """验证端口：根据抓包数据，访问登录页返回 302 或 200 即可"""
    test_url = f"http://{DOMAIN}:{port}/iptv/login3.php"
    try:
        # 增加超时到 3.5s 以应对 GitHub Actions 的网络波动
        res = requests.head(test_url, timeout=3.5, allow_redirects=False)
        if res.status_code in [200, 302]:
            return str(port)
    except:
        return None
    return None

def scan_worker(port_list, desc):
    """并行扫描核心函数"""
    print(f"Scanning {desc}... Total: {len(port_list)}")
    random.shuffle(port_list) # 随机化，防止被防火墙识别
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=70) as executor:
        results = executor.map(check_port, port_list)
        for r in results:
            if r: return r
    return None

def get_latest_port():
    """分层扫描策略：核心区 -> 全量区"""
    # 1. 极高概率区
    priority = [8080, 48559, 48867]
    for p in priority:
        if check_port(p): return str(p)

    # 2. 核心扫描区 (40000-50000)
    res = scan_worker(list(range(40000, 50001)), "Core (40k-50k)")
    if res: return res

    # 3. 补漏扫描区 (20000-40000 & 50000-65535)
    print("Expanding range...")
    res = scan_worker(list(range(20000, 40000)) + list(range(50001, 65536)), "Full (20k-65k)")
    return res if res else "48559"

def update_files():
    new_port = get_latest_port()
    bj_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    other_parts = []   # 普通频道
    private_parts = [] # 私密频道
    is_private = False

    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line: continue

            # 【精准替换】仅修改包含目标域名的行，不触碰备用源
            if DOMAIN in line:
                line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{new_port}', line)

            # 【分组逻辑】识别标准 TXT 分组格式
            if "#genre#" in line:
                is_private = "私密频道" in line
            
            if is_private:
                private_parts.append(line)
            else:
                other_parts.append(line)

        # 生成全量文件：普通在前，私密在后
        with open(TOTAL_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(other_parts + private_parts))
            f.write(f"\n\n# 自动更新: {bj_time} | 端口: {new_port}")

        # 生成纯私密文件
        if private_parts:
            with open(PRIVATE_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(private_parts))
                f.write(f"\n# 更新时间: {bj_time}")

        print(f"Done! Port: {new_port}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_files()
