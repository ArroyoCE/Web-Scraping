import requests
from bs4 import BeautifulSoup
from FuncoesWebScrapping import extract_html
from FuncoesWebScrapping import abrir_navegador 
import urllib.parse


#Buscar a página

site = "https://www.enjoei.com.br/eletronicos-videogames/s?ref=search_categories_menu&sid=5727c0ff-46b3-4350-b958-39932c2b46a6-1724501634933&lp=24h&u=true&sr=same_country&dep=eletronicos&cat=eletronicos-videogames"

html = extract_html(site)

soup = BeautifulSoup(html, "html.parser")
links=[]
links_cached = []

while(True):
    if not links:
        for link in soup.find_all('a'):
            if link.get('href') != None:
                if link.get('href').startswith('/p/'): 
                    url = str("http://www.enjoei.com.br"+link.get('href'))
                    links.append(url)
        
    
    html = extract_html(site)
    soup = BeautifulSoup(html, "html.parser")
    result_list = list(set(links_cached + links))
    links_cached = result_list
    
    links=[]
        
    for link in soup.find_all('a'):
        if link.get('href') != None:
            if link.get('href').startswith('/p/'): 
                url = str("http://www.enjoei.com.br"+link.get('href'))
                links.append(url)

    
    
    print(len(links))
    print("\n\n\n\n\n\n\n\n")
    for i in range(len(links)):
        print(links[i])
        if links[i] in links_cached:
            pass
        else:
            abrir_navegador(links[i])


