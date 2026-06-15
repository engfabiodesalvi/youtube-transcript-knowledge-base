import os
import asyncio
import gzip
import json
from lista_videos import videos, curso, videos_listados
from playwright.async_api import async_playwright
from pathlib import Path


VIDEO_URL = videos_listados[13][2]

# Cria uma pasta local para simular o cache e cookies de um usuário real
USER_DATA_DIR = os.path.join(os.getcwd(), "perfildoplaywright")

legendas = []

def procurar_legendas(obj):

    if isinstance(obj, dict):
        
        # print("---dict---")
        # print(obj)

        # Para GET_PANEL
        if "transcriptSegmentViewModel" in obj:

            seg = obj["transcriptSegmentViewModel"]

            # print("---transcriptSegmentViewModel---")
            # print(seg)            

            timestamp = seg.get("timestamp", "")
            texto_legenda = seg.get("simpleText", "")

            # print(f"[{timestamp}] {texto}")
            legendas.append({
                "timestamp": timestamp,
                "texto": texto_legenda
            })

        # Para GET_TRANSCRIPT
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

            # print(f"[{timestamp}] {texto}")       
            legendas.append({
                "timestamp": timestamp,
                "texto": texto_legenda
            })                 

        for valor in obj.values():
            # print("---dict-obj---")
            # print(valor)

            procurar_legendas(valor)
    
    elif isinstance(obj, list):

        # print("---list---")
        for item in obj:
            # print("---list item obj---")
            # print(item)

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
        await page.add_init_script("""
        Object.defineProperty(
            navigator,
            'webdriver',
            {get: () => undefined}
        );

        Object.defineProperty(
            navigator,
            'languages',
            {get: () => ['en-US','en']}
        );

        Object.defineProperty(
            navigator,
            'plugins',
            {get: () => [1,2,3,4,5]}
        );

        window.chrome = {
            runtime: {}
        };

        delete window.__playwright__;
        delete window.__pwInitScripts;
        """)                

        async def capturar_response(response):

            if ("youtubei/v1/get_panel" not in response.url
                and
                "youtubei/v1/get_transcript" not in response.url
            ):
                return
            
            # if ("youtubei/v1/next" not in response.url):
            #     return            

            print("\nGET_PANEL OR GET_TRANSCRIPT REQUEST")
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
                    "body_6.json"
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

                print(f"\nSegmentos encontrados: {len(legendas)}")

                texto_completo = " ".join(
                    item["texto"]
                    for item in legendas
                )

                print("\nPrimeiros 1000 caracteres:")
                print(texto_completo[:1000])

            except Exception as e:

                print("\nERRO")
                print(type(e).__name__)
                print(str(e))

        page.on("response", capturar_response)

        await page.goto(
            VIDEO_URL,
            wait_until="commit" # commit evita travar com anúncios infinitos
        )

        await page.wait_for_timeout(15_000)

        # botoes = await page.locator("button").all()

        # print(f"Botões encontrados: {len(botoes)}")

        # for i, botao in enumerate(botoes):

        #     try:

        #         aria = await botao.get_attribute("aria-label")
        #         texto = await botao.inner_text()

        #         if texto.strip():
        #             print(
        #                 f"{i} | aria={aria} | text={texto}"
        #                 )

        #     except: 
        #         pass


        while True:

            ad_showing = await page.evaluate("""
                document.querySelector('.ad-showing') !== null
            """)

            if not ad_showing:
                break

            print("Anúncio em execução...")
            await asyncio.sleep(1)

        print("Anúncio encerrado")

        await asyncio.sleep(15)

        # expandir a descrição
        try:
            # await page.locator("tp-yt-paper-button#expand").first.click()
            await page.locator("tp-yt-paper-button#expand").filter(has_text="...more").first.click()
            print("...MAIS clicado")
        except Exception as e:
            print("Erro ao clicar em ...MAIS", e)

        await asyncio.sleep(5)
        
        # mostrar a transcrição
        try:
            # await page.locator("tp-yt-paper-button#expand").first.click()
            # await page.locator("tp-yt-paper-button#expand").filter(has_text="...mais").first.click()
            botao_transcricao = page.locator('button[aria-label="Show transcript"]').first
            # print("Encontrados:", await botao_transcricao.count())

            await botao_transcricao.wait_for(state="visible", timeout=10000)
            await botao_transcricao.click()

            print("Mostrar transcrição clicado")
        except Exception as e:
            print("Erro ao clicar em Mostrar transcrição", e)            

        # botoes = await page.locator("yp-yt-paper-button#expand").count()
        # print("Botões encontrados:", botoes)

        # print("\nAbra a transcrição do vídeo")
        # print("Aguarde alguns segundos.")
        # print("Depois pressione ENTER.")

        # input()

        await asyncio.sleep(10)

        await context.close()

asyncio.run(main())