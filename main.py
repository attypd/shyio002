import asyncio
import re
import datetime
from playwright.async_api import async_playwright

# 关键词和生成的文件名
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def search_task(page, kw):
    try:
        await page.goto("https://ox.html-5.me/", wait_until="domcontentloaded", timeout=60000)
        search_input = page.locator('input[name="keyword"]')
        await search_input.click()
        await search_input.fill(kw)
        await page.keyboard.press("Enter")
        # 强制等待10秒加载结果
        await asyncio.sleep(10) 
        content = await page.content()
        ids = re.findall(r'/i/(\d+)\.txt', content)
        return list(set(ids))
    except: return []

async def get_content(context, fid):
    page = await context.new_page()
    results = []
    try:
        await page.goto(f"https://ox.html-5.me/i/{fid}.txt", wait_until="networkidle", timeout=30000)
        text = await page.inner_text("body")
        if text:
            for line in text.split('\n'):
                if any(k in line for k in KEYWORDS) and "http" in line:
                    results.append(line.strip())
    except: pass
    finally: await page.close()
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)")
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            ids = await search_task(page, kw)
            all_ids.update(ids)
            
        if not all_ids:
            print("🛑 未搜到任何ID，请检查网站或关键词")
            await browser.close()
            return

        tasks = [get_content(context, fid) for fid in all_ids]
        extracted_data = await asyncio.gather(*tasks)
        final_sources = {line for res in extracted_data for line in res}
        
        # 写入文件，开头增加时间戳确保Git能发现变化
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"🎬 自动分拣 - 更新时间: {now} - 共{len(final_sources)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_sources if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for line in sorted(group): f.write(f"{line}\n")
        
        await browser.close()
        print(f"✅ 成功提取 {len(final_sources)} 条源，文件已生成。")

if __name__ == "__main__":
    asyncio.run(main())
