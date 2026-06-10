import asyncio
import gzip
import json
from playwright.async_api import async_playwright

VIDEO_URL = "https://www.youtube.com/watch?v=bPntels5hw8"

def procurar_legendas(obj):

    if isinstance(obj, dict):

        if "transcriptSegmentViewModel" in obj:

            seg = obj["transcriptSegmentViewModel"]

            timestamp = seg.get("timestamp", "")
            texto = seg.get("simpleText", "")

            print(f"[{timestamp}] {texto}")

        for valor in obj.values():
            procurar_legendas(valor)
    
    elif isinstance(obj, list):

        for item in obj:
            procurar_legendas(item)

async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        page = await browser.new_page()

        async def capturar_response(response):

            if "youtubei/v1/get_panel" not in response.url:
                return

            print("\nGET_PANEL REQUEST")
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

        await browser.close()

asyncio.run(main())