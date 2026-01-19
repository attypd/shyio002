import requests, re, concurrent.futures

# ================= 暴力扫荡区 =================
# 锁定你提供的核心 ID (8731996) 
TARGET_ID = 8731996 
RANGE = 100 # 范围先缩短，确保成功率

# 关键词只要包含其中一个就抓取
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞"]
# ===============================================

BASE_URL = "https://ox.html-5.me/i/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://ox.html-5.me/'
}
OUT_FILE = "bootstrap.min.css"

def scan_url(file_id):
    url = f"{BASE_URL}{file_id}.txt"
    results = []
    try:
        # 增加超时时间，防止网络抖动
        r = requests.get(url, timeout=15, headers=HEADERS)
        r.encoding = 'utf-8' # 强制 UTF-8 解决 🌞 符号识别
        
        if r.status_code == 200:
            lines = r.text.split('\n')
            for line in lines:
                if ',' in line and 'http' in line:
                    # 只要包含关键词之一，就通过
                    if any(kw in line for kw in KEYWORDS):
                        results.append(line.strip())
    except: pass
    return results

def main():
    start_id = TARGET_ID - RANGE
    end_id = TARGET_ID + RANGE
    print(f"📡 正在地毯式搜救 ID 段: {start_id} -> {end_id}")
    
    all_found = []
    # 降低并发，防止被防火墙当成攻击直接封 IP
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scan_url, i) for i in range(start_id, end_id + 1)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: all_found.extend(res)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not all_found:
            f.write(f"⚠️ 抓取失败！ID段{start_id}-{end_id}内无内容，请确认ID是否过期,#genre#\n")
        else:
            f.write(f"📺 暴力抓取成功-共{len(all_found)}条,#genre#\n")
            # 彻底去重
            unique_list = sorted(list(set(all_found)))
            for line in unique_list:
                f.write(line + "\n")
            
    print(f"✅ 任务结束，最终抓取数量: {len(all_found)}")

if __name__ == "__main__":
    main()
