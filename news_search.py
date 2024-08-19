import requests
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
import pandas as pd
from urllib.parse import quote
import datetime
import re

async def get_news_with_query(keyword):
    keyword=quote(keyword)
    url=f"https://search.naver.com/search.naver?where=news&query={keyword}&sm=tab_opt&sort=0&photo=3&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0" 
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_titles = []
    news_contents = []
    news_release_date = []
    naver_news_links=[]
    
    def parse_page(soup):
        for info in soup.find_all(class_='news_info'):
            date=info.find_all('span',{"class":"info"})[1]
            news_release_date.append(date.get_text().strip())

            naver_news_link=info.find_all('a', {"class":"info"},href=True)[-1]
            naver_news_links.append(naver_news_link['href'])
            
        for title in soup.find_all(class_='news_tit'):
            news_titles.append(title.get_text().strip())
        for content in soup.find_all(class_='news_dsc'):
            news_contents.append(content.get_text().strip())

    parse_page(soup)
    
    next_page_url = url+"#"
    response = requests.get(next_page_url, stream=True)
    response.raw.decode_content = True
    soup = BeautifulSoup(response.text, 'html.parser')
    parse_page(soup)
    return news_titles,news_contents,news_release_date,naver_news_links

def news_crawling(naver_news_link):
    response = requests.get(naver_news_link, stream=True)
    response.raw.decode_content = True
    soup = BeautifulSoup(response.text, 'html.parser')

    articles=[]
    article = soup.select_one("#dic_area")
    for a in article:
        # print(a)
        articles.append(a.get_text())
    articles=[value for value in articles if value != ""]
    articles=[value for value in articles if value != "\n"]
    articles=articles[1:7]
    articles_str= "\n".join(articles)
    return articles_str

def parse_date(date_str):
    now = datetime.datetime.now()
    if '전' in date_str:
        number, unit = re.match(r'(\d+)(\D+)', date_str).groups()
        number = int(number)
        
        if '시간' in unit:
            return now - datetime.timedelta(hours=number)
        elif '분' in unit:
            return now - datetime.timedelta(minutes=number)
        elif '일' in unit:
            return now - datetime.timedelta(days=number)
        elif '주' in unit:
            return now - datetime.timedelta(weeks=number)
        elif '개월' in unit or "달" in unit:
            return now - datetime.timedelta(days=number*30)
    else:
        date_str = date_str.rstrip('.')
        return datetime.datetime.strptime(date_str, "%Y.%m.%d")

async def get_news(news_titles,news_contents,news_release_date,naver_news_links):
    crawling_result=[]
    for title,content,date,link in zip(news_titles,news_contents,news_release_date,naver_news_links):
        try:
            article_source=news_crawling(link)
            res={"title":title,"date":date, "article_source":article_source}
            # res={"title":title,"content":article_source}
            crawling_result.append(res)
        except Exception as e: pass
    crawling_result = sorted(crawling_result, key=lambda x: parse_date(x['date']), reverse=True)
    return crawling_result