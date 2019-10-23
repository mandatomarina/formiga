from slackbot.bot import respond_to
from slackbot.bot import listen_to
import re
import urllib.parse
from lxml.html import fromstring
import requests
import json

class Projeto:
    def __init__(self, tipo, numero, ano):
        self.tipo = tipo.upper()
        self.numero = numero
        self.ano = ano

    def search(self):
        nature = {
        'PL' : 1,
        'PDL' : 4,
        'PLC' : 2,
        'PR' : 3,
        'PEC' : 5,
        'REQ' : 7
    }
        base_url = "https://www.al.sp.gov.br"
        args = {
            'direction' : 'inicio',
            'lastPage' : 0,
            'currentPage' : 0,
            'act' : 'detalhe',
            'rowsPerPage' : 5,
            'currentPageDetalhe' : 1,
            'method' : 'search',
            'natureId' : nature[self.tipo],
            'legislativeNumber' : self.numero,
            'legislativeYear' : self.ano
        }

        self.search_url = base_url + '/alesp/pesquisa-proposicoes?' + urllib.parse.urlencode(args) 
        res = requests.get(self.search_url)
        print("Got!")
        soup = fromstring(res.content)
        soup = soup.xpath("//div[@id='lista_resultado']//table/tbody/tr")
        if len(soup) > 1:
            self.autor = soup[0].xpath('./td')[0].text_content().replace('\n','').replace('\t','').replace('\r','').strip()
            self.autor_url = base_url + soup[0].xpath("./td/a")[0].get('href')
            n = soup[0].xpath('./td/a[@target="_top"]')[0]
            n.getparent().remove(n)
            self.info = soup[0].xpath('./td')[1].text_content().replace('\n','').replace('\t','').replace('\r','').strip()
            self.url = base_url + soup[0].xpath("./td/a")[1].get('href')


@respond_to('([A-Z]{2,3}) ([0-9]*)\/([0-9]{2,4})')
def info(message, tipo, numero, ano):
    print("Getting {} {}/{}".format(tipo, numero, ano))
    if len(ano) == 2:
        ano = '20' + str(ano)
    pl = Projeto(tipo, numero, ano)
    pl.search()
    attachments = [
    {
        'fallback': pl.info,
        'author_name': "Autorxs: {}".format(pl.autor),
        'author_link' : pl.autor_url,
        'title' : "{} {}/{}".format(tipo, numero, ano),
        'title_link': pl.url,
        'text': pl.info,
        'color': '#59afe1'
    }]
    
    message.reply_webapi('', json.dumps(attachments), in_thread=True)
    #message.reply(pl.info)
