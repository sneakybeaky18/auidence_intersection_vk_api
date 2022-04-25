import asyncio
import aiohttp


class LoginToken:

    @staticmethod
    def get_login_token() -> str:
        with open("token.txt") as f:
            lines = f.readlines()
            for line in lines:
                return str(line).replace("\n", "")


class Groups:

    @staticmethod
    def post_data(posts: list[str]):
        return {
            'access_token': LoginToken().get_login_token(),
            'group_ids': ",".join(posts),
            'v': 5.131,
        }

    async def get_by_id(self, posts: list[str]):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.vk.com/method/groups.getById', data=self.post_data(posts)) as response:
                text = await response.text()
                return eval(str(text).replace("true", "True").replace("false", "False"))['response']


class Wall:

    @staticmethod
    def post_data(owner_id: str):
        return {
            'access_token': LoginToken().get_login_token(),
            'owner_id': f"-{owner_id}",
            'offset': 0,
            'count': 100,
            'v': 5.131,
        }

    async def get(self, owner_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.vk.com/method/wall.get', data=self.post_data(owner_id)) as response:
                text = await response.text()
                return eval(str(text).replace("true", "True").replace("false", "False"))['response']


class Likes:

    @staticmethod
    def post_data(owner_id: str, item_id: str):
        return {
            'access_token': LoginToken().get_login_token(),
            'type': 'post',
            'owner_id': owner_id,
            'item_id': item_id,
            'offset': 0,
            'count': 999,
            'v': 5.131,
        }

    async def get_list(self, owner_id: str, item_id: str):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post('https://api.vk.com/method/likes.getList', data=self.post_data(owner_id, item_id)) \
                        as response:
                    text = await response.text()
                    return eval(str(text).replace("true", "True").replace("false", "False"))['response']
            except Exception as e:
                print(e)
