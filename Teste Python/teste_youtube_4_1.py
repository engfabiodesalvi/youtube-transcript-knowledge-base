from lista_videos import videos, curso, videos_listados
from playwright.sync_api import sync_playwright
import json
import gzip
 
VIDEO_URL = videos[0][2]

json_salvo = False

def request_listener(request):

    if "get_panel" not in request.url:
        return

    print("\nGET_PANEL REQUEST")
    print(request.url)

    try:

        print("\nHEADERS:")
        print(request.headers)

        print("\nPOST_DATA:")
        print(repr(request.post_data))

    except Exception as e:

        print("\nERRO")
        print(type(e).__name__)
        print(e)    

    # global json_salvo

    # if json_salvo:
    #     return
    
    # if "get_panel" not in request.url:
    #     return
    
    # print("\nGET_PANEL REQUEST")
    # print(request.url)

    # try:

    #     payload = request.post_data

    #     print(payload)

    #     with open(
    #         "payload_get_panel.json",
    #         "w",
    #         encoding="utf-8"
    #     ) as f:
            
    #         f.write(payload)

    #     json_salvo = True
        
    #     print("\nPAYLOAD SALVO")

    # except Exception as e:

    #     print("\nERRO")
    #     print(type(e).__name__)
    #     print(e)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.on(
        "request",
        request_listener
    )

    page.goto(
        VIDEO_URL,
        wait_until="networkidle"
    )

    print(page.title())

    print("\nAbra a transcrição do vídeo")
    print("Aguarde alguns segundos.")
    
    input("Depois pressione ENTER.")

    browser.close()
