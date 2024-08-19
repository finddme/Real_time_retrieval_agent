import requests
from bs4 import BeautifulSoup
from tqdm.notebook import tqdm
import pandas as pd
from urllib.parse import quote
import urllib3, json

async def get_wikipedia(keyword):
    keyword=keyword.replace("제일","가장")
    openApiURL = "http://aiopen.etri.re.kr:8000/WikiQA"
    ETRI_API="9e4dfa9c-5aeb-4b9b-96bb-9f942f761eac"
    type_ = "hybridqa"

    requestJson = {
    "argument": {
    "question": keyword,
    "type": type_
    }
    }

    http = urllib3.PoolManager()
    response = http.request(
    "POST",
    openApiURL,
    headers={"Content-Type": "application/json; charset=UTF-8","Authorization": ETRI_API},
    body=json.dumps(requestJson)
    )

    fin_res=""
    res=json.loads(response.data.decode())
    for r in res["return_object"]["WiKiInfo"]["AnswerInfo"]:
        fin_res+=r["answer"]
        fin_res+=" "
    # fin_res={"title":f"wiki result {keyword}", "date":" ", "article_source":fin_res}
    # fin_res={"title":f"wiki result {keyword}", "content":fin_res}
    return fin_res