import os
import asyncio
import gzip
import json
from lista_videos import videos, curso, videos_listados
from playwright.async_api import async_playwright
from pathlib import Path


VIDEO_URL = videos[0][2]

# Cria uma pasta local para simular o cache e cookies de um usuário real
USER_DATA_DIR = os.path.join(os.getcwd(), "perfildoplaywright")

def procurar_legendas(obj):

    if isinstance(obj, dict):

        if "transcriptSegmentRenderer" in obj:

            seg = obj["transcriptSegmentRenderer"]

            timestamp = (
                seg.get("startTimeText", "")
                   .get("simpleText")
            )

            texto = " ".join(
                run.get("text", "")
                for run in seg.get("snippet", {}).get("runs", [])
            )

            print(f"[{timestamp}] {texto}")

        for valor in obj.values():
            procurar_legendas(valor)
    
    elif isinstance(obj, list):

        for item in obj:
            procurar_legendas(item)

async def main():

    async with async_playwright() as p:

        # browser = await p.chromium.launch(
        #     headless=False
        # )

        # page = await browser.new_page()

        # Em vez de launch + new_context, usamos launch_persistent_context
        # Isso simula perfeitamente o comportamento do seu Chrome comum
        context = await p.chromium.launch_persistent_context(
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

        # Pega a primeira aba padrão do contexto persistente        
        if context.pages:
            page = context.pages[0]
        else:
            page = await context.new_page()
 
        # Injeta um script oculto para camuflar o Playwright antes da página carregar
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")        

        async def capturar_response(response):

            if "youtubei" in response.url:
                print(response.url)               

            if "youtubei/v1/get_transcript" not in response.url:
                return

            print("\nGET_TRANSCRIPT REQUEST")
            print(response.url)

            try:

                headers = response.headers

                print("\nHEADERS:")
                print(headers)

                body = await response.body()

                print("\nBODY SIZE:")
                print(len(body))

                if headers.get("content-encoding") == "gzip":

                    print("\nDESCOMPACTANDO GZIP...")

                    body = gzip.decompress(body)

                texto = body.decode("utf-8")

                print("\nINÍCIO DO JSON:")
                # print(texto[:3000])
                dados = json.loads(texto)
                
                # define o diretório atual para salvar o arquivo
                arquivo_saida = (
                    Path(__file__).parent /
                    "body_5_2.json"
                )                    
                # Salva body em arquivo                
                # Forma moderna
                arquivo_saida.write_text(
                    json.dumps(
                        dados,
                        ensure_ascii=False,
                        indent=2
                    ),
                    encoding="utf-8" 
                )                   

                procurar_legendas(dados)

            except Exception as e:

                print("\nERRO")
                print(type(e).__name__)
                print(str(e))

        page.on("response", capturar_response)

        await page.goto(
            VIDEO_URL,
            wait_until="networkidle"
        )

        print("\nAbra a transcrição do vídeo")
        print("Aguarde alguns segundos.")
        print("Depois pressione ENTER.")

        input()

        await asyncio.sleep(10)

        await context.close()

asyncio.run(main())