import asyncio, re, datetime
from playwright.async_api import async_playwright

# 1. 你可以随时在这里更换关键词
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css" # 最终生成的 TXT 格式源文件

async def main():
    async with async_playwright() as p:
        # 模拟真实 iPhone 浏览器环境
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        for kw in KEYWORDS:
            try:
                print(f"🔍 正在模拟手机搜索: {kw}")
                await page.goto("https://ox.html-5.me/", wait_until="domcontentloaded", timeout=60000)
                await page.fill('input[name="keyword"]', kw)
                # 【模拟手机键盘回车】
                await page.keyboard.press("Enter")
                # 必须死等15秒，确保动态加载的 ID 列表显示出来
                await asyncio.sleep(15) 
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
                all_ids.update(ids)
                print(f"✅ 找到相关 ID: {len(ids)}个")
            except: continue

        final_sources = []
        # 穿透抓取真实链接
        for fid in all_ids:
            try:
                p_new = await context.new_page()
                await p_new.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                text = await p_new.inner_text("body")
                for line in text.split('\n'):
                    if any(k in line for k in KEYWORDS) and "http" in line:
                        final_sources.append(line.strip())
                await p_new.close()
            except: continue

        # 【强制生成新文件并正确分组】
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"🎬 自动同步时间：{now} - 共{len(final_sources)}条,#genre#\n")
            for kw in KEYWORDS:
                # 过滤出符合该关键词的分组内容
                group = [l for l in final_sources if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for item in sorted(list(set(group))):
                        f.write(f"{item}\n")
        
        await browser.close()
        print(f"🏁 任务圆满完成，文件 {OUT_FILE} 已生成。")

if __name__ == "__main__":
    asyncio.run(main())
