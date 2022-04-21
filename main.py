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
        return ""
    
class GetPeopleFollows:
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        
    def __post_data(self):
        return {
            'access_token': LoginToken().get_login_token(),
            'user_id': self.user_id,
            'count': 10,
            'v': 5.131,
        }
        
    def get_all_ids(self) -> list:
        """
            return dict with group ids
        """
        try:
            return eval(requests.post(f"{BaseApiUrl().get_api_url()}users.getSubscriptions", \
                                        data=self.__post_data()).text)['response']['groups']['items']
        except KeyError:
            return [f"{self.__post_data()['user_id']} close page"]

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
    
    
class GetFollowsByPosts:
    
    def __init__(self, post_list: list[str]):
        self.post_list = post_list
        
    def get_user_ids(self) -> list:
        user_ids = []
        for post in self.post_list:
            user_ids.append(\
                            GetLikersIds(link_for_post=post).get()
                           )
        return list(set(list(itertools.chain(*user_ids))))
    
    def get_user_subs(self) -> dict:
        user_ids = self.get_user_ids()
        user_subs = []
        for user in tqdm(user_ids):
            user_subs.append(\
                             GetPeopleFollows(user_id=user).get_all_ids()
                            )
        return user_subs
    
    def main(self): 
        return [_ for _ in list(itertools.chain(*self.get_user_subs())) if type(_) != str]
    
class GetGroupNames:
    
    def __init__(self, group_ids: list[int]):
        self.group_ids = group_ids 
    
    def __post_data(self, group_id):
        return {
            'access_token': LoginToken().get_login_token(),
            'group_id': group_id,
            'v': 5.131,
        }
    
    def get_group_name_by_id(self, group_id) -> str:
        return eval(requests.post(f"{BaseApiUrl().get_api_url()}groups.getById", \
                                     data = self.__post_data(group_id),
                                   ).text)['response'][0]['name']

    def create_dataframe(self, names: list['str']):
        df = pd.DataFrame()
        names = [k for k in names]
        df['names'] = names
        df.to_csv(f"temp/parsing_result{r.randint(1,1000)}.csv")
        return df

    def get_group_names(self, task_number):
        names = []
        for group_id in tqdm(self.group_ids):
            names.append(
                self.get_group_name_by_id(group_id)
            )
        return self.create_dataframe(names)

class GetParalleled:

    def __init__(self, group_ids):
        self.groups = group_ids 
    
    def get_25_quant(self):
        arr = self.groups 
        paralleled = [
            arr[int(len(arr) * .0) : int(len(arr) * .25)],
            arr[int(len(arr) * .25) : int(len(arr) * .5)],
            arr[int(len(arr) * .5) : int(len(arr) * .75)],
            arr[int(len(arr) * .75) : int(len(arr) * 1)],
        ]
        return paralleled 

    def get_10_quant(self):
        arr = self.groups 
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

class Runner:

    def print_wating(self):
        print()
        print()
        print("      * *        *            * ")
        print("  *        *            *       ") 
        print("     Wating for followers..     ")
        print("      * *        *   *          ") 
        print(" *        *            *        ")
        print()
        print()

    def main(self):
        self.print_wating()
        group_ids = GetFollowsByPosts(['https://vk.com/wall-105838386_18710']).main() 
        arrays = GetParalleled(group_ids).get_10_quant()
        tasks = [Process(target=GetGroupNames(array).get_group_names, args=(i,)) for array, i in zip(arrays, range(len(arrays)))]
        for _ in tasks:
            _.start()

class ConcatDataFrames:

    def __init__(self, directory):
        self.directory = directory

    def concat(self):
        names = []
        for file in os.listdir(self.directory):
            df = pd.read_csv(f"{self.directory}/{file}")
            for name in df['names']:
                names.append(name)
            os.remove(f"{self.directory}/{file}")
        new_df = pd.DataFrame()
        new_df['names'] = names
        counts = new_df['names'].value_counts()[:50]
        counts.to_csv("result.csv")

if __name__ ==  '__main__':

    Runner().main()

    while True:
        time.sleep(0.25)
        if len(os.listdir("temp")) >= 8:
            ConcatDataFrames("temp").concat()
            break