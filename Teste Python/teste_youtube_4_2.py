import os
from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright
import json
import gzip

VIDEO_URL = videos[0][2]

# Cria uma pasta local para simular o cache e cookies de um usuário real
USER_DATA_DIR = os.path.join(os.getcwd(), "perfildoplaywright")

json_salvo = False

def request_listener(request):

    if "youtubei/v1/next" not in request.url:
        return

    print("\nNEXT REQUEST")
    print(request.url)

    try:

        print("\nHEADERS:")
        print(request.headers)

        print("\nPOST_DATA:")
        print(repr(request.post_data))

    except Exception as e:

        print("\nERRO")
        print(type(e).__name__)
        print(e)    

    # global json_salvo

    # if json_salvo:
    #     return
    
    # if "get_panel" not in request.url:
    #     return
    
    # print("\nGET_PANEL REQUEST")
    # print(request.url)

    # try:

    #     payload = request.post_data

    #     print(payload)

    #     with open(
    #         "payload_get_panel.json",
    #         "w",
    #         encoding="utf-8"
    #     ) as f:
            
    #         f.write(payload)

    #     json_salvo = True
        
    #     print("\nPAYLOAD SALVO")

    # except Exception as e:

    #     print("\nERRO")
    #     print(type(e).__name__)
    #     print(e)


with sync_playwright() as p:

    # Em vez de launch + new_context, usamos launch_persistent_context
    # Isso simula perfeitamente o comportamento do seu Chrome comum
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        locale="en-US",
        #locale="pt-BR",
        args=[
            "--disable-blink-features=AutomationControlled", # Esconde que é robô
            "--start-maximized" # Abre a tela cheia para evitar bugs de layout do YT
        ],
        no_viewport=True, # Permite que a tela use o tamanho máximo real
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    page = context.pages[0] # Pega a primeira aba padrão do contexto persistente

    # Injeta um script oculto para camuflar o Playwright antes da página carregar
    page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    page.on(
        "request",
        request_listener
    )

    print("Carregando o YouTube...")
    page.goto(VIDEO_URL, wait_until="domcontentloaded") # "commit" evita travar com anúncios infinitos

    print(f"Vídeo aberto: {page.title()}")
    print("Agora clique no botão de transcrição na tela. O texto vai carregar normalmente!")

    # Mantém aberto para você interagir na tela
    input("Pressione ENTER para fechar o script...")
    
    context.close()    

    # browser = p.chromium.launch(
    #     headless=False
    # )

    # page = browser.new_page()

    # page.on(
    #     "request",
    #     request_listener
    # )

    # page.goto(
    #     VIDEO_URL,
    #     wait_until="networkidle"
    # )

    # print(page.title())

    # print("\nAbra a transcrição do vídeo")
    # print("Aguarde alguns segundos.")
    
    # input("Depois pressione ENTER.")

    # browser.close()
