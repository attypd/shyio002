import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"   # 仓库内原始标准分组格式文件
TOTAL_FILE = "total_live.txt"     # 全量文件（自动对时，私密在后）
PRIVATE_FILE = "private_only.txt"  # 仅私密频道

def check_port(port):
    """判定逻辑：根据截图显示返回 302 即为有效端口"""
    # 路径匹配截图中的 /iptv//login3.php
    test_url = f"http://{DOMAIN}:{port}/iptv//login3.php"
    headers = {
        'accept': '*/*',
        'user-agent': 'MSIE',
        'connection': 'Keep-Alive'
    }
    try:
        # 使用 2.0s 超时，只要 302 就判定成功
        res = requests.head(test_url, headers=headers, timeout=2.0, allow_redirects=False)
        if res.status_code == 302:
            return str(port)
    except:
        return None
    return None

def scan_worker(port_list):
    """并行扫描函数"""
    random.shuffle(port_list)
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
        results = executor.map(check_port, port_list)
        for r in results:
            if r: return r
    return None

def get_latest_port():
    """扩大后的扫描逻辑"""
    # 1. 优先尝试已知的高频端口
    priority_ports = [48559, 48867]
    for p in priority_ports:
        if check_port(p): return str(p)

    # 2. 核心扫描范围：40000 - 50000
    res = scan_worker(list(range(40000, 50001)))
    if res: return res

    # 3. 扩大的全量扫描范围：20000 - 65535
    print("Expanding scan range to full...")
    res = scan_worker(list(range(20000, 40000)) + list(range(50001, 65536)))
    return res if res else "48559"

def update_files():
    new_port = get_latest_port()
    # 自动对时：获取北京时间
    bj_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    other_lines = []
    private_lines = []
    is_private_group = False

    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line: continue

            # --- 关键修改：只替换 url.cdnhs.store 的源，别的不替换 ---
            if DOMAIN in line:
                # 使用正则仅替换该域名的端口部分
                updated_line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{new_port}', line)
            else:
                # 其他备用源（如固定IP、本地源等）直接保留，不作改动
                updated_line = line

            # 分组识别：确保格式正确，私密在后
            if "#genre#" in updated_line:
                is_private_group = "私密频道" in updated_line
            
            if is_private_group:
                private_lines.append(updated_line)
            else:
                other_lines.append(updated_line)

        # 写入全量文件并记录对时信息
        with open(TOTAL_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(other_lines + private_lines))
            f.write(f"\n\n# 自动更新对时: {bj_time} | 端口: {new_port}")

        # 独立生成私密频道文件
        if private_lines:
            with open(PRIVATE_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(private_lines))
                f.write(f"\n# 更新时间: {bj_time}")

        print(f"Success! Port: {new_port} at {bj_time}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_files()
