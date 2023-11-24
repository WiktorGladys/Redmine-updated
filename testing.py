from collections import namedtuple
import json
import random
import logging
from datetime import date
from typing import List, NamedTuple
from redminelib import Redmine
from icecream import ic
from pydantic import BaseModel
import docker
from rocketchat_API.rocketchat import RocketChat
from pprint import pprint
REDMINE_URL: str = "http://172.17.0.2:3000/"
REDMINE_USERNAME: str = "admin"
REDMINE_PASSWORD: str = "admin123"
redmine = Redmine(url=REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWORD)
# redmine.project_membership.create(project_id='testing',user_id=7,role_ids=[3,5])
# redmine.issue.create(
#     project_id="testing",
#     subject="TEST",
#     assigned_to_id=5,
#     tracker_id=1,
#     priority_id=1
# )
rocket: RocketChat = RocketChat(
    "wiktor_gladys", "admin123", server_url="http://172.27.0.3:3000"
)
data = rocket.users_list().json()
# user_id = []
# for elem in data["users"]:
#     if 'admin' in elem["roles"]:
#         id_admin = elem["_id"]
#     user_id.append(elem["_id"])
# for elem in user_id:
#     ic(id_admin+elem)
#     rocket.chat_post_message("test",id_admin+elem)

# pprint(rocket.users_list().json())
# data = rocket.users_list().json()
# pprint((data["users"]))
# pprint(data["users"][0]["_id"])
# pprint(rocket.rooms_get().json())
# rocket.chat_post_message("test1111","iadJAcWiW3JiAXedeiSZJi8oZoCKkycLrj")
pprint(rocket.channels_list().json())