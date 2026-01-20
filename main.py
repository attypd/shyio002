import asyncio, re, datetime
from playwright.async_api import async_playwright

# 严格匹配你视频中的关键词
KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 1. 模拟真实手机浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            try:
                print(f"📡 模拟真实输入搜索: {kw}")
                await page.goto("https://ox.html-5.me/", timeout=60000)
                
                # 定位输入框并填入文字
                search_input = page.locator('input[name="keyword"]')
                await search_input.fill(kw)
                
                # 【关键点】：模拟手机键盘“回车”
                await search_input.press("Enter")
                
                # 【核心修复】：视频里结果加载需要时间。
                # 必须等待页面上出现 "/i/数字.txt" 的链接才继续，最多等 30 秒。
                try:
                    await page.wait_for_selector('a[href*="/i/"]', timeout=30000)
                except:
                    print(f"⚠️ [{kw}] 搜索超时，可能未加载出结果")
                
                # 抓取所有 ID
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
                all_ids.update(ids)
                print(f"✅ [{kw}] 成功提取到 {len(ids)} 个 ID")
            except Exception as e:
                print(f"❌ [{kw}] 出错: {e}")

        final_sources = []
        # 2. 穿透抓取真实链接（支持关键词符合）
        for fid in all_ids:
            try:
                p_sub = await context.new_page()
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                raw_text = await p_sub.inner_text("body")
                for line in raw_text.split('\n'):
                    # 必须支持关键词符合且包含 http
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_sources.append(line.strip())
                await p_sub.close()
            except: continue

        # 3. 强制生成 TXT 格式分组
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"🎬 同步时间：{now_str} - 总计{len(final_sources)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_sources if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n") # OK 影视壳子分类格式
                    for item in sorted(list(set(group))):
                        f.write(f"{item}\n")
        
        await browser.close()
        print(f"🏁 任务完成！文件 {OUT_FILE} 已生成。")

if __name__ == "__main__":
    asyncio.run(main())
