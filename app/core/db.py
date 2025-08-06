# app/core/db.py

import motor.motor_asyncio
from dotenv import load_dotenv
import os

load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL"))

# Alteramos o nome do banco de dados para algo mais apropriado
database = client["blog"]

# Definindo as novas coleções para o nosso sistema de Blog
post_collection = database["posts"]
category_collection = database["categories"]
tag_collection = database["tags"]
comment_collection = database["comments"]
post_tag_collection = database["post_tags"] # Para a associação N:N
user_collection = database["users"]
post_like_collection = database["post_likes"]