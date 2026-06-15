from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright
import json

VIDEO_URL = videos[0][2]

def response_listener(response):

    url = response.url

    if "get_panel" not in url:
        return
    
    print("\nGET_PANEL ENCONTRADO")
    print(url)

    try:

        data = response.json()

        with open(
            "get_panel.json",
            "w",
            encoding="uft-8"
        ) as f:
            
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )
        
        print("ERRO:", e)

    except Exception as e:
        print("ERRO:", e)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.on(
        "response",
        response_listener
    )




    page.goto(
        VIDEO_URL,
        wait_until="networkidle"
    )

    print(page.title())

    input("Abra a transcrição manualmente e pressione ENTER para fechar...")

    browser.close()