import urllib.request
import re

# ================= 核心锁定 =================
TARGET_ID = 8731996 
KEYWORDS = ["港台", "翡翠", "凤凰", "经典", "邵氏", "私密", "一本道", "星空", "电影", "🌞", "💎"]
OUT_FILE = "bootstrap.min.css"

def fetch_content(url):
    """最原始的抓取方法，不走 requests 库，减少特征"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
        'Referer': 'https://ox.html-5.me/'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except:
        return None

def main():
    # 尝试两种协议：https 和 http，防止端口封锁
    urls = [
        f"https://ox.html-5.me/i/{TARGET_ID}.txt",
        f"http://ox.html-5.me/i/{TARGET_ID}.txt"
    ]
    
    content = None
    for url in urls:
        print(f"📡 尝试抓取: {url}")
        content = fetch_content(url)
        if content: break

    found = []
    if content:
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if ',' in line and 'http' in line:
                # 模糊匹配关键词
                if any(kw in line for kw in KEYWORDS):
                    found.append(line)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        if not found:
            # 如果真的抓不到，我把整个网页的前100个字符写进去，看看它到底回了什么鬼话
            debug_info = content[:100] if content else "NO_RESPONSE"
            f.write(f"❌ 调试失败: {debug_info},#genre#\n")
        else:
            f.write(f"🎬 强制提取成功-共{len(found)}条,#genre#\n")
            for item in sorted(list(set(found))):
                f.write(item + "\n")
    
    print(f"🏁 任务结束，捕获: {len(found)} 条")

if __name__ == "__main__":
    main()
