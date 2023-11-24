"""Script to manage redmine project
    Created: 17.11.2023
    Author: Wiktor Glądys
"""
from collections import namedtuple
import random
import logging
from datetime import date
from typing import List, NamedTuple
from redminelib import Redmine
from icecream import ic
from pydantic import BaseModel
import docker
from rocketchat_API.rocketchat import RocketChat

logging.basicConfig(filename="example.log", encoding="utf-8", level=logging.INFO)
# logging.basicConfig(filename="warns.log", encoding="utf-8", level=logging.WARNING)
client: docker.client.DockerClient = docker.from_env()

if client.containers.get("3c155e01967d"):
    pass
else:
    container: docker.models.containers.Container = client.containers.run(
        "configured", name="redmine_test", detach=True
    )


class RedmineConfig(BaseModel):
    """Base model used to create RedmineManager class"""
    url: str
    username: str
    password: str
    project_id: str
    status_id_complete: int
    status_id_ready: int
    tracker_id: int
    priority_id: int
    url_rockect: str
    username_rocket: str
    password_rocket: str
    oldest: str


class RedmineManager:
    """Class to manage a project"""

    def __init__(self, config: RedmineConfig):
        self.redmine = Redmine(
            config.url, username=config.username, password=config.password
        )
        self.rocket: RocketChat = RocketChat(
            config.username_rocket,
            config.password_rocket,
            server_url=config.url_rockect,
        )
        self.project_id: str = config.project_id
        self.tracker_id: int = config.tracker_id
        self.priority_id: int = config.priority_id
        self.status_id_ready: int = config.status_id_ready
        self.status_id_complete: int = config.status_id_complete
        self.oldest = config.oldest
        self.issues = self.redmine.issue.filter(project_id=config.project_id)
        self.list_ = self.prepare_list()
        self.users = self.get_users()

    def create_user(
        self, login: str, password: str, firstname: str, lastname: str, email: str
    ) -> None:
        """Creates User from args"""
        self.redmine.user.create(
            login=login,
            password=password,
            firstname=firstname,
            lastname=lastname,
            mail=email,
        )

    def create_memberships(self):
        """Creates memberships for project"""
        for elem in self.users:
            self.redmine.project_membership.create(
                project_id=self.project_id, user_id=elem, role_ids=[3, 5]
            )

    def create_new_version(self, version_name: str) -> None:
        """Creates versions"""
        self.redmine.version.create(project_id=self.project_id, name=version_name)

    def update_issues(self) -> None:
        """Updates variable issues"""
        self.issues = self.redmine.issue.filter(project_id=self.project_id)
        ic(self.issues)

    def _create_task(self, name: str) -> None:
        """Creates Tasks"""
        rand_num_from_list: int = random.choice(self.users)
        ic(rand_num_from_list)
        issue = self.redmine.issue.create(
            project_id=self.project_id,
            subject=name,
            tracker_id=self.tracker_id,
            priority_id=self.priority_id,
            assigned_to_id=rand_num_from_list,
        )
        return issue

    def create_relation(self, id_first: int, id_second: int) -> None:
        """Create relation between tasks"""
        ic(id_first)
        id(id_second)
        self.redmine.issue_relation.create(
            issue_id=id_second, issue_to_id=id_first, relation_type="blocked"
        )

    def find_task(self, name_to_find: str) -> int:
        """Takes Subject Name and returns its ID"""
        for elem in self.issues:
            name: str = getattr(elem, "subject")
            if name_to_find == name:
                id_of_searched_task: int = getattr(elem, "id")
                return id_of_searched_task
        return 0

    def prepare_list(self) -> List[NamedTuple]:
        """Prepares List from graph on wiki"""
        ic(self.project_id)
        wiki_page = self.redmine.wiki_page.get("Foo", project_id=self.project_id)
        list_process: str = wiki_page.text
        list_process = list_process.replace('"', "")
        list_process = list_process.replace("\n", "")
        list_process = list_process.replace("\r", "")
        list_completed: List[str] = list_process.split(";")
        new_list: List[NamedTuple] = []
        task = namedtuple("task", ["left", "right"])
        for elem in list_completed[: len(list_completed) - 1]:
            temp_list = elem.split("->")
            new_list.append(task(temp_list[0].strip(), temp_list[1].strip()))
        ic(new_list)
        return new_list

    def check_if_in(self, elem_left, elem_right, checking_list):
        """Creates tasks"""
        if elem_left in checking_list:
            if elem_right in checking_list:
                self.find_task(elem_left)
                self.find_task(elem_right)
                # done
            else:
                self._create_task(elem_right)
                checking_list.append(elem_right)
                logging.info("Sucessfully added task %s", elem_right)
                self.find_task(elem_left)
                # done
        else:
            self._create_task(elem_left)
            logging.info("Sucessfully added task %s", elem_left)
            checking_list.append(elem_left)
            if elem_right in checking_list:
                self.find_task(elem_right)
            else:
                self._create_task(elem_right)
                logging.info("Sucessfully added task %s", elem_right)
                checking_list.append(elem_right)

    def init_project(self) -> None:
        """Initialize project from graph on wiki"""
        checking_list: List[str] = []
        self.update_issues()
        for elem in self.list_[: len(self.list_) - 1]:
            self.check_if_in(elem.left, elem.right, checking_list)
        self.update_issues()

    def init_relations(self) -> None:
        """Initializes relation creation"""
        for elem in self.list_:
            first: int = self.find_task(elem.left)
            second: int = self.find_task(elem.right)
            self.create_relation(first, second)
            logging.info("Sucessfully added relation")
        self.update_issues()

    def get_number(self, issue_subject: str) -> int:
        """Gets task, returns number of subtasks"""
        number: int = 0
        for elem in self.list_[: len(self.list_) - 1]:
            if issue_subject in elem.right:
                number = number + 1
        return number

    def get_ids(self, issue_subject: str) -> List[int]:
        """Gets task, returns IDs of  subtasks"""
        ids = []
        for elem in self.list_[: len(self.list_) - 1]:
            if issue_subject in elem.right:
                ids.append(self.find_task(elem.left))
        return ids

    def get_users(self):
        """Returns user ids"""
        users_ids = []
        users = self.redmine.user.filter(project_id=self.project_id)
        print(list(users))
        for elem in users:
            id_of_user = getattr(elem, "id")
            users_ids.append(id_of_user)
        return users_ids

    def _check_status(self, issue_subject: str) -> int:
        """Gets task, returns number of completed subtasks"""
        number: int = 0
        for elem in self.list_[: len(self.list_) - 1]:
            if issue_subject in elem.right:
                issue_get = self.redmine.issue.get(self.find_task(elem.left))
                number += self._issue_status_check(issue_get)
        return number

    def _issue_status_check(self, issue) -> int:
        """Gets issue and checks if status is completed"""
        number: int = 0
        if issue.status.id == self.status_id_complete:
            number = 1
        return number

    def _notification(self, id_of_issue: int) -> None:
        """Notification"""
        with open("gotowe_do_realizacji.txt", "w", encoding="utf8") as file:
            file.write(f"Task o id {id_of_issue} jest Gotowy do realizacji\n")
            file.close()

    def create_user_in_rocket_chat(self):
        """Creates Users in rocket chat from redmine users"""
        for elem in self.users:
            user = self.redmine.user.get(elem)
            self.rocket.users_create(
                email=user.mail,
                name=user.login,
                password=user.firstname,
                username=user.firstname + user.lastname,
            )

    def clean_rocket_chat(self) -> None:
        """Cleans rocket bot chat"""
        now: str = str(date.today())
        now = now + "T13:34:32.603Z"
        data = self.rocket.rooms_get().json()
        ic(data["update"][0]["_id"])
        for elem in data["update"]:
            self.rocket.rooms_clean_history(
                elem["_id"], latest=now, oldest=self.oldest
            )
        logging.info("Cleaned rocket chat")

    def _send_message_to_all_users(self, message_body) -> None:
        """Notification on rocket chat"""
        ic(self.rocket.rooms_get().json())
        data = self.rocket.users_list().json()
        user_id_rocketchat = []
        for elem in data["users"]:
            if "admin" in elem["roles"]:
                id_admin = elem["_id"]
            user_id_rocketchat.append(elem["_id"])
        for elem in user_id_rocketchat:
            if self.rocket.chat_post_message(message_body, elem + id_admin):
                ic("True")
            self.rocket.chat_post_message(message_body, id_admin + elem)

    def get_admin_rocketchat(self):
        """Returns rocketchat admin's id"""
        data = self.rocket.users_list().json()
        for elem in data["users"]:
            if "admin" in elem["roles"]:
                return elem["_id"]

    def _send_message_to_single_user(self, id_of_issue: int, username: str) -> None:
        data = self.rocket.users_list().json()
        ic(self.rocket.rooms_get().json())
        for elem in data["users"]:
            if elem["username"] == username:
                ic("wejscie")
                id_admin = self.get_admin_rocketchat()
                ic(id_admin)
                ic(elem["_id"])
                if self.rocket.chat_post_message(f"Task o id {id_of_issue} jest gotowy do realizacji",id_admin + elem["_id"],):
                    logging.info("Sended message to User")
                    return
                self.rocket.chat_post_message(f"Task o id {id_of_issue} jest gotowy do realizacji",elem["_id"] + id_admin)
                logging.info("Sended message to User")
                return

    def delete_all(self) -> None:
        """Deletes all issues"""
        if self.issues is not None:
            for elem in self.issues:
                elem.delete()
                logging.info("Deleted task %s", elem.subject)
        else:
            print("First initialize project")
            logging.info("Tried to delete when project is not initialized")
    def get_username(self, username_with_space: str) -> str:
        return username_with_space.replace(" ", "")
    def update(self) -> None:
        """Updates Redmine by reading graph from wiki"""
        for elem in self.list_[: len(self.list_) - 1]:
            first: int = self.find_task(elem.left)
            second: int = self.find_task(elem.right)
            issue = self.redmine.issue.get(first)
            issue_second = self.redmine.issue.get(second)
            number_of_completed_tasks: int = 0
            if (
                issue.status.id is self.status_id_complete
                and issue_second.status.id is not self.status_id_ready
                and issue_second.status.id is not self.status_id_complete
            ):
                number_of_completed_tasks = self._check_status(issue_second.subject)
            else:
                continue
            if number_of_completed_tasks == self.get_number(issue_second.subject):
                issue_second.status_id = self.status_id_ready
                issue_second.save()
                logging.info(
                    "Succesfully updated status of task %s ", issue_second.subject
                )
                self._notification(second)
                self._send_message_to_single_user(second, self.get_username(issue_second.assigned_to.name))
                # self._send_message(second)
            else:
                logging.info("No tasks to update!")
