"""Script to manage redmine project
    Created: 17.11.2023
    Author: Wiktor Glądys
"""
from collections import namedtuple
import logging
from datetime import date
from typing import List, NamedTuple
from redminelib import Redmine
from icecream import ic
from pydantic import BaseModel
import docker
from rocketchat_API.rocketchat import RocketChat

rocket: RocketChat = RocketChat(
    "wiktor_gladys", "admin123", server_url="http://localhost:3000"
)
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
    url: str
    username: str
    password: str
    project_id: str
    status_id_complete: int
    status_id_ready: int
    tracker_id: int
    priority_id: int


class RedmineManager:
    """Class to manage a project"""

    def __init__(self, config: RedmineConfig):
        self.redmine = Redmine(
            config.url,
            username=config.username,
            password=config.password
        )
        self.project_id = config.project_id
        self.status_id_complete = config.status_id_complete
        self.status_id_ready = config.status_id_ready
        self.tracker_id = config.tracker_id
        self.priority_id = config.priority_id
        self.issues = self.redmine.issue.filter(project_id=config.project_id)

    def _create_task(self, name: str):
        """Creates Tasks"""
        issue = self.redmine.issue.create(
            project_id=self.project_id,
            subject=name,
            tracker_id=self.tracker_id,
            priority_id=self.priority_id,
        )
        return issue

    def create_relation(self, id_first: int, id_second: int) -> None:
        """Create relation between tasks"""
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
        for elem in list_[: len(list_) - 1]:
            self.check_if_in(elem.left, elem.right, checking_list)

    def init_relations(self) -> None:
        """Initializes relation creation"""
        for elem in list_[: len(list_) - 1]:
            first: int = self.find_task(elem.left)
            second: int = self.find_task(elem.right)
            self.create_relation(first, second)
            logging.info("Sucessfully added relation")

    def get_number(self, issue_subject: str) -> int:
        """Gets task, returns number of subtasks"""
        number: int = 0
        for elem in list_[: len(list_) - 1]:
            if issue_subject in elem.right:
                number = number + 1
        return number

    def get_ids(self, issue_subject: str) -> List[int]:
        """Gets task, returns IDs of  subtasks"""
        ids = []
        for elem in list_[: len(list_) - 1]:
            if issue_subject in elem.right:
                ids.append(self.find_task(elem.left))
        return ids

    def _check_status(self, issue_subject: str) -> int:
        """Gets task, returns number of completed subtasks"""
        number: int = 0
        for elem in list_[: len(list_) - 1]:
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

    def clean_rocket_chat(self) -> None:
        """Cleans rocket bot chat"""
        now: str = str(date.today())
        now = now + "T13:34:32.603Z"
        rocket.rooms_clean_history(room_id=ROOM_ID, latest=now, oldest=OLDEST)
        logging.info("Cleaned rocket chat")

    def _send_message(self, id_of_issue: int) -> None:
        """Notification on rocket chat"""
        rocket.chat_post_message(
            f"Task o id {id_of_issue} jest Gotowy do realizacji", ROOM_ID
        )
        logging.info("Sended message to rocket chat")

    def delete_all(self) -> None:
        """Deletes all issues"""
        for elem in self.issues:
            elem.delete()
            logging.info("Deleted task %s", elem.subject)

    # @property
    # def get_issue(self, id_of_task: int):
    #     """Returns issue of given ID"""
    #     return self.redmine.issue.get(id_of_task)
    # @property
    # def get_issues(self):
    #     """Returns all issues"""
    #     return self.issues

    def update(self) -> None:
        """Updates Redmine by reading graph from wiki"""
        for elem in list_[: len(list_) - 1]:
            first: int = self.find_task(elem.left)
            second: int = self.find_task(elem.right)
            issue = self.redmine.issue.get(first)
            issue_second = self.redmine.issue.get(second)
            number_of_completed_tasks: int = 0
            if (
                issue.status.id == self.status_id_complete
                and issue_second.status.id != self.status_id_ready
                and issue_second.status.id != self.status_id_complete
            ):
                ic(123)
                number_of_completed_tasks = self._check_status(issue_second.subject)
            if number_of_completed_tasks == self.get_number(issue_second.subject):
                issue_second.status_id = self.status_id_ready
                issue_second.save()
                logging.info(
                    "Succesfully updated status of task %s ", issue_second.subject
                )
                self._notification(second)
                self._send_message(second)


# Configuration
REDMINE_URL: str = "http://172.17.0.2:3000/"
REDMINE_USERNAME: str = "admin"
REDMINE_PASSWORD: str = "admin123"
PROJECT_ID: str = "testing"
STATUS_ID_COMPLETE: int = 4
STATUS_ID_READY: int = 3
STATUS_ID_NEW: int = 1
TRACKER_ID: int = 1
PRIORITY_ID: int = 1
ROOM_ID: str = "aQTNDBmpk2jDXBCLTu7bXji4aeLzsMFCgE"
OLDEST: str = "2016-05-30T13:42:25.304Z"
redmine_config = RedmineConfig(
    url = REDMINE_URL,
    username = REDMINE_USERNAME,
    password = REDMINE_PASSWORD,
    project_id = PROJECT_ID,
    status_id_complete = STATUS_ID_COMPLETE,
    status_id_ready = STATUS_ID_READY,
    tracker_id = TRACKER_ID,
    priority_id = PRIORITY_ID,
)
redmine_manager = RedmineManager(redmine_config)
# INITIALIZATION
list_: List[NamedTuple] = redmine_manager.prepare_list()
# ic(list_)
# redmine_manager.delete_all()
# redmine_manager.init_project()
# redmine_manager.init_relations()
redmine_manager.update()
redmine_manager.clean_rocket_chat()
