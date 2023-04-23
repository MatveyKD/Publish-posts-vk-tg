from dotenv import dotenv_values
import time

from datetime import datetime
import telegram

from vk_publishing import publish_post
from load_googlesheets import load_googlesheets_to_json, change_status, get_status

import json


def get_json_posts(file_name):
    with open(file_name, "r", encoding="UTF-8") as file:
        posts_data = json.load(file)
    return posts_data


def publish_posts_if_time(tg_bot, vk_group_id, vk_acess_token, posts):
    for index, post in enumerate(posts):
        post_date = post["date"]
        post_time = post["time"]

        currtime = datetime.now()
        post_datetime = datetime.strptime(f"{post_date} {post_time}", "%d.%m.%Y %H.%M.%S")
        if currtime > post_datetime and get_status(index) != "Опубликовано":
            with open(post["img"], 'rb') as image:
                if post["platform"] == "TG":
                    tg_bot.send_photo(
                        chat_id=chat_id,
                        photo=image,
                        caption=post["text"]
                    )
                elif post["platform"] == "VK":
                    publish_post(post["text"], post["img"], vk_group_id, vk_acess_token)
                else:
                    tg_bot.send_photo(
                        chat_id=chat_id,
                        photo=image,
                        caption=post["text"]
                    )
                    publish_post(post["text"], post["img"], vk_group_id, vk_acess_token)
            change_status(index, "Опубликовано")


if __name__ == "__main__":
    tg_bot = telegram.Bot(dotenv_values(".env")["BOT_TOKEN"])
    chat_id = dotenv_values(".env")["CHAT_ID"]
    vk_group_id = int(dotenv_values(".env")["GROUP_ID"])
    vk_acess_token = dotenv_values(".env")["ACESS_TOKEN"]
    json_filename = "data.json"
    while True:
        load_googlesheets_to_json(json_filename)
        posts = get_json_posts(json_filename)
        publish_posts_if_time(tg_bot, vk_group_id, vk_acess_token, posts)
        time.sleep(10)
