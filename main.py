import asyncio, re, datetime, random
from playwright.async_api import async_playwright

# 【核心要素：你刚刚生成的专属域名】
CF_PROXY = "https://my-proxy.1747138780.workers.dev/?url="

KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 要素 1：安卓真机环境模拟 (Mi 11 Ultra)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Mi 11 Ultra Build/TKQ1.221114.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        # 要素 2：利用你的 CF 域名作为“引子”去敲门
        try:
            print(f"📡 正在尝试穿透访问: https://ox.html-5.me/")
            # 通过带参数的访问，让对方防火墙看到的是 Cloudflare 的请求轨迹
            await page.goto(CF_PROXY + "https://ox.html-5.me/", timeout=60000)
            await asyncio.sleep(15) # 关键：给够 15 秒让数据透传
            
            content = await page.content()
            ids = re.findall(r'/i/(\d+)\.txt', content)
            
            # 如果中转没抓到，立刻原地无感切换到“原生硬闯”模式
            if not ids:
                print("⚠️ 中转反馈为空，执行‘滴水不漏’原生扫描...")
                await page.goto("https://ox.html-5.me/", timeout=60000)
                await asyncio.sleep(10)
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
            
            all_ids.update(ids)
            print(f"✅ 提取阶段结束，拿到 {len(all_ids)} 个 ID")
            
        except Exception as e:
            print(f"❌ 访问异常: {e}")

        # 要素 3：深度全量分拣
        final_list = []
        id_queue = list(all_ids)[:80]
        
        for i, fid in enumerate(id_queue):
            try:
                # 每一条之间都随机停顿，防止被网站拉黑
                await asyncio.sleep(random.uniform(2, 5))
                p_sub = await context.new_page()
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=30000)
                text = await p_sub.inner_text("body")
                for line in text.split('\n'):
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                await p_sub.close()
                if i % 20 == 0: print(f"📊 进度: {i}/{len(id_queue)}")
            except: continue

        # 要素 4：写入文件 (权限已在 yml 确认正确)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            count = len(final_list)
            f.write(f"🎬 穿透同步：{now} - 资源:{count}条,#genre#\n")
            if count > 0:
                for kw in KEYWORDS:
                    group = [l for l in final_list if kw in l]
                    if group:
                        f.write(f"{kw},#genre#\n")
                        for item in sorted(list(set(group))):
                            f.write(f"{item}\n")
            else:
                f.write("⚠️ 数据依然为空,#genre#\n")
                f.write("结论：Git IP 已被该网站死封，且中转站代码未生效。\n")
        
        await browser.close()
        print(f"🏁 任务结束。")

if __name__ == "__main__":
    asyncio.run(main())
