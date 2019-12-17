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

    # field cpu location
    DD_CPU     = 1    
    DD_BRAND   = 0
    DD_ALIASES = 1

    def __init__(self):
        self.kimovil_url = "https://www.kimovil.com/en/compare-smartphones"

        # self.deviceUrlList  = []
        # self.deviceInfoList = []
        self.max_page   = 330        

    ## Generate the kimovil_url.txt for the first run
    def gen_kimovil_url_list(self, url_file):

        kimovil_url = self.kimovil_url
        max_page    = self.max_page
        deviceUrlList = []

        try:
            for i in range(1, max_page):    
                #time.sleep(1)
                logging.info("get url in page {0}".format(i))
                res = requests.get('{0}/page.{1}'.format(kimovil_url, i))
                soup = BeautifulSoup(res.text)
                
                tag = soup.find_all("a", class_="open-newtab")
                
                for item in tag:
                    deviceUrlList.append(item['href'])    
                    #print(item['href'])
                #print(res.text)
                
        except Exception as e:
            logging.error(str(e))
        
        with open(url_file,'w') as fptr:
            for itr in deviceUrlList:        
                fptr.writelines(itr+'\n')

    ## Generate the kimovil_url.txt for the first run
    def start_crawler(self, url_file):
        
        deviceUrlList   = []
        deviceInfoList  = []

        if os.path.exists(url_file):            
            logging.info("Using {0}".format(url_file))
        else:
            self.gen_kimovil_url_list(url_file)

        ## check the url list is existed
        with open(url_file, 'r') as fptr:
            for line in fptr.readlines():        
                deviceUrlList.append(line)                

        ## iterate the url items
        page = 0
        featureDict = {}        
        for itr in deviceUrlList:      
            
            # inital value
            featureDict = {
                'model': None,
                'brand': None,
                'aliases': None,
                'cpu': None
            }

            try:
                url = itr.strip()
                #time.sleep(1)
                logging.info("page {0}, access {1}".format(page, url))    
            
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')

                ## get model name            
                featureDict['model'] = re.sub(r'.*buy-','',url)
                
                ## parsing intro sheet                   
                prs_intro_sheet    = soup.find_all('section', class_='kc-container white container-sheet-intro')
                prs_intro_sheet_dd = prs_intro_sheet[0].find_all('dl', class_="k-dl")[0].find_all("dd")

                ## get brand & alias name
                try:
                    tmp_str_brand   = prs_intro_sheet_dd[self.DD_BRAND].text              
                except Exception as e:
                    logging.warn(str(e))

                try:
                    tmp_str_aliases = prs_intro_sheet_dd[self.DD_ALIASES].text
                except Exception as e:
                    logging.warn(str(e))   
                
                featureDict['brand'] = re.sub(r'[^\w]',' ',tmp_str_brand.strip()) # replace symbol by space
                featureDict['aliases'] = re.sub(r'[^\w]',' ',tmp_str_aliases.strip()) # replace symbol by space

                ## parsing hardware sheet
                prs_hw_sheet    = soup.find_all('section', class_='kc-container white container-sheet-hardware')
                prs_hw_sheet_dd = prs_hw_sheet[0].find_all('dl', class_="k-dl")[0].find_all("dd")            
                tmp_str_cpu = prs_hw_sheet_dd[self.DD_CPU].text                        
                featureDict['cpu'] = re.sub(r'[^\w]',' ',tmp_str_cpu.strip()) # replace symbol by space
                
                deviceInfoList.append(list(featureDict.values()))
                print(list(featureDict.values()))
            
            except Exception as e:
                logging.error(str(e))

            if page % 500 == 0:
                df = pd.DataFrame(data=deviceInfoList, 
                    #columns={'Model','CPU'}
                    columns=list(featureDict.keys())
                    )
                df.to_csv("deviceInfo_tmp.csv", sep=',' , encoding='utf-8')
                
            page += 1    
            
        df = pd.DataFrame(data=deviceInfoList, columns=list(featureDict.keys()))
        df.to_csv("deviceInfo.csv", sep=',' , encoding='utf-8')

if __name__ == "__main__":
    kimovilCrawler = KimovilCrawler();
    kimovilCrawler.start_crawler(url_file="kimovil_url.txt")
