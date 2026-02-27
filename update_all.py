import socket
import concurrent.futures
import random
import re
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
# 002 仓库对应的三个目标文件
FILE_LIST = ["total_live.txt", "private_only.txt"]

def check_port(port):
    """TCP 底层探测，直接绕过 Web 拦截"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.7) 
            if s.connect_ex((DOMAIN, int(port))) == 0:
                return str(port)
    except:
        pass
    return None

def run_scanner(port_list):
    """120 线程并发快速扫描"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=120) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """三阶段全频段扫描策略"""
    print(f"Scanning {DOMAIN} across all ranges...")
    
    # Stage 1: 核心活跃区 (40000 - 50000)
    res = run_scanner(list(range(40000, 50001)))
    if res: return res

    # Stage 2: 扩展随机区 (30000-40000 & 50001-65535)
    reg_list = list(range(30000, 40000)) + list(range(50001, 65536))
    random.shuffle(reg_list)
    res = run_scanner(reg_list)
    if res: return res

    # Stage 3: 低频存量区 (8000 - 30000)
    res = run_scanner(list(range(8000, 30000)))
    return res if res else "48559" # 最终保底端口

def update_files():
    active_port = get_latest_port()
    # 修正为 UTC+8 北京时间
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Success! Port: {active_port} | Sync Time: {sync_time}")

    for file_path in FILE_LIST:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 精准匹配域名行，避免修改其他直播源
            new_lines = [re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{active_port}', line) if DOMAIN in line else line for line in lines]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Updated: {file_path}")
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    update_files()
