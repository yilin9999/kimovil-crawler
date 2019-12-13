import requests
import time
import os
import sys
import re
import pandas as pd
from bs4 import BeautifulSoup

import logging
# Logging setting
logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.INFO)

class KimovilCrawler():
    def __init__(self):
        self.kimovil_url = "https://www.kimovil.com/en/compare-smartphones/"

        self.deviceUrlList  = []
        self.deviceInfoList = []
        self.max_page       = 300

    ## Generate the kimovil_url.txt for the first run
    def gen_kimovil_url_list(self, url_file):

        kimovil_url = self.kimovil_url
        max_page    = self.max_page

        try:
            for i in range(1,max_page):    
                time.sleep(2)
                logging.info("get url in page {0}".format(i))
                res = requests.get('{0}/page.{1}'.format(kimovil_url, i))
                soup = BeautifulSoup(res.text)
                
                tag = soup.find_all("a", class_="open-newtab")
                
                for item in tag:
                    self.deviceUrlList.append(item['href'])    
                #print(res.text)
        except Exception as e:
            logging.error(str(e))
        
        with open(url_file,'w') as fptr:
            for itr in self.deviceUrlList:        
                fptr.writelines(itr+'\n')

    ## Generate the kimovil_url.txt for the first run
    def start_crawler(self, url_file):

        ## check the url list is existed
        if os.path.exists(url_file):
            logging.info("Using {0}".format(url_file))
        else:
            self.gen_kimovil_url_list(url_file)
        
        ## iterate the url items
        page = 0
        for url in self.deviceUrlList:
            
            time.sleep(2)
            logging.info("page {0}, access {1}".format(page, url))    
        
            res = requests.get(url)
            soup = BeautifulSoup(res.text)
            
            ## Syntax parsing
            tag   = soup.find_all(class_="section hardware clear", id = "hardware")
            tag_1 = tag[0].find_all(class_="cell right")
            ###############
            r_chipset  = 0 
            r_cores    = 2
            r_freq     = 3
            r_dram     = 0
            r_antutu   = 0
            ###############
            tag     = soup.find_all(class_ ="fc w100 osversion")
            version = tag[0].text
            ###############
            tag_2   = tag_1[0].find_all("dd")
            chipset = tag_2[r_chipset].text
            cores   = tag_2[r_cores].text
            freq  =   tag_2[r_freq].text    
            ###############    
            tag_2 = tag_1[2].find_all("dd")
            dram  = tag_2[r_dram].text
            ############### 
            tag_2   = tag_1[3].find_all("dd")
            antutu  = tag_2[r_antutu].text
            antutu  = re.sub(r'\(.*','', antutu)
            antutu  = antutu.strip('\n')
            antutu  = antutu.strip()
            
            model = re.sub(r'.*buy-','',url)
            chipset = re.sub(r'\n-.*','',chipset)
            chipset = re.sub(r'\n','',chipset)    
            dram =re.sub(r'^.*\n','',dram)
            dram =re.sub(r'\n.*$','',dram)
            version =re.sub(r'^.*\n','',version)
            version =re.sub(r'\n.*$','',version)    
            
            self.deviceInfoList.append([model, chipset, cores, freq, dram, version, antutu])
            print([model, chipset, cores, freq, dram, version, antutu])
            
            if page % 500 == 0:
                df = pd.DataFrame(data=self.deviceInfoList, 
                    columns={'Model','Chipset','CPU_cores','CPU_freq', 'Dram', 'Android', 'Antutu'}
                    )
                df.to_csv("deviceInfo_tmp.csv", sep=',' , encoding='utf-8')
                
            page += 1    
            

        df = pd.DataFrame(data=self.deviceInfoList,                   
                    columns=['Model','Chipset','CPU_cores','CPU_freq', 'Dram', 'Android', 'Antutu']
                    )
        df.to_csv("deviceInfo.csv", sep=',' , encoding='utf-8')

if __name__ == "__main__":
    kimovilCrawler = KimovilCrawler();
    kimovilCrawler.start_crawler(url_file="kimovil_url.txt")
