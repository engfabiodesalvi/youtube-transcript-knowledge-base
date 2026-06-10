from playwright.sync_api import sync_playwright

VIDEO_URL = "https://www.youtube.com/watch?v=bPntels5hw8"


def response_listener(response):

    url = response.url

    if "get_panel" in url:
        print("\nGET_PANEL ENCONTRADO")
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