from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright

VIDEO_URL = videos[0][2]


def response_listener(response):

    url = response.url

    if "get_panel" in url:
        print("\nGET_PANEL ENCONTRADO")
        print(url)

    if "youtubei" in url:
        print(url)        

    


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