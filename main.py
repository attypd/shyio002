import asyncio, re, datetime, random, os
from playwright.async_api import async_playwright

# 配置信息
KEYWORDS = ["港台", "西瓜🍉", "私密", "电报"]
OUT_FILE = "bootstrap.min.css"

async def main():
    async with async_playwright() as p:
        # 1. 模拟安卓真机环境 (小米11 Ultra)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Linux; Android 13; Mi 11 Ultra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
            viewport={'width': 390, 'height': 844}
        )
        page = await context.new_page()
        
        all_ids = set()
        
        # 2. 使用 wsrv.nl 公共跳板穿透 GitHub IP 封锁
        target_url = "https://ox.html-5.me/"
        proxy_bridge = f"https://wsrv.nl/?url={target_url}&output=rich"
        
        try:
            print(f"📡 正在启动穿透引擎访问: {target_url}")
            # 设置 120 秒超长等待，防止 Timeout
            await page.goto(proxy_bridge, timeout=120000)
            await asyncio.sleep(15) # 强制定格，等待数据加载
            
            content = await page.content()
            
            # 兼容性匹配：抓取多种可能的资源 ID 格式
            ids = re.findall(r'i/(\d+)\.txt', content)
            if not ids:
                ids = re.findall(r'(\d+)\.txt', content)
            
            all_ids.update(ids)
            print(f"✅ 提取阶段结束，成功捕获 {len(all_ids)} 个资源 ID")
            
        except Exception as e:
            print(f"❌ 穿透访问失败: {e}")

        # 3. 深度分拣数据
        final_list = []
        id_queue = list(all_ids)[:50] # 每次处理前50条，保证不超时
        
        for i, fid in enumerate(id_queue):
            try:
                # 随机减速，模拟人类行为
                await asyncio.sleep(random.uniform(2, 4))
                p_sub = await context.new_page()
                sub_url = f"https://ox.html-5.me/i/{fid}.txt"
                # 详情页同样走跳板
                await p_sub.goto(f"https://wsrv.nl/?url={sub_url}", timeout=40000)
                text = await p_sub.inner_text("body")
                
                for line in text.split('\n'):
                    if "http" in line and any(k in line for k in KEYWORDS):
                        final_list.append(line.strip())
                await p_sub.close()
                if i % 10 == 0: print(f"📊 数据分拣进度: {i}/{len(id_queue)}")
            except: continue

        # 4. 结果保存（含自动创建文件逻辑，防止报错）
        try:
            # 如果文件不存在则创建
            if not os.path.exists(OUT_FILE):
                with open(OUT_FILE, 'w', encoding='utf-8') as f:
                    pass
            
            with open(OUT_FILE, "w", encoding="utf-8") as f:
                now = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d %H:%M')
                count = len(final_list)
                f.write(f"🎬 终极同步：{now} - 捕获:{count}条,#genre#\n")
                if count > 0:
                    for kw in KEYWORDS:
                        group = [l for l in final_list if kw in l]
                        if group:
                            f.write(f"{kw},#genre#\n")
                            for item in sorted(list(set(group))):
                                f.write(f"{item}\n")
                else:
                    f.write("⚠️ 本次抓取为空，可能是跳板暂时失效,#genre#\n")
            print(f"💾 文件 {OUT_FILE} 已成功保存。")
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
        
        await browser.close()
        print(f"🏁 机器人任务圆满完成。")

if __name__ == "__main__":
    asyncio.run(main())
