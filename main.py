import asyncio
from playwright.async_api import async_playwright

# 锁定目标编号
TARGET_ID = 8731996 
OUT_FILE = "bootstrap.min.css"
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞", "💎"]

async def main():
    print("🚀 正在启动无头浏览器 (Chromium)...")
    async with async_playwright() as p:
        # 启动浏览器，模拟真实的手机环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = await context.new_page()

        url = f"https://ox.html-5.me/i/{TARGET_ID}.txt"
        print(f"📡 正在破盾访问: {url}")

        try:
            # 关键：等待网络空闲，确保 JS 验证通过并加载出内容
            await page.goto(url, wait_until="networkidle", timeout=60000)
            # 获取页面显示的文字
            content = await page.inner_text("body")
            
            found = []
            if content and "," in content:
                for line in content.split('\n'):
                    if any(kw in line for kw in KEYWORDS) and "http" in line:
                        found.append(line.strip())

            # 写入结果
            with open(OUT_FILE, "w", encoding="utf-8") as f:
                if not found:
                    f.write("⚠️ 浏览器已启动但未抓取到内容，请检查ID或关键词,#genre#\n")
                else:
                    f.write(f"📺 浏览器穿透提取-共{len(found)}条,#genre#\n")
                    for item in sorted(list(set(found))):
                        f.write(item + "\n")
            print(f"✅ 抓取成功：共计 {len(found)} 条资源")

        except Exception as e:
            print(f"❌ 浏览器运行出错: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
