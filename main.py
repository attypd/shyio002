import asyncio, re, datetime, random
from playwright.async_api import async_playwright

# 要素：关键词与输出文件名
KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 要素 1：安卓真机环境模拟
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Mi 11 Ultra Build/TKQ1.221114.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.163 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        
        # 要素 2：使用公共跳板 wsrv.nl 强行穿透
        # 这种方式可以让网站以为是该代理服务器在访问，从而绕过对 GitHub IP 的封锁
        target_url = "https://ox.html-5.me/"
        proxy_bridge = f"https://wsrv.nl/?url={target_url}&output=rich"
        
        try:
            print(f"📡 正在通过公共跳板发起穿透: {target_url}")
            # 设置极长等待时间，防止再次 Timeout
            await page.goto(proxy_bridge, timeout=120000, wait_until="commit")
            await asyncio.sleep(20) # 给够 20 秒让跳板加载网页内容
            
            content = await page.content()
            # 提取 /i/数字.txt
                    # 优化后的提取规则：同时抓取多种可能的链接格式
        ids = re.findall(r'i/(\d+)\.txt', content) 
        if not ids:
            # 备选规则：直接抓取 数字.txt
            ids = re.findall(r'(\d+)\.txt', content)
            
        all_ids.update(ids)
        print(f"✅ 穿透成功！提取到 {len(all_ids)} 个资源链接")

            print(f"✅ 穿透成功！提取到 {len(ids)} 个资源链接")
            
        except Exception as e:
            print(f"❌ 跳板访问也超时了: {e}")

        # 要素 3：深度数据提取
        final_list = []
        id_queue = list(all_ids)[:50] # 缩小范围，确保不超时
        
        for i, fid in enumerate(id_queue):
            try:
                # 减速避雷
                await asyncio.sleep(random.uniform(3, 6))
                p_sub = await context.new_page()
                # 详情页也走跳板
                sub_url = f"https://ox.html-5.me/i/{fid}.txt"
                await p_sub.goto(f"https://wsrv.nl/?url={sub_url}", timeout=40000)
                text = await p_sub.inner_text("body")
                
                for line in text.split('\n'):
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                await p_sub.close()
                if i % 10 == 0: print(f"📊 进度: {i}/{len(id_queue)}")
            except: continue

        # 要素 4：结果持久化
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            count = len(final_list)
            f.write(f"🎬 终极穿透同步：{now} - 资源:{count}条,#genre#\n")
            if count > 0:
                for kw in KEYWORDS:
                    group = [l for l in final_list if kw in l]
                    if group:
                        f.write(f"{kw},#genre#\n")
                        for item in sorted(list(set(group))):
                            f.write(f"{item}\n")
            else:
                f.write("⚠️ 跳板已被识别，请明天再试,#genre#\n")
        
        await browser.close()
        print(f"🏁 任务圆满结束。")

if __name__ == "__main__":
    asyncio.run(main())
