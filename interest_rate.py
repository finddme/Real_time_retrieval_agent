import requests
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
import pandas as pd
from urllib.parse import quote
from config import state_name_list,kor,states_bank
async def kor_base_interest_rate():
    url=f"https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&ssc=tab.nx.all&query=%ED%95%9C%EA%B5%AD+%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC+%EC%B6%94%EC%9D%B4&oquery=%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC&tqi=ir78KsqptbNssDJYcJGssssss5N-333521&acq=%EA%B8%B0%EC%A4%80%EA%B8%88%EB%A6%AC%EC%B6%94%EC%9D%B4&acr=4&qdt=0"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    base_interest_rate=[]
    base_interest_rate_final=[]
    def parse_page(soup):
        for infos in soup.find_all(class_='cont_info'):
            info_list=infos.find_all('span',{"class":"text"})
            for info in info_list:
                base_interest_rate.append(info.get_text().strip())

    parse_page(soup)

    for i in range(0, len(base_interest_rate), 3):
        base_interest_rate_final.append(base_interest_rate[i:i+3])

    final_res=""
    for r in base_interest_rate_final[1:]:
        txt=f"{r[0]} 기준 금리 {r[1]}"
        if r[2] == "-": txt += " 변동 없음"
        else: txt += r[2]
        final_res+= f"{txt}\n"
    
    return final_res

async def global_base_interest_rate(keyword):
    def find_state(keyword):
        key_list=[]
        for key, values in state_name_list.items():
            for value in values:
                if value in keyword:
                    key_list.append(key)
        if len(key_list)!=0:
            return key_list
        else:
            return None

    global_base_interest_rate_final=[]
    def parse_page(soup):
        base_interest_rate=[]
        for infos in soup.find_all(class_='cont_info'):
            info_list=infos.find_all('span',{"class":"text"})
            for info in info_list:
                base_interest_rate.append(info.get_text().strip())
        return base_interest_rate
        
    states=find_state(keyword)
    if states:
        for state in states:
            state_bank=states_bank[state]
            try:
                query=quote(state_bank)
                url=f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={query}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, 'html.parser')
            
                base_interest_rate=[]
                base_interest_rate_final=[]
                base_interest_rate=parse_page(soup)
    
                for i in range(0, len(base_interest_rate), 3):
                    base_interest_rate_final.append(base_interest_rate[i:i+3])
            
                final_res=""
                for r in base_interest_rate_final[1:]:
                    txt=f"{r[0]} 기준 금리 {r[1]}"
                    if r[2] == "-": txt += " 변동 없음"
                    else: txt += r[2]
                    final_res+= f"{txt}\n"
                if final_res=="":pass
                else:
                    global_base_interest_rate_final.append({"state":state,"interest_rate":final_res})
            except Exception as e: pass

    return global_base_interest_rate_final