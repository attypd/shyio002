import socket
import concurrent.futures
import random
import re
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
FILE_LIST = ["total_live.txt", "private_only.txt"]

def check_port(port):
    """底层 TCP 探测，确保绕过 Web 拦截"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.8) 
            if s.connect_ex((DOMAIN, int(port))) == 0:
                return str(port)
    except:
        pass
    return None

def run_scanner(port_list):
    """并发扫描"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=120) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """三阶段快速扫描策略"""
    # Stage 1: 核心区间
    res = run_scanner(list(range(40000, 50001)))
    if res: return res

    # Stage 2: 扩展区间 (随机化)
    reg_list = list(range(30000, 40000)) + list(range(50001, 65536))
    random.shuffle(reg_list)
    res = run_scanner(reg_list)
    if res: return res

    # Stage 3: 低频区间
    res = run_scanner(list(range(8000, 30000)))
    return res if res else "48559" # 最终保底

def update_files():
    active_port = get_latest_port()
    # 修正 UTC+8 时间
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Success! Port: {active_port} | Sync Time: {sync_time}")

    for file_path in FILE_LIST:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            for line in lines:
                # 【精准替换核心】只有包含主域名的行才更新端口
                if DOMAIN in line:
                    line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line)
                new_lines.append(line)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Updated: {file_path}")
        except FileNotFoundError:
            print(f"File {file_path} not found, skipped.")

if __name__ == "__main__":
    update_files()
