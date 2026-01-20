import requests
import concurrent.futures
import time
import re
from datetime import datetime, timedelta

# 配置
DOMAIN = "url.cdnhs.store"

def check_port(port):
    """探测端口：支持 200 和 302 重定向"""
    test_url = f"http://{DOMAIN}:{port}/mytv.php?id=3"
    try:
        # allow_redirects=False 识别 302/8080 跳转
        res = requests.head(test_url, timeout=1.5, allow_redirects=False)
        if res.status_code in [200, 302]:
            return str(port)
    except:
        return None
    return None

def get_latest_port():
    """全自动扫描端口"""
    for p in [48867, 48559, 8080]:
        if check_port(p): return str(p)
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        ports = range(40000, 50000)
        results = executor.map(check_port, ports)
        for r in results:
            if r: return r
    return "48559"

def update_files():
    new_port = get_latest_port()
    # 北京时间对时
    bj_time = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    
    total_lines = []
    private_only_lines = []
    is_private_section = False 
    
    try:
        # 严格读取你的原始 cvs_mylive.txt
        with open("cvs_mylive.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 1. 精准替换端口，不改变任何频道顺序
            updated_line = re.sub(r':\d+/', f':{new_port}/', line)
            total_lines.append(updated_line)
            
            # 2. 改进的私密频道识别逻辑
            # 只要这一行包含“私密频道”四个字，就开始提取
            if "私密频道" in updated_line:
                is_private_section = True
            
            if is_private_section:
                private_only_lines.append(updated_line)
                
    except Exception as e:
        print(f"执行失败: {e}")
        return

    # 文件 1: 全量源 (total_live.txt) - 顺序和你原始文件完全一致
    with open("total_live.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(total_lines))
        f.write(f"\n\n# 自动对时更新: {bj_time} | 当前端口: {new_port}")

    # 文件 2: 独立私密源 (private_only.txt)
    if private_only_lines:
        with open("private_only.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(private_only_lines))
            f.write(f"\n\n# 对时: {bj_time}")

    print(f"✅ 更新成功！发现端口: {new_port} | 时间: {bj_time}")

if __name__ == "__main__":
    update_files()
