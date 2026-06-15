import asyncio
import gzip
import json
import subprocess
from lista_videos import videos, curso, videos_listados
from playwright.async_api import async_playwright
from pathlib import Path


# Comando correto e atualizado para limpar o CMD
subprocess.run("cls", shell=True)

# Novo formato do arquivo de vídeos

lista_videos_curso = videos
# lista_cursos = [
#     {
#         "curso": "",
#         "topicos": [
#             {
#                 "topico":"",
#                 "subtopicos": [
#                     {
#                         "nome": "",
#                         "video_url": ""
#                     } 
#                 ]
#             } 
#         ]
#     } 
# ]

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

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        async def processar_video(url):


            await page.goto(
                url,
                wait_until="domcontentloaded" # networkidle -> mais lento (várias coneções abertas) / domcontentloaded -> mais rápido
            )  

            await page.wait_for_timeout(1000)

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
                if await botao_transcricao.count() == 0:
                    print("Vídeos sem transcrição")
                    return None
                
                await botao_transcricao.wait_for(
                    state="visible",
                    timeout=10000
                )

                async with page.expect_response(
                    lambda r:
                    "youtubei/v1/get_panel" in r.url
                ) as response_info:

                    await botao_transcricao.click()
                    # print("Mostrar transcrição clicado")    

                response = await response_info.value

                body = await response.body()

                encoding = (
                    response.headers.get(
                        "content-encoding",
                        ""
                    ).lower()
                )           

                if encoding == "gzip":

                    # print("\nDESCOMPACTANDO GZIP...")

                    body = gzip.decompress(body)

                texto = body.decode(
                    "utf-8",
                    errors="ignore")

                # print("\nINÍCIO DO JSON:")
                # print(texto[:3000])
                dados = json.loads(texto)                

                legendas = extrair_transcricao(dados)
              
                return legendas

            except Exception as e:
                print("Erro ao bter transcrição")         

                print(type(e).__name__)   
                print(str(e))
       
        resultado_curso = {
            "curso": lista_videos_curso[0]['curso'],
            "videos": []
        }

        for curso in lista_videos_curso: # videos[:1]

            for topico in curso['topicos']:

                for subTopico in topico['subtopicos']:

                    print(f"\n[Tópico] {topico['topico']}")
                    print(f"[Subtópico] {subTopico['nome']}")

                    legendas = await processar_video(subTopico['video_url'])

                    if not legendas:

                        print("Sem transcrição")
                        continue                    
                    
                    # Inclui a legenda na estrutura já existente
                    subTopico['transcricao'] = legendas

                    resultado_curso["videos"].append(
                        {
                            "topico": topico['topico'],
                            "subtopico": subTopico['nome'],
                            "url": subTopico['video_url'],
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
                        f"[{legendas[-1]['timestamp']}] "
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

        # define o diretório atual para salvar o arquivo
        arquivo_saida = (
            Path(__file__).parent /
            "lista_videos_curso_12.json"
        )  

        # Forma moderna
        arquivo_saida.write_text(
            json.dumps(
                lista_videos_curso,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8" 
        )       

        print(f"\nArquivo salvo em:\n{arquivo_saida}")

        await browser.close()

asyncio.run(main())