from playwright.sync_api import sync_playwright

VIDEO_URL = "https://www.youtube.com/watch?v=bPntels5hw8"

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto(
        VIDEO_URL,
        wait_until="networkidle"
    )

    print(page.title())

    input("Pressione ENTER para fechar...")

    browser.close()