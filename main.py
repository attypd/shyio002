import asyncio, re, datetime, random
from playwright.async_api import async_playwright

# 要素1：分拣逻辑定义
KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 要素2：硬件级环境伪装 (模拟最新的 iPhone 15 Pro 真实指纹)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            viewport={'width': 393, 'height': 852},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        page = await context.new_page()
        
        all_ids = set()
        # 要素3：绕过搜索拦截，改用“首页地毯式深爬”
        # 爬取前3页，确保覆盖你视频里所有新跳出的资源
        scan_urls = [
            "https://ox.html-5.me/",
            "https://ox.html-5.me/index.php?page=1",
            "https://ox.html-5.me/index.php?page=2"
        ]
        
        for url in scan_urls:
            try:
                # 要素4：极慢速人类模拟 (像真人一样等待加载)
                print(f"🐢 [行为模拟] 正在访问: {url}")
                await page.goto(url, timeout=120000, wait_until="networkidle")
                
                # 要素5：物理滚动模拟 (模拟手指滑屏看页面的动作)
                for _ in range(random.randint(3, 5)):
                    await page.mouse.wheel(0, random.randint(500, 1000))
                    await asyncio.sleep(random.uniform(1.5, 3.0)) # 停顿看一看
                
                content = await page.content()
                ids = re.findall(r'/i/(\d+)\.txt', content)
                all_ids.update(ids)
                print(f"✅ 提取到 {len(ids)} 个资源 ID，当前累计: {len(all_ids)}")
            except Exception as e:
                print(f"⚠️ 访问受阻，可能 Git IP 波动，跳过本页: {e}")

        # 要素6：深度链接分拣 (穿透每一条 TXT 内部)
        final_list = []
        id_queue = list(all_ids)[:150] # 优先处理最新的 150 个资源
        
        print(f"🚀 开始深度模拟分拣，预计耗时 5-10 分钟...")
        for i, fid in enumerate(id_queue):
            try:
                # 要素7：冷却与频率控制 (每隔几条强制“休息”，防止被封 IP)
                if i % 8 == 0:
                    await asyncio.sleep(random.uniform(3, 6))
                
                p_sub = await context.new_page()
                # 进入子页面抓取真实播放链接
                await p_sub.goto(f"https://ox.html-5.me/i/{fid}.txt", timeout=40000)
                text = await p_sub.inner_text("body")
                
                for line in text.split('\n'):
                    # 严格筛选：带 http 且符合关键词
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                
                await p_sub.close()
                if i % 20 == 0:
                    print(f"📊 任务进度: {i}/{len(id_queue)}...")
            except:
                continue

        # 要素8：自动化格式写入 (严格适配 OK 影视壳子)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"🎬 深度分拣同步：{now} - 资源总计:{len(final_list)}条,#genre#\n")
            
            for kw in KEYWORDS:
                group = [l for l in final_list if kw in l]
                if group:
                    f.write(f"{kw},#genre#\n")
                    # 去重、排序，保持最整洁的列表
                    for item in sorted(list(set(group))):
                        f.write(f"{item}\n")
        
        await browser.close()
        print(f"🏁 全要素任务圆满结束。")

if __name__ == "__main__":
    asyncio.run(main())
