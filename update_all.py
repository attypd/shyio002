import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- 核心配置 ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"   # 原始分组文件
TOTAL_FILE = "total_live.txt"     # 全量输出 (私密在后)
PRIVATE_FILE = "private_only.txt"  # 私密提取

def check_port(port):
    """判定逻辑：模拟真实壳子，识别 302 状态"""
    test_url = f"http://{DOMAIN}:{port}/iptv/login3.php"
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; 23078RKD5C Build/TKQ1.221114.001)',
        'Connection': 'Keep-Alive'
    }
    try:
        # 使用 2.0s 超时加速，只要 302 就返回
        res = requests.head(test_url, headers=headers, timeout=2.0, allow_redirects=False)
        if res.status_code == 302:
            return str(port)
    except:
        return None
    return None

def scan_ports(port_list):
    """并行扫描函数"""
    random.shuffle(port_list)
    # 并发控制在 60，防止被 GitHub 网络限制
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = executor.map(check_port, port_list)
        for r in results:
            if r: return r
    return None

def get_latest_port():
    """多组端口范围扫描逻辑"""
    # 1. 优先已知高频端口
    for p in [48559, 48867]:
        if check_port(p): return str(p)

    # 2. 核心区扫描：40000 - 50000
    res = scan_ports(list(range(40000, 50001)))
    if res: return res

    # 3. 全量区扫描：20000 - 65535
    print("Expanding scan range...")
    res = scan_ports(list(range(20000, 40000)) + list(range(50001, 65536)))
    return res if res else "48559"

def update_files():
    new_port = get_latest_port()
    bj_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    other_lines = []
    private_lines = []
    is_private_section = False

    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line: continue

            # 【精准替换】仅针对 DOMAIN 行修改，其余行原样保留
            if DOMAIN in line:
                updated_line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{new_port}', line)
            else:
                updated_line = line

            # 分组识别提取
            if "#genre#" in updated_line:
                is_private_section = "私密频道" in updated_line
            
            if is_private_section:
                private_lines.append(updated_line)
            else:
                other_lines.append(updated_line)

        # 写入全量文件 (私密频道排最后)
        with open(TOTAL_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(other_lines + private_lines))
            f.write(f"\n\n# 自动对时: {bj_time} | 当前端口: {new_port}")

        # 写入纯私密文件
        if private_lines:
            with open(PRIVATE_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(private_lines))
                f.write(f"\n# 更新时间: {bj_time}")

        print(f"Success! Port {new_port} at {bj_time}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_files()
