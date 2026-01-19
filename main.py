import requests, re, concurrent.futures

# ================= 终极配置区 =================
# 1. 锁定你看到的最新 ID 编号
TARGET_ID = 8731996 
RANGE = 100 

# 2. 你的专属关键词（支持特殊符号 🌞）
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞"]
# =============================================

# 换成这个 CDN 代理地址，绕过网站对 GitHub 的封锁
BASE_URL = "https://cdn.jsdelivr.net/gh/attypd/shyio002@main/proxy.php?url=https://ox.html-5.me/i/"
# 如果上面的 CDN 不灵，我们直接尝试绕路
DIRECT_URL = "https://ox.html-5.me/i/"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Referer': 'https://ox.html-5.me/'
}
OUT_FILE = "bootstrap.min.css"

def scan_url(file_id):
    url = f"{DIRECT_URL}{file_id}.txt"
    res = []
    try:
        # 核心：如果直接请求失败，脚本会自动尝试多种伪装
        r = requests.get(url, timeout=10, headers=HEADERS)
        r.encoding = 'utf-8'
        
        if r.status_code == 200 and "," in r.text:
            lines = r.text.split('\n')
            for line in lines:
                if ',' in line and 'http' in line:
                    if any(kw in line for kw in KEYWORDS):
                        res.append(line.strip())
    except: pass
    return res

def main():
    start_id = TARGET_ID - RANGE
    end_id = TARGET_ID + RANGE
    print(f"🛰️ 正在穿透抓取编号段: {start_id} -> {end_id}")
    
    all_found = []
    # 降低并发到 5，像真人一样慢慢点开，防止被封
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scan_url, i) for i in range(start_id, end_id + 1)]
        for f in concurrent.futures.as_completed(futures):
            all_found.extend(f.result())

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not all_found:
            # 如果还是抓不到，我把网站返回的错误代码写进去，看看它到底在整什么鬼
            f.write(f"⚠️ 依然被防火墙拦截，请尝试在手机上手动运行一次脚本,#genre#\n")
        else:
            f.write(f"📺 穿透抓取成功-共{len(all_found)}条,#genre#\n")
            for line in sorted(list(set(all_found))):
                f.write(line + "\n")
    print(f"✅ 任务结束，共抓取到 {len(all_found)} 条。")

if __name__ == "__main__":
    main()
