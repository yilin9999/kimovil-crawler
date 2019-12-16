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
    DD_CPU=1    

    def __init__(self):
        self.kimovil_url = "https://www.kimovil.com/en/compare-smartphones/"

        # self.deviceUrlList  = []
        # self.deviceInfoList = []
        self.max_page   = 330        

    ## Generate the kimovil_url.txt for the first run
    def gen_kimovil_url_list(self, url_file):

        kimovil_url = self.kimovil_url
        max_page    = self.max_page
        deviceUrlList = []

        try:
            for i in range(1,max_page):    
                #time.sleep(1)
                logging.info("get url in page {0}".format(i))
                res = requests.get('{0}/page.{1}'.format(kimovil_url, i))
                soup = BeautifulSoup(res.text)
                
                tag = soup.find_all("a", class_="open-newtab")
                
                for item in tag:
                    deviceUrlList.append(item['href'])    
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

        ## check the url list is existed
        with open(url_file, 'r') as fptr:
            for line in fptr.readlines():        
                deviceUrlList.append(line)                

        # if os.path.exists(url_file):            
        #     logging.info("Using {0}".format(url_file))
        # else:
        #     self.gen_kimovil_url_list(url_file)
        
        ## iterate the url items
        page = 0
        featureDict = {}        
        for itr in deviceUrlList:      
            
            url = itr.strip()
            time.sleep(1)
            logging.info("page {0}, access {1}".format(page, url))    
        
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
                        
            ## Get model name
            featureDict['model'] = re.sub(r'.*buy-','',url)

            ## parsing hardware sheet
            prs_hw_sheet    = soup.find_all('section', class_='kc-container white container-sheet-hardware')
            prs_hw_sheet_dd = prs_hw_sheet[0].find_all('dl', class_="k-dl")[0].find_all("dd")            
            tmp_str = prs_hw_sheet_dd[self.DD_CPU].text            
            ## replace symbol by space
            featureDict['cpu'] = re.sub(r'[^\w]',' ',tmp_str.strip())
             
            deviceInfoList.append(list(featureDict.values()))
            print(list(featureDict.values()))
            
            if page % 500 == 0:
                df = pd.DataFrame(data=deviceInfoList, 
                    columns={'Model','CPU'}
                    #columns=list(featureDict.keys())
                    )
                df.to_csv("deviceInfo_tmp.csv", sep=',' , encoding='utf-8')
                
            page += 1    
            
        df = pd.DataFrame(data=deviceInfoList, columns=list(featureDict.keys()))
        df.to_csv("deviceInfo.csv", sep=',' , encoding='utf-8')

if __name__ == "__main__":
    kimovilCrawler = KimovilCrawler();
    kimovilCrawler.start_crawler(url_file="kimovil_url.txt")
