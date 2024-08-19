import requests
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
from urllib.parse import quote
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel as BM
import urllib3, json
import datetime
import re, asyncio
from interest_rate import kor_base_interest_rate, global_base_interest_rate
from news_search import get_news_with_query, get_news
from wiki_search import get_wikipedia
from config import state_name_list,kor
# FastAPI
app = FastAPI(
    title="real_time_query"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """Web socket connection manager."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


conn_mgr = ConnectionManager()

@app.get("/")
def home():
    return {"message": "real_time_query"}

class Keyword(BM):
    keyword: str
    intent: str

@app.post("/real_time_query")
async def api(keyword:Keyword):
    final_res=[]
    intent=keyword.intent
    keyword=keyword.keyword

    if intent=="economic" and "금리" in keyword:
        if len([g for g in state_name_list if g in keyword.replace(" ","")])!=0:
            finance_info=await global_base_interest_rate(keyword)
            if len(finance_info)!=0:
                for fi in finance_info:
                    s=fi["state"]
                    final_res.append({"title":f"finance info search {s}", "content":fi["interest_rate"]})
        # elif len([k for k in kor if k in keyword.replace(" ","")])!=0:
        else:
            finance_info=await kor_base_interest_rate()
            final_res.append({"title":f"finance info search {keyword}", "content":finance_info})
        # else:
        #     finance_info=await global_base_interest_rate(keyword)
        #     if len(finance_info)!=0:
        #         for fi in finance_info:
        #             s=fi["state"]
        #             final_res.append({"title":f"finance info search {s}", "content":fi["interest_rate"]})

    else:
        wiki_res= await get_wikipedia(keyword)
        final_res.append({"title":f"wiki search {keyword}", "content":wiki_res})

    news_titles,news_contents,news_release_date,naver_news_links= await get_news_with_query(keyword)
    crawling_res=await get_news(news_titles,news_contents,news_release_date,naver_news_links)

    for cr in crawling_res:
        final_res.append({"title":cr["title"],"content":cr["article_source"]})
    # final_res.append(crawling_res)

    result = {
        "related_news_list": final_res
    }
    with open("./input_keyword.txt", 'a') as ff:
        ff.write(f"keyword:{keyword}\n{final_res[:3]}\n==============================================\n\n")
    return result

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8586)
    # uvicorn.run("__main__:app", host="0.0.0.0", port=8586, workers=4, reload=False)