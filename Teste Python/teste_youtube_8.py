import asyncio
import gzip
import json
from lista_videos import videos, curso, videos_listados
from playwright.async_api import async_playwright

VIDEO_URL = videos[0][2]


def extrair_transcricao(json_data):
    resultado = []

    try:
        itens = (
            json_data["content"]
            ["engagementPanelSectionListRenderer"]
            ["content"]
            ["sectionListRenderer"]
            ["contents"][0]
            ["itemSectionRenderer"]
            ["contents"]
        )

        for item in itens:

            timeline = (
                item["macroMarkersPanelItemViewModel"]
                ["item"]
                ["timelineItemViewModel"]
            )

            timestamp = timeline.get("timestamp", "")

            for content_item in timeline.get("contentItems", []):

                segmento = content_item.get(
                    "transcriptSegmentViewModel"
                )

                if segmento:

                    texto = segmento.get(
                        "simpleText",
                        ""
                    ).strip()

                    resultado.append(
                        (timestamp, texto)
                    )

    except Exception as e:
        print("Erro ao extrair:", e)

    return resultado



async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        async def capturar_response(response):

            if "youtubei/v1/get_panel" not in response.url:
                return

            # print("\nGET_PANEL REQUEST")
            # print(response.url)

            try:

                headers = response.headers

                # print("\nHEADERS:")
                # print(headers)

                body = await response.body()

                # print("\nBODY SIZE:")
                # print(len(body))

                if headers.get("content-encoding") == "gzip":

                    # print("\nDESCOMPACTANDO GZIP...")

                    body = gzip.decompress(body)

                texto = body.decode("utf-8")

                # print("\nINÍCIO DO JSON:")
                # print(texto[:3000])
                dados = json.loads(texto)
            
                legendas = extrair_transcricao(dados)

                # print(f"\nSegmentos encontrados: {len(legendas)}")

                # for timestamp, texto in [(item["timestamp"], item["texto"]) for item in legendas[:10]]:
                #     print(f"[{timestamp}] {texto}")

                # texto_completo = " ".join(
                #     item["texto"]
                #     for item in legendas
                # )                     
                print(f"[Title] {await page.title()}")    
                for timestamp, texto in legendas: # legendas[:10]
                    print(f"[{timestamp}] {texto}")

                # texto_completo = " ".join(
                #     item[1]
                #     for item in legendas
                # )

                # print("\nPrimeiros 1000 caracteres:")
                # print(texto_completo[:1000])

            except Exception as e:

                print("\nERRO")
                print(type(e).__name__)
                print(str(e))

        page.on("response", capturar_response)

        await page.goto(
            VIDEO_URL,
            wait_until="networkidle"
        )  

        await page.wait_for_timeout(1000)

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


        # expandir a descrição
        try:
            # await page.locator("tp-yt-paper-button#expand").first.click()
            await page.locator("tp-yt-paper-button#expand").filter(has_text="...mais").first.click()
            # print("...MAIS clicado")
        except Exception as e:
            print("Erro ao clicar em ...MAIS", e)

        # mostrar a transcrição
        try:
            # await page.locator("tp-yt-paper-button#expand").first.click()
            # await page.locator("tp-yt-paper-button#expand").filter(has_text="...mais").first.click()
            botao_transcricao = page.locator('button[aria-label="Mostrar transcrição"]').first
            # print("Encontrados:", await botao_transcricao.count())

            await botao_transcricao.wait_for(state="visible", timeout=10000)
            await botao_transcricao.click()

            # print("Mostrar transcrição clicado")
        except Exception as e:
            print("Erro ao clicar em Mostrar transcrição", e)            

        # botoes = await page.locator("yp-yt-paper-button#expand").count()
        # print("Botões encontrados:", botoes)

        # print("\nAbra a transcrição do vídeo")
        # print("Aguarde alguns segundos.")
        # print("Depois pressione ENTER.")

        # input()

        await asyncio.sleep(1)

        await browser.close()

asyncio.run(main())