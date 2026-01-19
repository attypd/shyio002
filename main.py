import requests, re, concurrent.futures

# --- 目标地址：直接抓取该站的总库文件 ---
TARGET_URL = "https://ox.html-5.me/itvlist.txt"

# 伪装成手机浏览器，防止被拦截
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Referer': 'https://ox.html-5.me/'
}

# 你的专属关键词筛选
WHITE_LIST = r"TVB|翡翠|J2|凤凰|NOW|星河|无线|明珠|三立|中天|东森|年代|民视|华视|台视|纬来|龙祥|HBO|公视|壹电视|澳门|莲花|星空|阳光|邵氏|经典|电影|剧场|私密|影院|星耀|东方卫视"
BLACK_LIST = r"CCTV|中央|教育|购物|广播|提示|测试|指南|内测|湖南卫视|浙江卫视|江苏卫视|安徽卫视|山东卫视|广东卫视"

OUT_FILE = "bootstrap.min.css"

def check(item):
    n, u = item
    try:
        # 测速：只给2秒时间，不通的不要
        with requests.get(u, timeout=2, stream=True, headers=HEADERS) as r:
            if r.status_code == 200: return (n, u)
    except: return None

def main():
    print(f"🚀 正在连接目标网站底库: {TARGET_URL}")
    try:
        r = requests.get(TARGET_URL, timeout=30, headers=HEADERS)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            print(f"❌ 访问失败，状态码: {r.status_code}")
            return
            
        # 提取所有 频道名,链接
        all_channels = re.findall(r"(.*),(http.*)", r.text)
        print(f"📡 成功进入底库！总共包含 {len(all_channels)} 条原始数据。")
        
        # 筛选你要的内容
        filtered = []
        for n, u in all_channels:
            n, u = n.strip(), u.strip()
            if re.search(WHITE_LIST, n, re.IGNORECASE) and not re.search(BLACK_LIST, n, re.IGNORECASE):
                filtered.append((n, u))
        
        print(f"🎯 筛选出符合你要求的频道 {len(filtered)} 个，开始并行测速...")

        # 测速去重
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            valid = [res for res in executor.map(check, list(set(filtered))) if res]

        # 写入文件
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            f.write("🎬 你的专属经典港台源,#genre#\n")
            for n, u in sorted(valid):
                f.write(f"{n},{u}\n")
        
        print(f"✅ 大功告成！已为你保存在 {OUT_FILE}")

    except Exception as e:
        print(f"💥 发生错误: {e}")

if __name__ == "__main__":
    main()
