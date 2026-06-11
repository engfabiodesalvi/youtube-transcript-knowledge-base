import asyncio
import gzip
import json
import subprocess
from playwright.async_api import async_playwright
from pathlib import Path


# Comando correto e atualizado para limpar o CMD
subprocess.run("cls", shell=True)

curso = "Curso Tipos de Variaveis em PHP"

# videos = ["Tópico", "Subtópico", "URL"]
videos = [
    (
        "O que são variáveis",
        "Apresentação do curso",
        "https://www.youtube.com/watch?v=sVbEyFZKgqk"
    ),(
        "O que são variáveis",
        "O que são variáveis",
        "https://www.youtube.com/watch?v=KgUp3FomMoc"
    ),(
        "O que são variáveis",
        "O que são constantes",
        "https://www.youtube.com/watch?v=HrtS-FkPBqk"
    ),(
        "Os principais tipos de dados",        
        "O que são strings?",
        "https://www.youtube.com/watch?v=6JtP8xk1U_k"
    ),(
        "Os principais tipos de dados",        
        "Tipos de dados Integers/números",
        "https://www.youtube.com/watch?v=KH4MmQsCDuw"
    ),(
        "Os principais tipos de dados",        
        "Tipos de dados Datas",
        "https://www.youtube.com/watch?v=1kO_g_ucYCQ"                        
    ),(
        "Os principais tipos de dados",        
        "Trabalhando com array no PHP",
        "https://www.youtube.com/watch?v=rjEP_GUdg6o"                        
    ),(
        "Funções e escopos",        
        "Funções Echo e Print",
        "https://www.youtube.com/watch?v=d3c_OOD4Jzs"                        
    ),(
        "Funções e escopos",        
        "Aprendendo sobre escopo local e global",
        "https://www.youtube.com/watch?v=97LnEncGx2c"                        
    ),(
        "Projeto prático e Revisão",
        "Apresentação do HTML",
        "https://www.youtube.com/watch?v=XspbsepnhQ4"                        
    ),(
        "Projeto prático e Revisão",        
        "Revisando Strings",
        "https://www.youtube.com/watch?v=C8ZFLq24g_A"                        
    ),(
        "Projeto prático e Revisão",
        "Revisando Números",
        "https://www.youtube.com/watch?v=bPntels5hw8"                        
    ),(
        "Projeto prático e Revisão",
        "Revisando Array",
        "https://www.youtube.com/watch?v=t8U2FGjjqM8"                        
    ),(
        "Projeto prático e Revisão",
        "Revisando Datas",
        "https://www.youtube.com/watch?v=gCVlQdbddXY"                        
    )
]


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

                    # resultado.append(
                    #     (timestamp, texto)
                    # )

                    # Melhor para futuras implementações
                    resultado.append(
                        {
                            "timestamp": timestamp,
                            "texto": texto
                        }
                    )                    



    except Exception as e:
        print("Erro ao extrair:", e)

    return resultado


async def main():

    transcricao_atual = None

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        async def capturar_response(response):

            nonlocal transcricao_atual

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
            
                nonlocal transcricao_atual

                legendas = extrair_transcricao(dados)

                # Verifica se a legenda foi encontrada
                if legendas:
                    transcricao_atual = legendas
                # else:
                #     print("Nenhuma legenda encontrada")
                #     return
                
                # print(f"\nSegmentos encontrados: {len(legendas)}")

                # for timestamp, texto in [(item["timestamp"], item["texto"]) for item in legendas[:10]]:
                #     print(f"[{timestamp}] {texto}")

                # texto_completo = " ".join(
                #     item["texto"]
                #     for item in legendas
                # )   
                                  
                # print(f"[Título vídeo] {await page.title()}")
                
                # primeiro_e_ultimo = [legendas[0], legendas[-1]]
                # for timestamp, texto in primeiro_e_ultimo: # legendas[:10]
                #     print(f"[{timestamp}] {texto}")

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

        async def processar_video(url):

            nonlocal transcricao_atual

            transcricao_atual = None

            await page.goto(
                url,
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

                # verifica se o vídeo possui transcrição
                if await botao_transcricao.count() > 0:
                    await botao_transcricao.wait_for(state="visible", timeout=10000)
                    await botao_transcricao.click()
                    # print("Mostrar transcrição clicado")
                else:
                    print("Vídeos sem transcrição")

            except Exception as e:
                print("Erro ao clicar em Mostrar transcrição", e)            

            # botoes = await page.locator("yp-yt-paper-button#expand").count()
            # print("Botões encontrados:", botoes)

            # print("\nAbra a transcrição do vídeo")
            # print("Aguarde alguns segundos.")
            # print("Depois pressione ENTER.")

            # input()

            # espera a resposta
            for _ in range(5):

                if transcricao_atual is not None:
                    break

                await asyncio.sleep(0.2)   

            return transcricao_atual         
        
        page.on("response", capturar_response)

        resultado_curso = {
            "curso": curso,
            "videos": []
        }

        for video in videos: # videos[:1]

            print(f"\n[Tópico] {video[0]}")
            print(f"[Subtópico] {video[1]}")

            legendas = await processar_video(video[2])

            if not legendas:

                print("Sem transcrição")
                continue

            resultado_curso["videos"].append(
                {
                    "topico": video[0],
                    "subtopico": video[1],
                    "url": video[2],
                    "transcricao": legendas
                }
            )

            print(
                f"Segmentos encontrados: {len(legendas)}"
            )
            # print(legendas)
            # print(legendas[0])
            # print(legendas[0]['timestamp'])

            print(
                f"[{legendas[0]['timestamp']}] "
                f"{legendas[0]['texto']}"
            )

            print(
                f"[{legendas[-1]['timestamp']} "
                f"{legendas[-1]['texto']}"
            )

        # define o diretório atual para salvar o arquivo
        arquivo_saida = (
            Path(__file__).parent /
            "transcricoes.json"
        )        

        # with open(
        #     arquivo_saida,
        #     "w",
        #     encoding="utf-8"
        # ) as arquivo:
            
        #     json.dump(
        #         resultado_curso,
        #         arquivo,
        #         ensure_ascii=False,
        #         indent=2
        #     )
        
        # Forma moderna
        arquivo_saida.write_text(
            json.dumps(
                resultado_curso,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8" 
        )       

        print(f"\nArquivo salvo em:\n{arquivo_saida}")

        await browser.close()

asyncio.run(main())