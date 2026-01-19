import requests, re, concurrent.futures, time

# ================= 你的专属配置 =================
# 包含特殊字符关键词，脚本会自动处理编码
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞", "💎"]
SCAN_DEPTH = 500  # 深度增加到500，确保覆盖最近24小时
# ===============================================

BASE_URL = "https://ox.html-5.me/i/"
# 模拟极致真实的手机请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-cn',
    'Referer': 'https://ox.html-5.me/'
}
OUT_FILE = "bootstrap.min.css"

def get_latest_id():
    try:
        # 尝试从首页抓取最新编号
        r = requests.get("https://ox.html-5.me/", timeout=15, headers=HEADERS)
        r.encoding = 'utf-8'
        ids = re.findall(r'/i/(\d+)\.txt', r.text)
        if ids:
            return max(map(int, ids))
    except: pass
    return 8732100 

def scan_url(file_id, pattern):
    url = f"{BASE_URL}{file_id}.txt"
    results = []
    try:
        # 加上随机延迟防止被封
        r = requests.get(url, timeout=8, headers=HEADERS)
        # 核心：自动识别并转换所有特殊字符编码
        r.encoding = r.apparent_encoding if r.apparent_encoding else 'utf-8'
        
        content = r.text
        if r.status_code == 200 and "," in content:
            # 暴力匹配：只要符合 名字,链接 格式的全部提取
            lines = re.findall(r"([^,\n\r]+),(http[^\s\n\r]+)", content)
            for name, link in lines:
                name = name.strip()
                # 只要名字里包含关键词或特殊符号
                if any(kw in name for kw in KEYWORDS):
                    results.append(f"{name},{link.strip()}")
    except: pass
    return results

def main():
    latest_id = get_latest_id()
    start_id = latest_id - SCAN_DEPTH
    print(f"🛰️ 目标锁定：从 {start_id} 扫荡至 {latest_id}")
    
    all_found = []
    # 关键词正则
    pattern = "|".join(KEYWORDS)

    # 稍微降低并发，防止被网站防火墙拉黑
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(scan_url, i, pattern) for i in range(start_id, latest_id + 1)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res: all_found.extend(res)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not all_found:
            f.write("⚠️ 扫荡完毕但关键词未匹配，请确认网页是否有更新,#genre#\n")
            # 调试信息：把扫到的最后一个文件的第一行写进去，看看抓到啥了
            f.write(f"调试：最后扫描ID {latest_id},http://0.0.0.0\n")
        else:
            f.write(f"📺 扫荡完成-支持特殊字符[共{len(all_found)}个],#genre#\n")
            unique_list = sorted(list(set(all_found)))
            for line in unique_list:
                f.write(line + "\n")
            
    print(f"🏁 任务结束，抓取到 {len(all_found)} 条数据。")

if __name__ == "__main__":
    main()
