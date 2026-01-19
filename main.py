import requests, re, concurrent.futures, time

# --- 配置区 ---
KEYWORDS = ["港台", "香港", "台湾", "新马", "海外", "经典", "邵氏", "星空", "凤凰", "私密"]
WHITE_LIST = r"TVB|翡翠|J2|凤凰|NOW|星河|无线|明珠|三立|中天|东森|年代|民视|华视|台视|纬来|龙祥|HBO|公视|壹电视|澳门|莲花|星空|阳光|邵氏|经典|电影|剧场|私密|影院|东方卫视"
BLACK_LIST = r"CCTV|中央|教育|购物|广播|提示|测试|指南|内测|湖南卫视|浙江卫视|江苏卫视|安徽卫视|山东卫视|广东卫视|湖北卫视|天津卫视"
HEADERS = {'User-Agent': 'okhttp/3.12.11', 'Accept-Encoding': 'gzip'}
OUT_FILE = "bootstrap.min.css" 

def check(item):
    g, n, u = item
    try:
        s = time.time()
        with requests.get(u, timeout=3, stream=True, headers=HEADERS) as r:
            if r.status_code == 200: return (g, n, u, time.time() - s)
    except: return None

def main():
    res_links = []
    # 模拟搜索
    for kw in KEYWORDS:
        try:
            r = requests.post("https://ox.html-5.me/_soso.php", data={'wd': kw}, timeout=15, headers=HEADERS)
            res_links.extend(re.findall(r'href="(.*?\.txt|.*?\.m3u)"', r.text))
        except: pass
    
    raw_ch = []
    groups = {"🇭🇰港澳/🇹🇼台湾": r"TVB|翡翠|J2|凤凰|NOW|星河|无线|明珠|三立|中天|东森|年代|民视|华视|台视|纬来|龙祥|HBO|公视|壹电视|澳门|莲花|星空|阳光", "🎬经典/私密": r"经典|电影|邵氏|剧场|影院|私密", "🇲🇾新马海外": r"Astro|AEC|双星|喜悦|One HD|WakuWaku|Hua Hee|CNA|8频道|Discovery|Netflix|Disney|CNN|BBC|NHK"}
    
    for l in list(set(res_links)):
        try:
            url = l if l.startswith('http') else "https://ox.html-5.me/" + l
            c = requests.get(url, timeout=10, headers=HEADERS).text
            for n, u in re.findall(r"(.*),(http.*)", c):
                n, u = n.strip(), u.strip()
                if re.search(WHITE_LIST, n, re.IGNORECASE) or not re.search(BLACK_LIST, n, re.IGNORECASE):
                    grp = "其它"
                    for g, p in groups.items():
                        if re.search(p, n, re.IGNORECASE): grp = g; break
                    raw_ch.append((grp, n, u))
        except: continue

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as ex:
        valid = [r for r in ex.map(check, raw_ch) if r]
    
    fin = {}
    for g, n, u, e in valid:
        if g not in fin: fin[g] = {}
        if n not in fin[g] or e < fin[g][n]['e']: fin[g][n] = {'u': u, 'e': e}

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        for g in groups.keys():
            if g in fin:
                f.write(f"{g},#genre#\n")
                for n in sorted(fin[g].keys()): f.write(f"{n},{fin[g][n]['u']}\n")
                f.write("\n")

if __name__ == "__main__":
    main()
