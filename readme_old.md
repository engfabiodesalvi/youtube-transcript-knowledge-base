<!-- Segue um README.md completo para o GitHub documentando as duas versões (`teste_youtube_10.py` e `teste_youtube_11.py`), destacando arquitetura, fluxo, desempenho e funções utilizadas.-->

# Extrator de Transcrições do YouTube com Playwright e BeautifulSoup

## Visão Geral

Este projeto automatiza a obtenção de transcrições (legendas) de vídeos do YouTube utilizando Python e Playwright.

Diferentemente de soluções que dependem de APIs externas ou bibliotecas de terceiros específicas para transcrição, esta implementação utiliza o próprio mecanismo interno do YouTube acessado pelo navegador, garantindo maior compatibilidade com vídeos públicos que possuem transcrição disponível.

O processo é realizado automaticamente através da navegação na página do vídeo, abertura da área de descrição, acionamento da opção **"Mostrar transcrição"** e captura da resposta JSON enviada pelo endpoint interno do YouTube.

---

# Tecnologias Utilizadas

* Python 3.10+
* Playwright
* AsyncIO
* JSON
* Pathlib
* GZIP

---

# Estrutura dos Dados

Cada vídeo é definido como:

```python
(
    "Tópico",
    "Subtópico",
    "URL"
)
```

Exemplo:

```python
(
    "Topico",
    "Subtopico",
    "URL Video Youtube"
)
```

---

# Fluxo Geral da Aplicação

## 1. Inicialização

O navegador Chromium é iniciado via Playwright:

```python
browser = await p.chromium.launch(
    headless=True
)
```

O modo Headless permite executar todo o processo sem abrir janelas gráficas.

---

## 2. Acesso ao Vídeo

Cada URL é carregada:

```python
await page.goto(
    url,
    wait_until="domcontentloaded"
)
```

ou

```python
await page.goto(
    url,
    wait_until="networkidle"
)
```

dependendo da versão utilizada.

---

## 3. Expansão da Descrição

O botão "...mais" é localizado e clicado:

```python
await page.locator(
    "tp-yt-paper-button#expand"
).filter(
    has_text="...mais"
).first.click()
```

Esta etapa é necessária para tornar visível o botão de transcrição.

---

## 4. Abertura da Transcrição

O botão "Mostrar transcrição" é localizado:

```python
button[aria-label="Mostrar transcrição"]
```

e acionado automaticamente.

---

## 5. Captura da Resposta JSON

Ao abrir a transcrição, o YouTube faz uma chamada para:

```text
youtubei/v1/get_panel
```

Esta resposta contém todos os segmentos da legenda.

---

## 6. Extração da Transcrição

Os dados são extraídos da estrutura:

```text
content
 └─ engagementPanelSectionListRenderer
     └─ content
         └─ sectionListRenderer
             └─ contents
```

Cada segmento contém:

```json
{
    "timestamp": "0:00",
    "simpleText": "Texto da legenda"
}
```

---

## 7. Geração do Arquivo JSON

O resultado final é salvo em:

```text
transcricoes.json
```

na mesma pasta do script.

---

# Estrutura do Arquivo Gerado

```json
{
  "curso": "Curso Tipos de Variaveis em PHP",
  "videos": [
    {
      "topico": "...",
      "subtopico": "...",
      "url": "...",
      "transcricao": [
        {
          "timestamp": "0:00",
          "texto": "Olá pessoal..."
        }
      ]
    }
  ]
}
```

---

# Funções Principais

## extrair_transcricao()

Responsável por percorrer a estrutura JSON retornada pelo YouTube.

### Entrada

```python
json_data
```

### Saída

```python
[
    {
        "timestamp": "0:00",
        "texto": "Olá pessoal..."
    }
]
```

### Responsabilidades

* Navegar pela estrutura JSON.
* Localizar segmentos da legenda.
* Extrair timestamp.
* Extrair texto.
* Montar estrutura padronizada.

---

## processar_video()

Responsável por processar um único vídeo.

### Etapas

1. Abrir vídeo.
2. Expandir descrição.
3. Abrir transcrição.
4. Capturar JSON.
5. Extrair segmentos.
6. Retornar legenda.

### Retorno

```python
[
    {
        "timestamp": "...",
        "texto": "..."
    }
]
```

ou

```python
None
```

quando não existir transcrição.

---

# Versão 10 (teste_youtube_10.py)

## Arquitetura

Baseada em monitoramento global de respostas da página.

Utiliza:

```python
page.on(
    "response",
    capturar_response
)
```

Sempre que uma resposta é recebida pelo navegador, ela é analisada.

---

## Fluxo

```text
Vídeo
 ↓
Abrir transcrição
 ↓
Evento Response
 ↓
Capturar JSON
 ↓
Salvar em variável global
 ↓
Processar
```

---

## Vantagens

* Simples de implementar.
* Fácil depuração.
* Permite monitorar qualquer requisição.

---

## Desvantagens

* Captura respostas desnecessárias.
* Depende de variável compartilhada.
* Necessita sincronização adicional.
* Pode sofrer condições de corrida.

---

# Versão 11 (teste_youtube_11.py)

## Arquitetura

Baseada em captura direta da resposta esperada.

Utiliza:

```python
async with page.expect_response(...)
```

---

## Fluxo

```text
Aguardar resposta específica
 ↓
Clicar em transcrição
 ↓
Receber JSON
 ↓
Extrair dados
 ↓
Retornar resultado
```

---

## Exemplo

```python
async with page.expect_response(
    lambda r:
    "youtubei/v1/get_panel" in r.url
) as response_info:

    await botao_transcricao.click()
```

---

# Melhorias de Desempenho da Versão 11

## Remoção do Listener Global

Versão 10:

```python
page.on("response")
```

Versão 11:

```python
page.expect_response()
```

Resultado:

* Menor consumo de memória.
* Menor processamento.
* Menos eventos analisados.

---

## Eliminação de Esperas Ativas

Versão 10:

```python
for _ in range(5):
    await asyncio.sleep(0.2)
```

Versão 11:

Não necessita espera.

Resultado:

* Menor latência.
* Código mais previsível.

---

## Retorno Direto

Versão 10:

```python
transcricao_atual
```

Versão 11:

```python
return legendas
```

Resultado:

* Menor acoplamento.
* Menor complexidade.

---

## Troca de networkidle por domcontentloaded

Versão 10:

```python
wait_until="networkidle"
```

Versão 11:

```python
wait_until="domcontentloaded"
```

Benefícios:

* Carregamento mais rápido.
* Menor tempo por vídeo.
* Menor espera por conexões secundárias.

---

# Tratamento de Compressão

Algumas respostas chegam comprimidas.

O código identifica:

```python
content-encoding
```

e realiza:

```python
gzip.decompress()
```

quando necessário.

---

# Tratamento de Erros

O projeto trata:

* Vídeos sem transcrição.
* Erros de navegação.
* JSON inválido.
* Falhas de localização de elementos.
* Compressão incorreta.
* Timeouts.

---

# Modo Headless

O navegador pode executar sem interface gráfica:

```python
headless=True
```

Benefícios:

* Menor consumo de memória.
* Maior velocidade.
* Execução em servidores.
* Processamento em lote.

---

# Evolução da Arquitetura

Durante o desenvolvimento foram identificadas diferentes formas de obter as transcrições dos vídeos do YouTube.

## Abordagem 1 - Endpoint get_panel

O YouTube disponibilava a transcrição através do endpoint:

```text
youtubei/v1/get_panel
```

A captura era realizada através de:

```python
async with page.expect_response(
    lambda r:
    "youtubei/v1/get_panel" in r.url
)
```

### Vantagens

* Estrutura JSON organizada.
* Fácil extração dos timestamps.
* Baixa necessidade de processamento.

### Desvantagens

* Nem todos os vídeos utilizam este endpoint.
* O comportamento varia conforme o idioma da interface.
* Alterações frequentes do YouTube podem quebrar a implementação.

---

## Abordagem 2 - Endpoint get_transcript

Em alguns vídeos o YouTube passou a utilizar:

```text
youtubei/v1/get_transcript
```

Estrutura identificada:

```json
{
  "transcriptSegmentRenderer": {
    "startTimeText": {
      "simpleText": "0:05"
    },
    "snippet": {
      "runs": [
        {
          "text": "so far you have learned..."
        }
      ]
    }
  }
}
```

### Problemas encontrados

Nem sempre a resposta retornava a transcrição.

Em diversos casos foi retornado:

```json
{
  "error": {
    "code": 400,
    "status": "FAILED_PRECONDITION"
  }
}
```

Também foram observadas diferenças de comportamento entre:

* vídeos listados;
* vídeos individuais;
* idioma do navegador;
* idioma da conta do YouTube.

---

## Abordagem 3 - Extração Direta do HTML

Após diversas alterações internas do YouTube, foi adotada uma abordagem mais robusta:

1. Abrir a transcrição.
2. Capturar o HTML do painel.
3. Extrair os segmentos diretamente do DOM.

Esta abordagem não depende dos endpoints internos do YouTube.

---

# Estrutura HTML Identificada

Foi identificado o seguinte padrão:

```html
<transcript-segment-view-model>

    <div
        class="ytwTranscriptSegmentViewModelTimestamp">
        0:04
    </div>

    <span role="text">
        They say PHP is dead...
    </span>

</transcript-segment-view-model>
```

Onde:

| Elemento                               | Função           |
| -------------------------------------- | ---------------- |
| ytwTranscriptSegmentViewModelTimestamp | Timestamp        |
| span[role="text"]                      | Texto da legenda |

---

# Extração com BeautifulSoup

Instalação:

```bash
pip install beautifulsoup4 lxml
```

Processamento:

```python
segmentos = soup.find_all(
    "transcript-segment-view-model"
)
```

Extração:

```python
timestamp = segmento.find(
    "div",
    class_="ytwTranscriptSegmentViewModelTimestamp"
)

texto = segmento.find(
    "span",
    role="text"
)
```

---

# Normalização do Texto

Durante os testes foi identificado que o HTML contém:

* quebras de linha;
* espaços de indentação;
* tabulações.

Exemplo bruto:

```text
PHP is still very much alive,
                                    and learning it...
```

Para normalização foi utilizada:

```python
texto_limpo = " ".join(
    texto.get_text().split()
)
```

Resultado:

```text
PHP is still very much alive, and learning it...
```

### Benefícios

Remove automaticamente:

* múltiplos espaços;
* quebras de linha;
* tabulações;
* caracteres de espaçamento redundantes.

---

# Comparação das Abordagens

| Método               | Estabilidade | Complexidade | Dependência Interna |
| -------------------- | ------------ | ------------ | ------------------- |
| get_panel            | Média        | Média        | Alta                |
| get_transcript       | Baixa        | Alta         | Alta                |
| HTML + BeautifulSoup | Alta         | Baixa        | Baixa               |

---

# Lições Aprendidas

Durante o desenvolvimento foram observados os seguintes comportamentos do YouTube:

* Alteração frequente dos endpoints internos.
* Mudança do endpoint utilizado dependendo do vídeo.
* Diferenças entre vídeos listados e não listados.
* Diferenças causadas pelo idioma do navegador.
* Possível interferência de anúncios.
* Possível interferência de mecanismos anti-automação.

Por esse motivo, a estratégia baseada em extração do HTML da transcrição apresentou maior robustez e menor dependência de mudanças internas da plataforma.

---

# Possíveis Evoluções Futuras

* Exportação para Markdown.
* Exportação para TXT.
* Exportação para CSV.
* Agrupamento por curso.
* Paralelização de vídeos.
* Processamento de playlists automaticamente.
* Geração automática de documentação.
* Integração com IA para sumarização.
* Indexação vetorial para RAG.
* Busca semântica sobre as transcrições.

---

# Resultado

A versão 11 representa uma evolução significativa da arquitetura original, oferecendo menor acoplamento, melhor desempenho, menor consumo de recursos e maior confiabilidade durante a captura das transcrições do YouTube.
