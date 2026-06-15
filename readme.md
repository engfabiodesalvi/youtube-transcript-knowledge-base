# YouTube Transcript Extractor with Playwright and BeautifulSoup

Extrator de transcrições do YouTube desenvolvido em Python utilizando Playwright, BeautifulSoup e Expressões Regulares.

O objetivo deste projeto é automatizar a obtenção de legendas/transcrições de vídeos do YouTube para posterior utilização em:

* Estudos e cursos online
* Geração de documentação
* Construção de bases de conhecimento
* Sistemas RAG (Retrieval Augmented Generation)
* Fine-tuning de modelos de IA
* Indexação semântica
* Pesquisa textual
* Conversão de conteúdo audiovisual para texto estruturado

---

# Visão Geral

Durante o desenvolvimento foram estudadas diversas formas de obter transcrições diretamente do YouTube.

Inicialmente foram utilizadas chamadas internas realizadas pelo próprio site. Com o avanço dos testes observou-se que o YouTube altera frequentemente sua arquitetura interna, exigindo a implementação de abordagens alternativas.

Atualmente o projeto documenta quatro estratégias distintas de obtenção das transcrições:

1. Captura do endpoint `get_panel`
2. Captura do endpoint `get_transcript`
3. Extração do HTML utilizando BeautifulSoup
4. Extração do HTML utilizando Expressões Regulares (Regex)

---

# Tecnologias Utilizadas

## Navegação Automatizada

* Python 3.10+
* Playwright
* Chromium

## Processamento

* AsyncIO
* JSON
* GZIP
* Pathlib

## Parsing HTML

* BeautifulSoup4
* html.parser

## Expressões Regulares

* re

---

# Estrutura do Projeto

```text
Projeto
│
├── teste_youtube_10.py
├── teste_youtube_11.py
├── teste_youtube_12.py
│
├── elemento_transcricao_1.html
│
├── transcricoes.json
├── transcricao_1_1.json
├── transcricao_2_1.json
│
└── lista_videos.py
```

---

# Estrutura dos Vídeos

Os vídeos são organizados por curso, tópico e subtópico.

Exemplo:

```python
videos = [
    {
        "curso": "Curso PHP",
        "topicos": [
            {
                "topico": "Variáveis",
                "subtopicos": [
                    {
                        "nome": "O que são variáveis",
                        "video_url": "https://youtube..."
                    }
                ]
            }
        ]
    }
]
```

---

# Estratégia 1 - Endpoint get_panel

## Funcionamento

Após abrir a área de transcrição, o YouTube realiza uma requisição para:

```text
youtubei/v1/get_panel
```

Essa resposta contém toda a legenda em formato JSON.

---

## Fluxo

```text
Abrir vídeo
    ↓
Expandir descrição
    ↓
Mostrar transcrição
    ↓
Interceptar get_panel
    ↓
Extrair JSON
    ↓
Gerar transcrição
```

---

## Captura da Resposta

Utilizando:

```python
async with page.expect_response(
    lambda r:
    "youtubei/v1/get_panel" in r.url
) as response_info:
```

---

## Estrutura Encontrada

```json
{
  "timestamp": "0:00",
  "simpleText": "Texto da legenda"
}
```

---

## Vantagens

* Estrutura organizada.
* Fácil processamento.
* Menor necessidade de parsing.

---

## Limitações

* Nem todos os vídeos utilizam este endpoint.
* Mudanças internas do YouTube podem quebrar o fluxo.
* Dependência da interface atual da plataforma.

---

# Estratégia 2 - Endpoint get_transcript

Durante os testes foi identificado outro endpoint:

```text
youtubei/v1/get_transcript
```

---

## Estrutura Identificada

```json
{
  "transcriptSegmentRenderer": {
    "startTimeText": {
      "simpleText": "0:05"
    },
    "snippet": {
      "runs": [
        {
          "text": "Texto da legenda"
        }
      ]
    }
  }
}
```

---

## Problemas Encontrados

Em muitos vídeos foi retornado:

```json
{
  "error": {
    "code": 400,
    "status": "FAILED_PRECONDITION"
  }
}
```

---

## Possíveis Causas

* Mudanças na API interna.
* Vídeos privados.
* Vídeos listados.
* Diferenças de idioma.
* Restrições regionais.
* Validações internas do YouTube.

---

# Estratégia 3 - HTML + BeautifulSoup

Após diversas alterações observadas no YouTube, foi implementada uma solução baseada diretamente no HTML da transcrição.

Nesta abordagem o usuário abre manualmente a transcrição e copia o HTML.

---

## Estrutura HTML Identificada

```html
<ytd-transcript-segment-renderer>

    <div class="segment-timestamp">
        0:04
    </div>

    <yt-formatted-string class="segment-text">
        Texto da legenda
    </yt-formatted-string>

</ytd-transcript-segment-renderer>
```

---

## Extração

```python
segmentos = soup.select(
    "ytd-transcript-segment-renderer"
)
```

---

### Timestamp

```python
.segment-timestamp
```

### Texto

```python
.segment-text
```

---

## Vantagens

* Não depende dos endpoints internos.
* Maior estabilidade.
* Fácil manutenção.
* Compatível com diferentes idiomas.

---

## Desvantagens

* Requer obtenção manual do HTML.
* Depende da estrutura visual da página.

---

# Estratégia 4 - HTML + Regex

Implementação focada em simplicidade e velocidade.

---

## Padrão Utilizado

```python
padrao = re.compile(
    r'<div class="segment-timestamp.*?">\s*(.*?)\s*</div>.*?<yt-formatted-string class="segment-text.*?">(.*?)</yt-formatted-string>',
    re.S
)
```

---

## Limpeza do Texto

```python
texto = re.sub(
    r"<.*?>",
    "",
    texto
)
```

---

## Vantagens

* Extremamente rápida.
* Sem dependências externas.
* Baixo consumo de memória.

---

## Desvantagens

* Mais sensível a alterações no HTML.
* Menor robustez para layouts complexos.

---

# Nova Estrutura HTML Identificada

Durante os testes mais recentes foi encontrada uma nova implementação da transcrição.

---

## Estrutura

```html
<transcript-segment-view-model>

    <div
        class="ytwTranscriptSegmentViewModelTimestamp">
        0:04
    </div>

    <span role="text">
        Texto da legenda
    </span>

</transcript-segment-view-model>
```

---

## Seletores

Timestamp:

```python
.ytwTranscriptSegmentViewModelTimestamp
```

Texto:

```python
span[role="text"]
```

---

# Normalização de Texto

Muitos segmentos possuem:

* quebras de linha
* tabs
* espaços duplicados

Exemplo:

```text
PHP is still very much alive,
                                    and learning it...
```

---

## Solução

```python
texto_limpo = " ".join(
    texto.get_text().split()
)
```

Resultado:

```text
PHP is still very much alive, and learning it...
```

---

# Melhorias de Desempenho

## Uso de expect_response()

Substituição de:

```python
page.on("response")
```

por:

```python
page.expect_response()
```

Benefícios:

* Menor consumo de memória.
* Menor acoplamento.
* Menor processamento.

---

## Uso de domcontentloaded

Substituição de:

```python
wait_until="networkidle"
```

por:

```python
wait_until="domcontentloaded"
```

Benefícios:

* Menor tempo de carregamento.
* Menor espera por conexões secundárias.
* Maior velocidade em lotes grandes.

---

## Execução Headless

```python
headless=True
```

Benefícios:

* Menor uso de memória.
* Menor uso de CPU.
* Execução em servidores.
* Processamento em lote.

---

# Tratamento de Compressão

Algumas respostas chegam compactadas.

Verificação:

```python
content-encoding
```

Processamento:

```python
gzip.decompress()
```

---

# Arquivos Gerados

## Transcrição Consolidada

```text
transcricoes.json
```

---

## Estrutura Atualizada dos Vídeos

```text
lista_videos_curso_12.json
```

---

## Exportações Individuais

```text
transcricao_1_1.json
transcricao_2_1.json
```

---

# Tratamento de Erros

O projeto contempla:

* Vídeos sem transcrição.
* Erros de navegação.
* Timeouts.
* JSON inválido.
* Compressão inválida.
* Alterações de layout.
* Falhas de localização de elementos.
* Endpoints indisponíveis.

---

# Comparação das Estratégias

| Método               | Velocidade | Robustez | Dependência Interna |
| -------------------- | ---------- | -------- | ------------------- |
| get_panel            | Alta       | Média    | Alta                |
| get_transcript       | Média      | Baixa    | Alta                |
| HTML + BeautifulSoup | Alta       | Alta     | Baixa               |
| HTML + Regex         | Muito Alta | Média    | Baixa               |

---

# Possíveis Evoluções

* Exportação Markdown
* Exportação TXT
* Exportação CSV
* Processamento automático de playlists
* Integração com IA
* Sumarização automática
* Geração de documentação
* Base para sistemas RAG
* Busca semântica
* Vetorização de conteúdo
* Geração automática de material de estudo

---

# Conclusão

O projeto evoluiu de uma simples captura de endpoints internos do YouTube para uma plataforma de experimentação e extração de transcrições baseada em múltiplas estratégias.

A documentação das diferentes abordagens permite adaptar rapidamente o sistema a futuras alterações do YouTube, garantindo maior longevidade e flexibilidade para uso em estudos, pesquisa e aplicações de Inteligência Artificial.
