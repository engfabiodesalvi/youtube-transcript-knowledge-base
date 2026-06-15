import json
import random
import time

from lista_videos import videos_nao_listados, curso, videos_listados
from urllib.parse import urlparse
from urllib.parse import parse_qs

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
)

# print(dir(YouTubeTranscriptApi))

videos = {videos_nao_listados[1]}

print(videos)

def obter_video_id(url):

    print(url)

    video_id = parse_qs(
        urlparse(url).query
    )["v"][0]

    print(video_id)

    return video_id

def obter_transcricao(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["en"]
    )

    print = transcript

    resultado = []



    # for item in transcript:

    #     resultado.append({
    #         "timestamp": item["start"],
    #         "texto": item["text"]
    #     })

    return resultado


dados_saida = []

for indice, video in enumerate(videos, start=1):
    print(video)

    topico = video[0]
    subtopico = video[1]
    url = video[2]

    video_id = obter_video_id(url)

    print(f"\n[{indice}/{len(videos)}] {subtopico}")

    try:
        
        espera = random.uniform(5, 15)        
        time.sleep(espera)

        if indice % 20 == 0:

            pausa_longa = random.uniform(30, 90)

            print(
                f"Pausa longa: {pausa_longa:.1f}s"
            )

            time.sleep(pausa_longa)    


        transcricao = obter_transcricao(video_id)

        dados_saida.append({
            "topico": topico,
            "subtopico": subtopico,
            "video_id": video_id,
            "transcricao": transcricao
        })

        print(
            f"OK - {len(transcricao)} segmentos"
        )

    except TranscriptsDisabled:

        print(
            "ERRO - Transcrição desabilitada"
        )

    except NoTranscriptFound:

        print(
            "ERRO - Transcrição não encontrada"
        )

    except Exception as e:

        print(
            f"ERRO - {e}"
        )

    # intervalo aleatório entre consultas
    espera = random.uniform(3, 8)

    print(
        f"Aguardando {espera:.1f}s..."
    )

    time.sleep(espera)


with open(
    "transcricoes.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dados_saida,
        f,
        ensure_ascii=False,
        indent=4
    )

print("\nConcluído.")