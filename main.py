import asyncio, re, datetime, random
from playwright.async_api import async_playwright

# 要素 1：核心分拣关键词
KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 要素 2：抛弃苹果，改用安卓真机指纹 (Android 13 + Chrome)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Mi 11 Ultra Build/TKQ1.221114.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        page = await context.new_page()
        
        all_ids = set()
        
        # 要素 3：绕过搜索，直接扫描首页及分页 (防止搜索框被封 IP)
        scan_urls = ["https://ox.html-5.me/", "https://ox.html-5.me/index.php?page=1"]
        
        for url in scan_urls:
            try:
                # 要素 4：模拟安卓极慢速加载
                print(f"🤖 [安卓模拟] 正在访问: {url}")
                await page.goto(url, timeout=90000, wait_until="load")
                
                # 要素 5：人类行为模拟 —— 随机物理滑动
                for _ in range(random.randint(4, 6)):
                    scroll = random.randint(500, 900)
                    await page.mouse.wheel(0, scroll)
                    await asyncio.sleep(random.uniform(2, 4)) # 模拟滑完后看一眼
                
                content = await page.content()
                # 提取你在视频里看到的 /i/数字.txt 格式链接
                ids = re.findall(r'/i/(\d+)\.txt', content)
                all_ids.update(ids)
                print(f"✅ 成功从安卓版网页提取到 {len(ids)} 个资源 ID")
            except Exception as e:
                print(f"⚠️ 访问异常，可能 Git IP 受限: {e}")

        final_list = []
        # 要素 6：深度穿透分拣
        id_queue = list(all_ids)[:120] # 优先处理最新的 120 个
        
        print(f"🚀 开始安卓模式深度分拣，限速运行中...")
        for i, fid in enumerate(id_queue):
            try:
                # 要素 7：频率冷却 (防止被封)
                if i % 10 == 0:
                    await asyncio.sleep(random.uniform(4, 7))
                
                p_sub = await context.new_page()
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                text = await p_sub.inner_text("body")
                
                for line in text.split('\n'):
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                
                await p_sub.close()
                if i % 20 == 0:
                    print(f"📊 已处理进度: {i}/{len(id_queue)}...")
            except:
                continue

        # 要素 8：格式化写入 (严格适配 OK 壳子)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            count = len(final_list)
            f.write(f"🎬 安卓全要素更新：{now} - 资源总计:{count}条,#genre#\n")
            
            if count > 0:
                for kw in KEYWORDS:
                    group = [l for l in final_list if kw in l]
                    if group:
                        f.write(f"{kw},#genre#\n")
                        # 去重并排序
                        for item in sorted(list(set(group))):
                            f.write(f"{item}\n")
            else:
                f.write("⚠️ 数据为空,#genre#\n")
                f.write("提示：GitHub 服务器 IP 可能被该网站全段屏蔽，建议联系配置代理。\n")
        
        await browser.close()
        print(f"🏁 任务圆满结束。")

if __name__ == "__main__":
    asyncio.run(main())
