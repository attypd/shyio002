import asyncio, re, datetime
from playwright.async_api import async_playwright

# 关键词和生成文件名
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 启动并配置模拟 iPhone
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            try:
                print(f"📡 正在模拟搜索: {kw}")
                await page.goto("https://ox.html-5.me/", timeout=60000)
                
                # 定位输入框并输入
                search_input = page.locator('input[name="keyword"]')
                await search_input.fill(kw)
                
                # 【核心】：模拟真实手机键盘的“前往/搜索”键
                await page.keyboard.press("Enter")
                
                # 【暴力等待】：这个网站在 GitHub 环境下加载慢，死等 20 秒确保 ID 刷出来
                await asyncio.sleep(20) 
                
                # 获取页面内容并提取 ID
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
                
                if ids:
                    all_ids.update(ids)
                    print(f"✅ [{kw}] 成功抓取到 {len(ids)} 个 ID")
                else:
                    print(f"⚠️ [{kw}] 页面已加载但未发现 ID，尝试二次刷新...")
            except Exception as e:
                print(f"❌ [{kw}] 搜索环节出错: {e}")

        final_data = []
        # 穿透抓取真实链接
        for fid in all_ids:
            try:
                p_sub = await context.new_page()
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                raw_text = await p_sub.inner_text("body")
                for line in raw_text.split('\n'):
                    if any(k in line for k in KEYWORDS) and "http" in line:
                        final_data.append(line.strip())
                await p_sub.close()
            except: continue

        # 强制按 TXT 壳子格式分组写入
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"🎬 自动更新: {now} - 总计{len(final_data)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_data if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for item in sorted(list(set(group))):
                        f.write(f"{item}\n")
        
        await browser.close()
        print(f"🏁 任务结束，文件 {OUT_FILE} 已写入根目录。")

if __name__ == "__main__":
    asyncio.run(main())
