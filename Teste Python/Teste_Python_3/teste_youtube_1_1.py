from bs4 import BeautifulSoup
from pathlib import Path
import json

# Videos listados

# define o diretório atual para abrir o arquivo
arquivo_entrada = (
    Path(__file__).parent /
    "elemento_transcricao_1.html"
)    

with open(
    arquivo_entrada,
    "r",
    encoding="utf-8"
) as f:

    html = f.read()

soup = BeautifulSoup(
    html,
    "html.parser"
)

transcricao = []

segmentos = soup.select(
    "ytd-transcript-segment-renderer"
)

for segmento in segmentos:

    timestamp = segmento.select_one(
        ".segment-timestamp"
    )

    texto = segmento.select_one(
        ".segment-text"
    )

    if timestamp and texto:

        transcricao.append(
            {
                "timestamp": timestamp.get_text(strip=True),
                "texto": texto.get_text(strip=True)                
            }
        )

        # print(
        #     f"[{timestamp.get_text(strip=True)}] "
        #     f"{texto.get_text(strip=True)}"
        # )        

if transcricao:
    print(
        f"[{transcricao[0]["timestamp"]}] "
        f"{transcricao[0]["texto"]}"
    )
    print(
        f"[{transcricao[-1]["timestamp"]}] "
        f"{transcricao[-1]["texto"]}"
    )


# define o diretório atual para salvar o arquivo
nome_arquivo = "transcricao_1_1.json"
arquivo_saida = (
    Path(__file__).parent /
    nome_arquivo
)  

dados = {
    "curso": "",
    "topico": "",
    "subtopico": "",
    "transcricao": transcricao
}

with open(
    arquivo_saida,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dados,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"Arquivo {nome_arquivo} gerado")        