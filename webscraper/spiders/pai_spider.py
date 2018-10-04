# -*- coding: utf-8 -*-
import codecs
import unicodedata
import scrapy
import time

#Constants
DICTIONARY = {ord(u'’'): u"'", ord(u'â'): u"a" }
def specials(error):
    return DICTIONARY.get(ord(error.object[error.start]), u''), error.end

def normalize(string):
    return str(unicodedata.normalize('NFKD', string.lower()).encode('ASCII', 'specials'))[2:-1]

class PaiSpider(scrapy.Spider):
    
    #Variables
    name = "pai"
    codecs.register_error('specials', specials)

    BASE_URL = 'http://www.pai.pt/q/business/advanced/where/'
    SPACE_DELIMITER = '%20'
    URL_DELIMITER = '/'

    def start_requests(self):
        urls = [
            'Região da Madeira',
            #'Distrito de Viana do Castelo',
            #'Distrito de Aveiro',
            #'Distrito de Beja',
            #'Distrito de Braga',
            # 'Distrito de Bragança',
            # 'Distrito de Castelo Branco',
            # 'Distrito de Coimbra',
            # 'Distrito de Évora',
            # 'Distrito de Faro',
            # 'Distrito da Guarda', 
            # 'Distrito de Leiria',
            # 'Distrito de Lisboa',
            # 'Distrito de Portalegre',
            # 'Distrito do Porto',
            # 'Distrito de Santarém',
            # 'Distrito de Setúbal',
            # 'Distrito de Viana do Castelo',
            # 'Distrito de Vila Real',
            # 'Distrito de Viseu',
        ]
        for url in urls:
           link = self.BASE_URL + url.replace(' ',self.SPACE_DELIMITER) + self.URL_DELIMITER + '1'
           yield scrapy.Request(url=link,callback=self.parse)

    def parse(self, response):    
        
        url_parts = []    
        next_page = response.request.url
        url_parts = response.request.url.split(self.URL_DELIMITER)

        for index in range(0, 20):    
            description = ''
            tags = ''
            zipcode = ''
            place = ''
            phone = ''
            address = ''
            list_of_address = []
            pcode = ''
            codex = ''
            place = ''

            try:
                name = response.css('span.result-bn::text')[index].extract()[2 : -1]
                if  ('todas as moradas' in name):
                        continue
            except IndexError:
                if index == 0: 
                   return
                else: 
                    continue
            try:   
                list_of_address = response.css('div.result-address')[index].extract().replace('<div class="result-address">','').replace('</div>','')[1:-1].split('<br>')
                address = list_of_address[-2]
                zipcode = list_of_address[-1]
                if (zipcode): 
                    pcode = zipcode[:4]
                    codex = zipcode[5:8]
                    place = zipcode[9:]
            except IndexError:
                pass

            try:
                phone = response.css('span.phone-number::text')[index + 1].extract()
                if (phone == 'telefone'): 
                    phone = response.css('span.phone-number::text')[index + 2].extract()
            except IndexError:
                pass

            try:
                description = response.css('div.flyout-txtresultlist::text')[index].extract()[1 : -1]
            except IndexError:
                pass

            try:
                 tags = response.css('a.refinement::text')[index].extract()[1 : -1]
            except IndexError:
                pass

            yield {
                'name' : normalize(name),
                'phone' : phone,
                'address' : normalize(address),
                'pcode' : pcode,
                'codex' : codex,
                'place' : normalize(place),
                'bulk' : str(list_of_address),
                'description' : normalize(description),
                'tags' : normalize(tags),
                'county' : url_parts[-2],
                'url_group' : response.request.url,
            }
        time.sleep(0.5 )
        next_index = url_parts[-1]    
        next_page = next_page.replace(self.URL_DELIMITER + next_index, '' ) + self.URL_DELIMITER + str(int(next_index ) + 1 )
        yield scrapy.Request(next_page, callback = self.parse )
