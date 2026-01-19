import asyncio
import re
from playwright.async_api import async_playwright

# 这里的关键词只要你改了，Actions 就会自动重跑
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def search_task(page, kw):
    try:
        # 1. 模拟打开首页
        await page.goto("https://ox.html-5.me/", wait_until="networkidle", timeout=60000)
        
        # 2. 模拟填入关键词
        search_input = page.locator('input[name="keyword"]')
        await search_input.fill(kw)
        
        # 3. 模拟按下回车 (对应你图里的确认动作)
        print(f"⌨️  正在搜索关键词: {kw}")
        await page.keyboard.press("Enter")
        
        # 4. 【核心点】强制等待 10 秒！哪怕网络慢也要等结果跳出来
        await asyncio.sleep(10) 
        
        # 5. 抓取页面内容
        content = await page.content()
        ids = re.findall(r'/i/(\d+)\.txt', content)
        unique_ids = list(set(ids))
        print(f"🎯 关键词 [{kw}] 搜到 ID 列表: {unique_ids}")
        return unique_ids
    except Exception as e:
        print(f"❌ 搜索 {kw} 超时或失败: {e}")
        return []

async def get_content(context, fid):
    page = await context.new_page()
    results = []
    try:
        await page.goto(f"https://ox.html-5.me/i/{fid}.txt", wait_until="networkidle", timeout=30000)
        text = await page.inner_text("body")
        if text:
            for line in text.split('\n'):
                # 只要符合你关键词的“货”
                if any(k in line for k in KEYWORDS) and "http" in line:
                    results.append(line.strip())
    except: pass
    finally: await page.close()
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 模拟 iPhone 13 真实环境
        context = await browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)")
        page = await context.new_page()

        all_ids = set()
        for kw in KEYWORDS:
            ids = await search_task(page, kw)
            all_ids.update(ids)

        if not all_ids:
            print("⚠️ 浏览器搜索结果为空，文件将不进行更新。")
            await browser.close()
            return

        print(f"📡 正在穿透提取 {len(all_ids)} 个文件...")
        tasks = [get_content(context, fid) for fid in all_ids]
        extracted_data = await asyncio.gather(*tasks)

        final_sources = set()
        for res in extracted_data:
            for item in res: final_sources.add(item)

        # 分类保存
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"📺 真实浏览器搜索提取-共{len(final_sources)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_sources if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for line in sorted(group): f.write(f"{line}\n")
        
        await browser.close()
        print(f"✅ 任务完成！有效源已写入 {OUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
