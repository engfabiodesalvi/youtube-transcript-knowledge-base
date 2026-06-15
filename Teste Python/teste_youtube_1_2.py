import os
from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright

VIDEO_URL = videos[0][2]

# Cria uma pasta local para simular o cache e cookies de um usuário real
USER_DATA_DIR = os.path.join(os.getcwd(), "perfildoplaywright")

with sync_playwright() as p:

    # Em vez de launch + new_context, usamos launch_persistent_context
    # Isso simula perfeitamente o comportamento do seu Chrome comum
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        # locale="en-US",
        locale="pt-BR",
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

    print("Carregando o YouTube...")
    page.goto(VIDEO_URL, wait_until="commit") # "commit" evita travar com anúncios infinitos

    print(f"Vídeo aberto: {page.title()}")
    print("Agora clique no botão de transcrição na tela. O texto vai carregar normalmente!")

    # Mantém aberto para você interagir na tela
    input("Pressione ENTER para fechar o script...")
    
    context.close()