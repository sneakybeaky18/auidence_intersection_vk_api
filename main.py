import time
import requests
import itertools
import pandas as pd 
from collections import Counter

class BaseApiUrl:
    
    def get_api_url(self) -> str:
        return 'https://api.vk.com/method/'

class LoginToken:
    
    def get_login_token(self) -> str:
        return "<provide token>"
    
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
        for user in user_ids:
            user_subs.append(\
                             GetPeopleFollows(user_id=user).get_all_ids()
                            )
        return user_subs
    
    def main(self): 
        return [_ for _ in list(itertools.chain(*self.get_user_subs())) if type(_) != str]
    
class GetGroupNames:
    
    def control_time(func):
        def decorator(self):
            start = time.time()
            result = func(self)
            print("Completed for ", time.time() - start, " seconds")
            return result
        return decorator
    
    def __init__(self, group_ids: list[int]):
        self.group_ids = group_ids 
    
    def __post_data(self, group_id):
        return {
            'access_token': LoginToken().get_login_token(),
            'group_id': group_id,
            'v': 5.131,
        }
    
    def get_group_name_by_id(self, group_id):
        return eval(requests.post(f"{BaseApiUrl().get_api_url()}groups.getById", \
                                     data = self.__post_data(group_id),
                                   ).text)['response'][0]['name']

    def create_dataframe(self, names):
        df = pd.DataFrame()
        items = []
        frequency = []
        for value in Counter(names).items():
            items.append(value[0])
            frequency.append(value[1])
        df['items'] = items
        df['frequency'] = frequency
        df.to_csv("parsing_result.csv")
        return df

    @control_time
    def get_group_names(self):
        names = []
        i = 0
        for group_id in self.group_ids:
            if i % 10 == 0:
                print(i, "/", len(self.group_ids))
            names.append(
                self.get_group_name_by_id(group_id)
            )
            i += 1
        return self.create_dataframe(names)


# Contains urls for post you want to parse
group_ids = GetFollowsByPosts(['https://vk.com/wall-105838386_18710', 
                               'https://vk.com/wall-105838386_18710', 
                               'https://vk.com/wall-105838386_18710']).main()
counter_names = GetGroupNames(group_ids).get_group_names()
# Generating csv file with counter