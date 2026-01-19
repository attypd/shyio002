import asyncio
import re
from playwright.async_api import async_playwright

# ================= 核心配置（请确认你的关键词） =================
KEYWORDS = ["🥦港台", "🇨🇳港🇭🇰台💫💫", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"
# =============================================================

async def search_and_get_ids(page, kw):
    """模拟真实浏览器：输入词 -> 按回车 -> 拿 ID"""
    try:
        # 打开首页并等待浏览器完全加载
        await page.goto("https://ox.html-5.me/", wait_until="networkidle", timeout=30000)
        
        # 定位搜索框
        search_box = page.locator('input[name="keyword"]')
        await search_box.click()
        await search_box.fill(kw)
        
        # 【关键】模拟你在手机上按下“回车键”
        await page.keyboard.press("Enter")
        
        # 等待搜索结果页面加载
        await page.wait_for_timeout(4000) 
        
        # 获取搜索后的网页内容，正则提取 /i/12345.txt 里的数字
        content = await page.content()
        ids = re.findall(r'/i/(\d+)\.txt', content)
        print(f"🔍 关键词 [{kw}] 搜到 ID 列表: {list(set(ids))}")
        return list(set(ids))
    except Exception as e:
        print(f"❌ 搜索 [{kw}] 时浏览器出错: {e}")
        return []

async def extract_content(context, file_id):
    """模拟浏览器进入具体的 TXT 页面抓取源"""
    url = f"https://ox.html-5.me/i/{file_id}.txt"
    page = await context.new_page()
    valid_data = []
    try:
        await page.goto(url, wait_until="networkidle", timeout=20000)
        text = await page.inner_text("body")
        if text:
            for line in text.split('\n'):
                line = line.strip()
                # 筛选：包含关键词且必须有链接
                if any(k in line for k in KEYWORDS) and "http" in line:
                    valid_data.append(line)
    except:
        pass
    finally:
        await page.close()
    return valid_data

async def main():
    async with async_playwright() as p:
        # 启动真实的 Chromium 浏览器
        browser = await p.chromium.launch(headless=True)
        # 模拟真实的手机环境（iPhone 13 浏览器指纹）
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        page = await context.new_page()

        all_collected_ids = set()
        for kw in KEYWORDS:
            ids = await search_and_get_ids(page, kw)
            all_collected_ids.update(ids)

        if not all_collected_ids:
            print("⚠️ 浏览器未能搜索到任何 ID，请确认关键词或网站状态。")
            await browser.close()
            return

        print(f"📡 浏览器正在批量穿透 {len(all_collected_ids)} 个文件提取直播源...")
        
        # 并发执行，节省 GitHub Actions 时间
        tasks = [extract_content(context, fid) for fid in all_collected_ids]
        results = await asyncio.gather(*tasks)

        # 汇总去重
        final_list = set()
        for r in results:
            for item in r:
                final_list.add(item)

        # 分类写入文件 (完全兼容 OK 壳子格式)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            f.write(f"🎬 真实浏览器全自动提取-共{len(final_list)}条,#genre#\n")
            for kw in KEYWORDS:
                group = [l for l in final_list if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    for line in sorted(group):
                        f.write(f"{line}\n")
        
        await browser.close()
        print(f"🏁 正事办完了！文件 {OUT_FILE} 已更新。")

if __name__ == "__main__":
    asyncio.run(main())
