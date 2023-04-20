import json
from dotenv import dotenv_values
import time

from datetime import datetime
import telegram

from vk_publishing import publish_post


def get_json_posts(file_name):
    with open(file_name, "r", encoding="UTF-8") as file:
        posts_data = json.load(file)
    return posts_data["posts"]


def publish_posts_if_time(tg_bot, vk_group_id, vk_acess_token, posts):
    while True:
        for post in posts:
            post_date = post["publication_date"]
            post_time = post["publication_time"]

            currtime = datetime.now()
            post_datetime = datetime.strptime(f"{post_date} {post_time}", "%d.%m.%y %H:%M")
            if currtime > post_datetime and post["status"] == "not_publicated":
                with open(post["image"], 'rb') as image:
                    if post["where"] == "tg":
                        tg_bot.send_photo(
                            chat_id=chat_id,
                            photo=image,
                            caption=post["text"]
                        )
                    elif post["where"] == "vk":
                        publish_post(post["text"], post["image"], vk_group_id, vk_acess_token)
                    else:
                        tg_bot.send_photo(
                            chat_id=chat_id,
                            photo=image,
                            caption=post["text"]
                        )
                        publish_post(post["text"], post["image"], vk_group_id, vk_acess_token)
                post["status"] = "publicated"
        time.sleep(10)


if __name__ == "__main__":
    tg_bot = telegram.Bot(dotenv_values(".env")["BOT_TOKEN"])
    chat_id = dotenv_values(".env")["CHAT_ID"]
    vk_group_id = int(dotenv_values(".env")["GROUP_ID"])
    vk_acess_token = dotenv_values(".env")["ACESS_TOKEN"]
    posts = get_json_posts("posts.json")
    publish_posts_if_time(tg_bot, vk_group_id, vk_acess_token, posts)
