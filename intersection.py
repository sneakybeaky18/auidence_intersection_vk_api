from tqdm import tqdm
import asyncio
import aiohttp
from modules import LoginToken
import pandas as pd
import time

def batch(iterable, n=1):
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


class Users:

    @staticmethod
    def post_data(user_id: str):
        return {
            'access_token': LoginToken.get_login_token(),
            'user_id': user_id,
            'extended': 1,
            'offset': 0,
            'count': 20,
            'v': 5.131,
        }

    async def get(self, user_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.vk.com/method/users.getSubscriptions',
                                    data=self.post_data(user_id)) as response:
                text = await response.text()
                return eval(str(text).replace("true", "True").replace("false", "False"))['response']


async def write_to_file(user_id: str):
    result = await Users().get(user_id=user_id)
    with open("names.txt", "a", encoding='utf-8') as f:
        for item in result['items']:
            f.write(f"{str(item['name'])}\n")


async def main():
    with open("clean_retarget.txt") as f:
        for array in tqdm(batch(f.readlines(), 500)):
            task_list = []
            for line in tqdm(array):
                line = line.replace('\n', '')
                task_list.append(
                    asyncio.create_task(
                        write_to_file(line)
                    )
                )
            await asyncio.gather(*task_list, return_exceptions=True)


def process_dataframe():
    values = []
    with open('names.txt', encoding='utf-8') as f:
        for line in f.readlines():
            values.append(line.replace("\n", ""))
    dataframe = pd.DataFrame()
    dataframe['values'] = values
    dataframe = dataframe['values'].value_counts()
    dataframe.to_csv("result.csv")


def get_values() -> int:
    with open('names.txt', encoding='utf-8') as f:
        value = len(f.readlines())
        return value


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start = time.time()
    asyncio.run(main())
    end = start - time.time()
    print("Finished for", end, " seconds \n", "Values processed: ", get_values())
    process_dataframe()
