import requests
import concurrent.futures
import re
import random
from datetime import datetime, timedelta

# --- 配置信息 ---
DOMAIN = "url.cdnhs.store"
SOURCE_FILE = "cvs_mylive.txt"   # 原始标准分组格式文件
TOTAL_FILE = "total_live.txt"     # 输出的全量文件 (私密在后)
PRIVATE_FILE = "private_only.txt"  # 提取的私密频道文件

def check_port(port):
    """
    判定逻辑：模拟真实 OK 影视壳子，只要返回 302 即可判定为有效端口
    """
    test_url = f"http://{DOMAIN}:{port}/iptv/login3.php"
    # 模拟真实壳子的请求头 (基于您提供的抓包特征)
    headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 11; 23078RKD5C Build/TKQ1.221114.001)',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    try:
        # allow_redirects=False 确保我们能抓到 302 本身
        res = requests.head(test_url, headers=headers, timeout=3.5, allow_redirects=False)
        if res.status_code == 302:
            return str(port)
    except:
        return None
    return None

def scan_worker(port_list, desc):
    """执行特定范围的并行扫描"""
    print(f"Scanning {desc}, total ports: {len(port_list)}...")
    random.shuffle(port_list) 
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=70) as executor:
        results = executor.map(check_port, port_list)
        for r in results:
            if r: return r
    return None

def get_latest_port():
    """分层扫描策略：已移除 8080，专注 4-5 万核心区"""
    # 1. 优先尝试之前成功的已知高概率端口
    priority = [48559, 48867]
    for p in priority:
        if check_port(p): return str(p)

    # 2. 第一阶段：重点扫描 40000-50000
    res = scan_worker(list(range(40000, 50001)), "Core (40k-50k)")
    if res: return res

    # 3. 第二阶段：补漏扫描 (20000-40000 & 50001-65535)
    print("Core range failed, expanding...")
    res = scan_worker(list(range(20000, 40000)) + list(range(50001, 65536)), "Full (20k-65k)")
    return res if res else "48559"

def update_files():
    new_port = get_latest_port()
    # 自动对时：获取北京时间
    bj_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    other_sections = []   # 普通频道分组
    private_section = []  # 私密频道分组
    is_private_group = False

    try:
        with open(SOURCE_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line: continue

            # 【精准替换逻辑】只有包含目标域名的行才替换端口，绝对不碰备用源
            if DOMAIN in line:
                updated_line = re.sub(rf'({re.escape(DOMAIN)}):(\d+)', f'\\1:{new_port}', line)
            else:
                updated_line = line

            # 【分组逻辑】识别标准 TXT 分组格式
            if "#genre#" in updated_line:
                is_private_group = "私密频道" in updated_line
            
            if is_private_group:
                private_section.append(updated_line)
            else:
                other_sections.append(updated_line)

        # 1. 生成全量文件：私密频道强制放在文件最后
        with open(TOTAL_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(other_sections + private_section))
            f.write(f"\n\n# 自动更新对时: {bj_time} | 当前有效端口: {new_port}")

        # 2. 独立生成私密频道文件
        if private_section:
            with open(PRIVATE_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(private_section))
                f.write(f"\n# 更新时间: {bj_time}")

        print(f"Success! Port found: {new_port} at {bj_time}")

    except Exception as e:
        print(f"Execution failed: {e}")

if __name__ == "__main__":
    update_files()
