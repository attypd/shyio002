import requests, re, concurrent.futures

# ================= 强制扫荡区 =================
# 直接锁定你提供的关键 ID 段，不让脚本乱跑
TARGET_ID = 8731996 
# 往前扫 200，往后扫 200，全覆盖 400 个文件
RANGE = 200 

# 关键词列表，强制支持特殊符号 🌞 解码
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞", "💎"]
# ===============================================

BASE_URL = "https://ox.html-5.me/i/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1',
    'Referer': 'https://ox.html-5.me/'
}
OUT_FILE = "bootstrap.min.css"

def scan_url(file_id, pattern_list):
    url = f"{BASE_URL}{file_id}.txt"
    results = []
    try:
        r = requests.get(url, timeout=8, headers=HEADERS)
        # 核心：精准识别 🌞 等特殊字符，不乱码
        r.encoding = r.apparent_encoding if r.apparent_encoding else 'utf-8'
        
        if r.status_code == 200 and "," in r.text:
            # 暴力正则提取：不限格式，只要符合 名字,链接
            matches = re.findall(r"([^,\n\r]+),(http[^\s\n\r]+)", r.text)
            for name, link in matches:
                name = name.strip()
                # 检查名字里是否包含任意一个关键词
                if any(kw in name for kw in pattern_list):
                    results.append(f"{name},{link.strip()}")
    except:
        pass
    return results

def main():
    start_id = TARGET_ID - RANGE
    end_id = TARGET_ID + RANGE
    print(f"🎯 强制锁定扫荡：{start_id} ---> {end_id}")
    
    all_found = []

    # 开启 50 个线程疯狂扫货
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(scan_url, i, KEYWORDS) for i in range(start_id, end_id + 1)]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                all_found.extend(res)

    # 写入标准的直播源 TXT 格式
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not all_found:
            f.write(f"⚠️ 扫荡完毕，但在 ID {start_id}-{end_id} 范围内未匹配到关键词内容,#genre#\n")
        else:
            f.write(f"📺 提取成功[共{len(all_found)}个源],#genre#\n")
            # 去重并排序，保持文件整洁
            unique_list = sorted(list(set(all_found)))
            for line in unique_list:
                f.write(line + "\n")
            
    print(f"✅ 任务完成！扫荡了 401 个文件，共抓取到 {len(all_found)} 条你要的资源。")

if __name__ == "__main__":
    main()
