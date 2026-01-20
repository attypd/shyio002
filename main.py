import asyncio, re, datetime
from playwright.async_api import async_playwright

KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 严格模拟 iPhone 浏览器特征
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            try:
                print(f"📡 模拟真人操作搜索: {kw}")
                await page.goto("https://ox.html-5.me/", timeout=60000)
                
                # 1. 物理点击输入框，获取焦点
                input_selector = 'input[name="keyword"]'
                await page.click(input_selector)
                
                # 2. 像真人一样一个个字母敲进去
                await page.type(input_selector, kw, delay=100)
                
                # 3. 三重触发搜索：先按回车
                await page.keyboard.press("Enter")
                await asyncio.sleep(2)
                
                # 4. 暴力点击放大镜图标（针对有些网页不吃回车的问题）
                # 自动寻找包含搜索图标的按钮
                search_btn = page.locator('button[type="submit"], i.fa-search, .input-group-addon')
                if await search_btn.count() > 0:
                    await search_btn.first.click()
                
                # 5. 延长等待：录屏显示动态加载需要时间，死等 20 秒
                await asyncio.sleep(20) 
                
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
                if ids:
                    all_ids.update(ids)
                    print(f"✅ [{kw}] 成功抓取 ID: {len(ids)} 个")
            except Exception as e:
                print(f"❌ [{kw}] 失败: {e}")

        # --- 以下抓取内容逻辑不变 ---
        final_list = []
        for fid in all_ids:
            try:
                p_sub = await context.new_page()
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                text = await p_sub.inner_text("body")
                for line in text.split('\n'):
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                await p_sub.close()
            except: continue

        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"🎬 自动更新：{now} - 共{len(final_list)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_list if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for item in sorted(list(set(group))):
                        f.write(f"{item}\n")
        
        await browser.close()
        print(f"🏁 任务结束，请检查首页文件。")

if __name__ == "__main__":
    asyncio.run(main())
