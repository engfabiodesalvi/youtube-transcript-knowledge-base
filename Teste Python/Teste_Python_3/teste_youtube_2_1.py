import re
import json
from pathlib import Path


# Videos listados

# define o diretório atual para salvar o arquivo
arquivo_entrada = (
    Path(__file__).parent /
    "elemento_transcricao_1.html"
)    

with open(
    arquivo_entrada,
    encoding="utf-8"
) as f:

    html = f.read()

padrao = re.compile(
    r'<div class="segment-timestamp.*?">\s*(.*?)\s*</div>.*?<yt-formatted-string class="segment-text.*?">(.*?)</yt-formatted-string>',
    re.S
)

transcricao = []

for timestamp, texto in padrao.findall(html):

    texto = re.sub(r"<.*?>", "", texto)

    transcricao.append(
        {
            "timestamp": timestamp.strip(),
            "texto": texto.strip()                
        }
    )

    # print(
    #     f"[{timestamp.strip()}] "
    #     f"{texto.strip()}"
    # )

print(
    f"[{transcricao[0]["timestamp"]}] "
    f"{transcricao[0]["texto"]}"
)
print(
    f"[{transcricao[-1]["timestamp"]}] "
    f"{transcricao[-1]["texto"]}"
)


# define o diretório atual para salvar o arquivo
nome_arquivo = "transcricao_2_1.json"
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