import requests, re, concurrent.futures

# ================= 自定义配置区 =================
# 1. 想要什么台就填什么词，支持 🌞 等符号的模糊匹配
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影"]

# 2. 扫描深度：往回扫多少个最新的编号
SCAN_DEPTH = 300 
# ===============================================

BASE_URL = "https://ox.html-5.me/i/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://ox.html-5.me/'
}
OUT_FILE = "bootstrap.min.css"

def get_latest_id():
    """自动获取该站当前最新的文件编号"""
    try:
        r = requests.get("https://ox.html-5.me/", timeout=10, headers=HEADERS)
        r.encoding = 'utf-8'
        ids = re.findall(r'href="/i/(\d+)\.txt"', r.text)
        if ids:
            return max(map(int, ids))
    except:
        pass
    return 8732100 # 备用初始编号

def scan_url(file_id, pattern):
    url = f"{BASE_URL}{file_id}.txt"
    results = []
    try:
        r = requests.get(url, timeout=5, headers=HEADERS)
        r.encoding = 'utf-8' # 强制 UTF-8 解码，解决 🌞 等特殊字符识别问题
        if r.status_code == 200 and "," in r.text:
            # 匹配 频道名,链接 (兼容所有特殊符号)
            matches = re.findall(r"([^,\n\r]+),(http[^\s\n\r]+)", r.text)
            for name, link in matches:
                name, link = name.strip(), link.strip()
                if re.search(pattern, name, re.IGNORECASE):
                    results.append(f"{name},{link}")
    except:
        pass
    return results

def main():
    latest_id = get_latest_id()
    start_id = latest_id - SCAN_DEPTH
    print(f"🚀 自动追踪起始点: {latest_id}, 深度: {SCAN_DEPTH}")
    
    pattern = "|".join(KEYWORDS)
    all_found = []

    # 并发扫描
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(scan_url, i, pattern) for i in range(start_id, latest_id + 1)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: all_found.extend(res)

    # 写入标准 TXT 格式文件
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not all_found:
            f.write("⚠️ 未扫描到有效源,#genre#\n")
        else:
            # 自动分类并按标准格式写入
            f.write("🎬 自动扫荡精选,#genre#\n")
            unique_list = sorted(list(set(all_found)))
            for line in unique_list:
                f.write(line + "\n")
            
    print(f"✅ 完成！文件已生成，共 {len(all_found)} 条源。")

if __name__ == "__main__":
    main()
