import asyncio
import re
import datetime
from playwright.async_api import async_playwright

# 配置信息
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def search_task(page, kw):
    try:
        # 模拟进入首页
        await page.goto("https://ox.html-5.me/", wait_until="domcontentloaded", timeout=60000)
        # 定位并填写搜索框
        search_box = page.locator('input[name="keyword"]')
        await search_box.fill(kw)
        # 核心动作：模拟手机按下回车
        await page.keyboard.press("Enter")
        # 必须死等10秒，让搜索结果出来
        await asyncio.sleep(10) 
        # 提取结果ID
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
        # 启动浏览器并模拟手机指纹
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)")
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            ids = await search_task(page, kw)
            all_ids.update(ids)
            
        if not all_ids:
            print("🛑 未搜到ID，停止更新。")
            await browser.close()
            return

        tasks = [get_content(context, fid) for fid in all_ids]
        extracted_data = await asyncio.gather(*tasks)
        final_sources = {line for res in extracted_data for line in res}
        
        # 写入文件
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"🎬 自动更新时间: {now} - 共{len(final_sources)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_sources if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for line in sorted(group): f.write(f"{line}\n")
        
        await browser.close()
        print(f"✅ 完成！生成文件 {OUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
