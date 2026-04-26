from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import json
import re
import random
import time
 
load_dotenv("cookies.env")
 
INSTAGRAM_USER = "sabrinacarpenter"
MAX_POSTS = 10
 
 
def esperar(min_s: float, max_s: float):
    duracion = random.uniform(min_s, max_s)
    time.sleep(duracion)
 
 
def esperar_pagina(page, min_s=2.5, max_s=5.5):
    ms = random.randint(int(min_s * 1000), int(max_s * 1000))
    page.wait_for_timeout(ms)
 
 
def cookie(name):
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Falta variable {name}")
    return {
        "name": name.lower(),
        "value": value,
        "domain": ".instagram.com",
        "path": "/"
    }
 
 
COOKIES = [
    cookie("CSRFTOKEN"),
    cookie("DS_USER_ID"),
    cookie("SESSIONID"),
    cookie("MID"),
    cookie("IG_DID"),
    cookie("RUR")
]
 
 
def a_numero(raw: str) -> int:
    raw = raw.strip().lower()
    mult = 1
 
    if "mil" in raw:
        mult = 1_000
        raw = raw.replace("mil", "")
    elif raw.endswith("k"):
        mult = 1_000
        raw = raw[:-1]
    elif raw.endswith("m"):
        mult = 1_000_000
        raw = raw[:-1]
 
    raw = raw.strip()
 
    if "," in raw and "." not in raw:
        raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")
 
    try:
        return int(float(raw) * mult)
    except Exception:
        return 0
 
 
def parsear_meta(meta: str):
    likes = 0
    comments = 0
    fecha = ""
    caption = ""
 
    matches = re.findall(
        r'([\d.,]+\s*(?:mil|[kKmM])?)\s+'
        r'(me gusta|likes?|comentarios?|comments?)',
        meta,
        re.IGNORECASE
    )
 
    for numero, tipo in matches:
        tipo = tipo.lower()
        if "like" in tipo or "gusta" in tipo:
            likes = a_numero(numero)
        if "comment" in tipo or "coment" in tipo:
            comments = a_numero(numero)
 
    for patron in [
        r'el\s+(\d+\s+de\s+\w+\s+de\s+\d{4})',
        r'el\s+(.+?)\s*:',
        r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
        r'(\w+\s+\d{1,2},\s+\d{4})',
    ]:
        m = re.search(patron, meta, re.IGNORECASE)
        if m:
            fecha = m.group(1).strip()
            break
 
    m = re.search(r'\d{4}[^:]*:\s*"?(.+)', meta, re.DOTALL)
    if m:
        caption = m.group(1).strip().strip('"').strip()
 
    return likes, comments, fecha, caption
 
 
def obtener_posts(page, max_posts=10):
    print("Buscando posts en el perfil")
 
    try:
        page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=8000)
    except Exception:
        print("No se encontraron posts")
        print("URL actual:", page.url)
        return []
 
    links = page.evaluate(f"""
        () => {{
            const links = [];
            const seen  = new Set();
 
            const anchors = document.querySelectorAll(
                'a[href*="/p/"], a[href*="/reel/"]'
            );
 
            for (const a of anchors) {{
                const href = a.getAttribute('href').split('?')[0];
                const full = 'https://www.instagram.com' + href;
 
                if (!seen.has(full)) {{
                    seen.add(full);
                    links.push(full);
                }}
 
                if (links.length >= {max_posts}) break;
            }}
 
            return links;
        }}
    """)
 
    return list(reversed(links))
 
 
def scrapear_post(page, link):
    print("Abriendo:", link)
 
    esperar(1.2, 3.0)
 
    page.goto(link, wait_until="domcontentloaded")
 
    esperar_pagina(page, 2.0, 5.0)
 
    if "login" in page.url:
        print("Instagram te envió a login")
        raise Exception("bloqueado login")
 
    html = page.content()
    if "Try again later" in html:
        print("Instagram bloqueo temporal")
        raise Exception("bloqueo temporal")
 
    meta = page.locator('meta[name="description"]').get_attribute("content")
 
    if not meta:
        print("No se encontró meta description")
        print("URL:", page.url)
 
    likes, comments, fecha, caption = parsear_meta(meta or "")
 
    return {
        "link": link,
        "fecha": fecha,
        "likes": likes,
        "comentarios": comments,
        "descripcion": caption,
        "tipo": "reel" if "/reel/" in link else "post"
    }
 
 
with sync_playwright() as p:
 
    print("Iniciando navegador")
 
    browser = p.chromium.launch(headless=True)
 
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    )
 
    page = context.new_page()
 
    print("Abriendo Instagram")
    page.goto("https://www.instagram.com/")
 
    esperar_pagina(page, 2.5, 4.5)
 
    print("Cargando cookies")
    context.add_cookies(COOKIES)
 
    page.reload()
 
    esperar_pagina(page, 4.0, 7.0)
 
    if "login" in page.url:
        print("No se logró login con cookies")
    else:
        print("Login con cookies OK")
 
    print("Abriendo perfil")
    page.goto(f"https://www.instagram.com/{INSTAGRAM_USER}/")
 
    esperar_pagina(page, 5.0, 9.0)
 
    print("URL actual:", page.url)
 
    post_links = obtener_posts(page, MAX_POSTS)
    print("Posts encontrados:", len(post_links))
 
    data = []
 
    for i, link in enumerate(post_links, 1):
        print(f"Procesando {i} de {len(post_links)}")
 
        try:
            post = scrapear_post(page, link)
            post["numero"] = i
            data.append(post)
 
            print(
                "likes", post["likes"],
                "comentarios", post["comentarios"],
                "fecha", post["fecha"]
            )
 
        except Exception as e:
            print("Error:", e)
 
        if i % 3 == 0:
            pausa = random.uniform(6.0, 12.0)
            print(f"Pausa larga: {pausa:.1f}s")
            time.sleep(pausa)
        else:
            pausa = random.uniform(2.0, 5.0)
            print(f"Pausa corta: {pausa:.1f}s")
            time.sleep(pausa)
 
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
 
    print("Guardado en posts.json")
 
    browser.close()