from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright

# Só mostra a transcrição em vídeos listados!!
VIDEO_URL = videos[0][2]

with sync_playwright() as p:

    # 1. REMOVE A FLAG DE AUTOMAÇÃO: Evita que o YouTube saiba que é o Playwright
    browser = p.chromium.launch(    
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized" # Abre a tela cheia para evitar bugs de layout do YT
        ]
    )

    # 2. EMULA UM USUÁRIO REAL: Define User-Agent real, tamanho de tela e idioma correto
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        no_viewport=True, # Permite que a tela use o tamanho máximo real
        #viewport={"width": 1280, "height": 720},
        # locale="pt-BR",
        # extra_http_headers={
        #     "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        # }        
        locale="en-US",
        extra_http_headers={
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        }       
    )    

    page = context.new_page()

    # 3. ALTERA O NAVIGATOR: Limpa o rastro do webdriver via JavaScript antes de carregar a página
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print(f"Idioma do navegador: {page.evaluate('navigator.language')}")

    page.goto(
        VIDEO_URL,
        wait_until="domcontentloaded"
    )

    print(page.title())

    input("Pressione ENTER para fechar...")

    context.close()
    browser.close()
