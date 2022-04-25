import asyncio
import time
from modules import Groups, Wall, Likes
from tqdm import tqdm


analyse = 0


async def entry(id_of_group):
    global analyse
    group_id = await Groups().get_by_id([id_of_group])
    post_list = await Wall().get(group_id[0]['id'])
    post_ids, owner_ids = [], []
    for post in tqdm(post_list['items']):
        post_ids.append(post['id'])
        owner_ids.append(post['owner_id'])

    for post, owner in zip(post_ids, owner_ids):
        result = await Likes().get_list(owner, post)
        with open('retarget.txt', 'a') as file:
            for item in result['items']:
                analyse += 1
                file.write(f"{item}\n")


async def main():
    task_list = []
    with open("urls.txt", encoding='utf-8') as f:
        lines = f.readlines()
        for line in tqdm(lines):
            line = line.replace("\n","")
            task = asyncio.create_task(entry(line))
            task_list.append(task)
    await asyncio.gather(*task_list, return_exceptions=True)


def get_unique_people():
    peoples = []
    with open("retarget.txt") as f:
        for line in f.readlines():
            peoples.append(line.replace("\n",""))
    unique = list(set(peoples))
    print(f"Analysed more then {len(unique)} people")
    with open("clean_retarget.txt", "a") as f:
        for uni in unique:
            f.write(f"{uni}\n")


if __name__ == '__main__':
    start = time.time()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
    print(f"Finished for {time.time() - start} seconds")
    get_unique_people()
