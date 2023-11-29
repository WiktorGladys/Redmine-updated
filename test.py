from pydantic import BaseModel
import json
from redminelib import Redmine
from pytest import Parser
redmine = Redmine(url="http://172.21.0.3:3000/", username="admin", key="68cb9ed2a4f1413445588a0d9073f8a6b0f4044b")

# importing required modules
import argparse
# parser = argparse.ArgumentParser(description = "An addition program")
# parser.add_argument("-nw","--wiki_page_name", metavar = "wiki_page_string", type = str, 
# 					help = "Enter name of wiki page.")
# parser.add_argument("-np","--project_id_name", metavar = "project_id_string", type = str, 
# 					help = "Enter name of project")
# args = parser.parse_args()
# args.wiki_page_name = "testeee"
# args.project_name = "Foo"
# check if add argument has any input data.
# If it has, then print sum of the given numbers
# print(args.project_name)
# with open('data_testing.json') as json_file:
#     data = json.load(json_file)
# print(data)
# if data["wiki_page_name"] == "":
#     data["wiki_page_name"] = args.wiki_page_name
# if data["project_name"] == "":
#     data["project_name"] = args.project_name
# print(data)
user_admin = redmine.user.all
for elem in redmine.user.all():
    if elem.id != 1:
        redmine.user.delete(elem.id)
    print(elem.id)

