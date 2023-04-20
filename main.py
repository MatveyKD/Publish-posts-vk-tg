import json
from dotenv import dotenv_values
import time

from datetime import datetime
import telegram


def get_json_posts(file_name):
    with open("posts.json", "r", encoding="UTF-8") as file:
        posts_data = json.load(file)
    return posts_data["posts"]


def publish_posts_if_time(posts):
    while True:
        for post in posts:
            post_date = post["publication_date"]
            post_time = post["publication_time"]

            currtime = datetime.now()
            post_datetime = datetime.strptime(f"{post_date} {post_time}", "%d.%m.%y %H:%M")
            if currtime > post_datetime and post["status"] == "not_publicated":
                with open(post["image"], 'rb') as image:
                    bot.send_photo(
                        chat_id=chat_id,
                        photo=image,
                        caption=post["text"]
                    )
                    post["status"] = "publicated"
        time.sleep(10)


if __name__ == "__main__":
    bot = telegram.Bot(dotenv_values(".env")["BOT_TOKEN"])
    chat_id = dotenv_values(".env")["CHAT_ID"]
    posts = get_json_posts("posts.json")
    publish_posts_if_time(posts)
