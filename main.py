from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import json
import re

load_dotenv("cookies.env")

INSTAGRAM_USER = "sabrinacarpenter"
MAX_POSTS = 10


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

    # coma miles 4,636
    if "," in raw and "." not in raw:
        raw = raw.replace(",", "")
    else:
        raw = raw.replace(",", ".")

    try:
        return int(float(raw) * mult)
    except:
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

    # fecha
    m = re.search(r'el\s+(.+?)\s*:', meta)
    if m:
        fecha = m.group(1).strip()

    # caption
    m = re.search(r'\d{4}:\s*"?(.+)', meta, re.DOTALL)
    if m:
        caption = m.group(1).strip().strip('"').strip()

    return likes, comments, fecha, caption

def obtener_posts(page, max_posts=10):
    page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]')

    return page.evaluate(f"""
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


def scrapear_post(page, link):
    page.goto(link, wait_until="domcontentloaded")

    meta = page.locator(
        'meta[name="description"]'
    ).get_attribute("content")

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

    browser = p.chromium.launch(headless=False)

    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    page = context.new_page()

    # login cookies
    page.goto("https://www.instagram.com/")
    page.wait_for_timeout(3000)

    context.add_cookies(COOKIES)

    page.reload()
    page.wait_for_timeout(5000)

    # abrir perfil
    page.goto(f"https://www.instagram.com/{INSTAGRAM_USER}/")
    page.wait_for_timeout(6000)

    post_links = obtener_posts(page, MAX_POSTS)

    print(f"Posts encontrados: {len(post_links)}")

    data = []

    for i, link in enumerate(post_links, 1):

        print(f"[{i}/{len(post_links)}] {link}")

        try:
            post = scrapear_post(page, link)
            post["numero"] = i
            data.append(post)

            print(
                f"  likes={post['likes']} | "
                f"comentarios={post['comentarios']} | "
                f"fecha={post['fecha']}"
            )

        except Exception as e:
            print(f"Error: {e}")

    # guardar json
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("\nGuardado en posts.json")

    browser.close()