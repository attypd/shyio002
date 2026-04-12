import socket
import concurrent.futures
import random
import re
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
# 定义母版文件（只读，不修改）
SOURCE_TEMPLATE = "cvs_mylive.txt" 
# 定义输出的目标文件（每次扫描后根据母版重新生成）
TARGET_FILES = ["total_live.txt", "private_only.txt"]

def check_port(port):
    """保持原有逻辑：TCP 握手探测"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.7) # 如果还是扫不到，建议把这里改成 1.5
            if s.connect_ex((DOMAIN, int(port))) == 0:
                return str(port)
    except:
        pass
    return None

def run_scanner(port_list):
    """保持原有逻辑：120 线程并发"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=120) as executor:
        future_to_port = {executor.submit(check_port, p): p for p in port_list}
        for future in concurrent.futures.as_completed(future_to_port):
            result = future.result()
            if result:
                # 扫到一个活的就立刻关掉其他线程，返回结果
                executor.shutdown(wait=False, cancel_futures=True)
                return result
    return None

def get_latest_port():
    """严格保持原有的三阶段扫描范围，不弄乱顺序"""
    print(f"Scanning {DOMAIN} across all ranges...")
    
    # Stage 1: 核心活跃区 (40000 - 50000)
    res = run_scanner(list(range(40000, 50001)))
    if res: return res
    
    # Stage 2: 扩展随机区 (30000-40000 & 50001-65535)
    reg_list = list(range(30000, 40000)) + list(range(50001, 65536))
    random.shuffle(reg_list)
    res = run_scanner(reg_list)
    if res: return res
    
    # Stage 3: 低段位存量区 (8000 - 30000)
    res = run_scanner(list(range(8000, 30001)))
    return res if res else "8888" # 全灭则返回默认保底端口

def update_files():
    """关键微调：从母版读取，写入目标"""
    active_port = get_latest_port()
    sync_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    print(f"Success! Port: {active_port} | Sync Time: {sync_time}")

    try:
        # 1. 读取母版内容
        with open(SOURCE_TEMPLATE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 2. 生成替换端口后的新内容
        new_lines = []
        pattern = rf"({re.escape(DOMAIN)}):(\d+)"
        replacement = f"\\1:{active_port}"
        
        for line in lines:
            # 只要匹配到域名:端口，就换成新的
            new_lines.append(re.sub(pattern, replacement, line))

        # 3. 覆盖写入到目标文件
        for file_path in TARGET_FILES:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Updated from template: {file_path}")

    except FileNotFoundError:
        print(f"Error: {SOURCE_TEMPLATE} not found.")
    except Exception as e:
        print(f"Update failed: {e}")

if __name__ == "__main__":
    update_files()
