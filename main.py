import asyncio
import re
from playwright.async_api import async_playwright

# ================= 核心配置区 =================
# 1. 你的专属关键词（包含 Emoji 完美支持）
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
# 2. 扫描深度：自动抓取首页最新 ID 并往前扫 80 个文件，确保不漏掉任何“货”
SCAN_DEPTH = 80 
OUT_FILE = "bootstrap.min.css"
# =============================================

async def fetch_content(context, file_id):
    url = f"https://ox.html-5.me/i/{file_id}.txt"
    page = await context.new_page()
    results = []
    try:
        # 模拟真实操作：打开页面 -> 等待 JS 验证 -> 提取文本
        await page.goto(url, wait_until="networkidle", timeout=25000)
        content = await page.inner_text("body")
        if content and "," in content:
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if ',' in line and 'http' in line:
                    # 只要名字里包含你给的任何一个关键词（包括符号）
                    if any(kw in line for kw in KEYWORDS):
                        results.append(line)
    except:
        pass
    finally:
        await page.close()
    return results

async def main():
    print("🚀 启动 Chromium 模拟浏览器...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 模拟真实的手机环境，绕过检测
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        
        # 1. 自动定位最新 ID
        page = await context.new_page()
        await page.goto("https://ox.html-5.me/", wait_until="networkidle")
        html = await page.content()
        ids = sorted(list(set(re.findall(r'/i/(\d+)\.txt', html))), reverse=True)
        latest_id = int(ids[0]) if ids else 8732100
        await page.close()

        print(f"📡 发现最新 ID: {latest_id}，正在执行全自动扫荡...")

        # 2. 并发扫描：从最新 ID 往前推 SCAN_DEPTH 个
        tasks = [fetch_content(context, i) for i in range(latest_id - SCAN_DEPTH, latest_id + 2)]
        gathered_results = await asyncio.gather(*tasks)
        
        # 3. 数据汇总与去重
        all_found = set()
        for res_list in gathered_results:
            for item in res_list:
                all_found.add(item)

        # 4. 自动分组逻辑
        categories = {kw: [] for kw in KEYWORDS}
        categories["其他资源"] = []

        for item in all_found:
            added = False
            for kw in KEYWORDS:
                if kw in item:
                    categories[kw].append(item)
                    added = True
                    break
            if not added:
                categories["其他资源"].append(item)

        # 5. 写入仓库文件 (格式完全兼容 OK 壳子)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            for cat, items in categories.items():
                if items:
                    f.write(f"{cat},#genre#\n")
                    for line in sorted(items):
                        f.write(f"{line}\n")
        
        await browser.close()
        print(f"✅ 任务结束！共捕获并验证 {len(all_found)} 条资源。")

if __name__ == "__main__":
    asyncio.run(main())
