import asyncio
from playwright.async_api import async_playwright
import re

# ================= 你的专属需求 =================
# 只要名字里带这些符号或词，一律抓取
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "🌞", "💎", "邵氏", "电影", "一本道"]
OUT_FILE = "bootstrap.min.css"
# ===============================================

async def get_latest_id(page):
    """去首页看一眼，现在更新到几号了"""
    try:
        await page.goto("https://ox.html-5.me/", wait_until="networkidle")
        html = await page.content()
        ids = re.findall(r'/i/(\d+)\.txt', html)
        return max(map(int, ids)) if ids else 8731996
    except:
        return 8731996

async def fetch_content(context, file_id):
    """穿透防火墙读取具体内容"""
    url = f"https://ox.html-5.me/i/{file_id}.txt"
    page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=20000)
        return await page.inner_text("body")
    except:
        return ""
    finally:
        await page.close()

async def main():
    print("🚀 启动浏览器，开始全自动巡逻...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)")
        
        # 1. 找最新编号
        init_page = await context.new_page()
        latest_id = await get_latest_id(init_page)
        await init_page.close()
        
        print(f"📡 发现最新编号: {latest_id}，正在自动扫荡附近资源...")

        # 2. 自动扫荡最新编号及之前的 30 个文件，确保不漏掉任何新出的 🌞
        tasks = [fetch_content(context, i) for i in range(latest_id - 30, latest_id + 1)]
        results = await asyncio.gather(*tasks)
        
        # 3. 提取、分拣、去重
        all_found = set()
        for content in results:
            if content and "," in content:
                for line in content.split('\n'):
                    if any(kw in line for kw in KEYWORDS) and "http" in line:
                        all_found.add(line.strip())

        # 4. 写入仓库
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            if not all_found:
                f.write("⚠️ 今日未发现匹配资源,#genre#\n")
            else:
                f.write(f"📺 自动更新-精选源[共{len(all_found)}个],#genre#\n")
                for item in sorted(list(all_found)):
                    f.write(item + "\n")
        
        await browser.close()
        print(f"✅ 任务彻底完成！自动抓取了 {len(all_found)} 条资源。")

if __name__ == "__main__":
    asyncio.run(main())
