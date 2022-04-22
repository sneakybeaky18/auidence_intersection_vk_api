import os
import time
import requests
import itertools
import random as r
import pandas as pd 
from tqdm import tqdm
from collections import Counter
from multiprocessing import Process

class BaseApiUrl:
    
    def get_api_url(self) -> str:
        return 'https://api.vk.com/method/'

class LoginToken:
    
    def get_login_token(self) -> str:
        with open("token.txt") as f:
            lines = f.readlines()
            for line in lines:
                return str(line).replace("\n","")

class WallApi:
    
    def __init__(self, wall_url):
        self.wall_url = wall_url
        
    def get_wall_url_vk_format(self) -> str:
        return self.wall_url[19:]
    
    def __post_data(self) -> dict:
        return {
            'access_token': LoginToken().get_login_token(),
            'posts': self.get_wall_url_vk_format(),
            'v': 5.131, 
        }
    
    def get_wall_info(self) -> dict:
        return eval(requests.post(f"{BaseApiUrl().get_api_url()}wall.getById", \
                                 data=self.__post_data(),
                                 ).text.replace("false", "False").replace("true", "True"))
    
    def get_id_and_owner_id(self):
        result = self.get_wall_info()['response'][0]
        return result['id'], result['owner_id']

class GetLikersIds:
    
    def __init__(self, link_for_post: str):
        self.link = link_for_post
        
    def __post_data(self) -> dict:
        item, owner = WallApi(wall_url=self.link).get_id_and_owner_id()
        return {
            'access_token': LoginToken().get_login_token(),
            'type': 'post',
            'owner_id': owner,
            'item_id': item,
            'page_url': self.link,
            'offset': 1,
            'count': 999,
            'v': 5.131,
        }
    
    def get(self) -> dict:
        return eval(requests.post(f"{BaseApiUrl().get_api_url()}likes.getList", \
                            data=self.__post_data()).text)['response']['items']


class GroupNamesById:
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
    def __post_data(self):
        return {
            'access_token': LoginToken().get_login_token(),
            'user_id': self.user_id,
            'extended': 1,
            'count': 10,
            'v': 5.131,
        }
        
    def get_all_names(self) -> list:
        """
            return dict with group ids
        """
        try:
            return [
                    j['name'] for j in 
                        eval(\
                            requests.post(f"{BaseApiUrl().get_api_url()}users.getSubscriptions", \
                                            data=self.__post_data()) \
                                            .text.replace("true","True").replace("false", "False")) \
                                            ['response']['items']
                   ]
        except KeyError:
            return ["closed page"]

class GetPostUrls:

    def get(self):
        post_urls = []
        with open("posts.txt") as posts:
            for line in posts.readlines():
                post_urls.append(line.replace("\n",""))
        return post_urls

class GetGroupNamesByLikers:

    def __init__(self, post_urls: list[str]):
        self.post_urls = post_urls 

    def get_likers(self) -> list[int]:
        return [GetLikersIds(post).get() for post in self.post_urls]

    def get_names(self, batch) -> bool:
        names = []
        for liker in tqdm(batch):
            names.append(
                GroupNamesById(liker).get_all_names()
            )
        df = pd.DataFrame()
        df['names'] = list(itertools.chain(*names))
        df.to_csv(f"temp/temp_csv{r.randint(1,10)}{time.time()}")
        return True
    
    def get_10_quant(self, arr: list):
        arr = list(itertools.chain(*arr))
        paralleled = [
            arr[int(len(arr) * .0) : int(len(arr) * .1)],
            arr[int(len(arr) * .1) : int(len(arr) * .2)],
            arr[int(len(arr) * .2) : int(len(arr) * .3)],
            arr[int(len(arr) * .4) : int(len(arr) * .5)],
            arr[int(len(arr) * .5) : int(len(arr) * .6)],
            arr[int(len(arr) * .6) : int(len(arr) * .7)],
            arr[int(len(arr) * .8) : int(len(arr) * .9)],
            arr[int(len(arr) * .9) : int(len(arr) * 1)],
        ]
        return paralleled

    def run(self) -> int:
        processes = []
        for batch in self.get_10_quant(self.get_likers()):
            processes.append(
                Process(target=self.get_names, args=(batch,))
            )
        for _ in processes:
            _.start()
        return 1 