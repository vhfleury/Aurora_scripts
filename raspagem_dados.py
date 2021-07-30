import requests, time, json
import steam_bit as steam 
import pandas as pd
import cookie

def entrando_link(pagina, cookies):
    """entra no mercado e puxa 100 itens, retorna a pagina com os itens"""

    while True:
        try:
            payload = {'start': pagina, 'count': 100, 'search_descriptions': '0', 'sort_column': 'name', 'sort_dir': 'asc', 'appid': '730', 'norender': '1', 'currency': '7'}
            url = 'http://steamcommunity.com/market/search/render?' 
            headers = {'user-agent': 'my-app/0.0.1'}

            return requests.get(url,  params=payload, headers=headers, cookies=cookies)

        except:
            print(f"erro de conexao, carregando novamente...")
            time.sleep(5)

def puxar_dados(conteudo_link, lista_itens, hora_retirada):
    """tratamento dos dados puxados no mercado"""

    for i in range(len(conteudo_link["results"])):
        teste_cookie = conteudo_link["results"][0]["sell_price_text"][0:1]
        
        if teste_cookie == "R":
            nome_skin = conteudo_link["results"][i]["name"]
            quantidade_anunciada = conteudo_link["results"][i]["sell_listings"]
            valor = conteudo_link["results"][i]["sell_price_text"]
            valor = valor.replace("R$ ", "").replace(".", "").replace(",", ".")
            tipo_item = conteudo_link["results"][i]["asset_description"]["type"]
            lista_itens.append((nome_skin, tipo_item, steam.data(), hora_retirada, valor, quantidade_anunciada))

        else:
            print("falha em ler cookie, tentando novamente...")
            break
            
def criando_arquivo(lista_itens, hora_retirada):
    """salvando os dados puxados em um arquivo csv"""
    coluna = ["Nome", "Tipo", 'Data', "Hora", "Valor R$", "Quatidade no Mercado"]
    dados = pd.DataFrame(data = lista_itens, columns= coluna)
    
    nome_arquivo = f"CSGO {steam.data()} h{hora_retirada[:2]}"
    dados.to_csv(f"dados raspagem/{nome_arquivo}.csv", sep=";", index = False)
    return nome_arquivo

def criando_log(nome_arquivo, lista_itens, iniciando_programa):
    """criando um log do desenpenho da raspagem"""

    with open(f"dados-log/{steam.data()}-log.txt", "a") as arquivo:
        log = f"{nome_arquivo}, {round((len(lista_itens))/100)} paginas carregas, {len(lista_itens)} itens puxados, iniciou as {time.ctime(iniciando_programa)[11:19]}, terminou {time.ctime()[11:19]}, levou {steam.tempo_total_programa(iniciando_programa)} minutos pra concluir\n"
        arquivo.write(log)

def puxando_todos_itens(hora_retirada):
    """puxando todos os itens disponivel no mercado"""
    lista_itens = []
    
    #puxando um cookie valido para a entregar os valores em real
    cookies, conta_cookie = cookie.cookie(retornar_conta=True)
    print(f"cookie da conta {conta_cookie}")
    if cookies != False:
        roda = True
    else:
        roda = False
        cookie.config()
    
    while (roda == True):

        link = entrando_link(len(lista_itens), cookies)

        #se a pagina carregou, tratar os dados puxados
        if link.status_code == 200:
            conteudo_link = json.loads(link.text)
            puxar_dados(conteudo_link, lista_itens, hora_retirada)
            pagina = round((len(lista_itens))/100)
            time.sleep(10)
        else:

            print(f"erro {link.status_code} ao carregar pagina {pagina}, tentando novamente...")
            time.sleep(10)

        print(f"pagina {pagina} carregada, total itens puxados {len(lista_itens)}")

        #quando puxar uma pagina com menos de 20 itens, parar o loop
        if len(conteudo_link["results"]) < 20 and len(lista_itens) > 11500:
            roda = False   

    return lista_itens

if __name__ == "__main__":
        iniciando_programa = time.time()
    hora_retirada = time.ctime(iniciando_programa)[11:16]
    
    print(hora_retirada)
    
    itens = puxando_todos_itens(hora_retirada)
    nome_arquivo = criando_arquivo(itens, hora_retirada)
    criando_log(nome_arquivo, itens, iniciando_programa)