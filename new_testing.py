from redminelib import Redmine
import testing_variant
from pydantic import BaseModel
from icecream import ic
import pytest
def create_project(name_of_project: str) -> None:
    redmine.project.create(name=name_of_project, identifier=name_of_project.lower())
    return name_of_project.lower()
def create_wiki_page(title: str) -> None:
    f = open("graph.txt", "r")
    redmine.wiki_page.create(project_id="testing", title=title, text=f.read())
# Configuration
REDMINE_URL: str = "http://172.17.0.2:3000/"
REDMINE_USERNAME: str = "admin"
REDMINE_PASSWORD: str = "admin123"
ROCKETCHAT_URL: str = "http://172.18.0.2:3000"
ROCKETCHAT_USERNAME = "wiktor_gladys"
ROCKETCHAT_PASSWORD = "admin123"
STATUS_ID_COMPLETE: int = 4
STATUS_ID_READY: int = 3
STATUS_ID_NEW: int = 1
TRACKER_ID: int = 1
PRIORITY_ID: int = 1
OLDEST: str = "2016-05-30T13:42:25.304Z"
redmine = Redmine(
    url=REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWORD
)
PROJECT_ID = create_project("Testing")
redmine_config = testing_variant.RedmineConfig(
    url=REDMINE_URL,
    username=REDMINE_USERNAME,
    password=REDMINE_PASSWORD,
    project_id=PROJECT_ID,
    status_id_complete=STATUS_ID_COMPLETE,
    status_id_ready=STATUS_ID_READY,
    tracker_id=TRACKER_ID,
    priority_id=PRIORITY_ID,
    url_rockect=ROCKETCHAT_URL,
    username_rocket=ROCKETCHAT_USERNAME,
    password_rocket=ROCKETCHAT_PASSWORD,
    oldest=OLDEST
)
create_wiki_page("Foo")
redmine_manager = testing_variant.RedmineManager(redmine_config)

def setup():
    # redmine_manager.create_user("test8956","test123456","Jan1","Nowak", "examp1le@op.pl")
    # redmine_manager.create_user("test123675","test456789","Jan1","Banas","example21137@op.pl")
    redmine_manager.create_memberships()


#TESTS
@pytest.fixture
def delete_all_fix():
    """Pytest fixture deletes all taska"""
    redmine_manager.delete_all()

@pytest.fixture
def project_init():
    """Pytest fixture initializes project"""
    redmine_manager.init_project()
@pytest.fixture
def project_init_relations():
    redmine_manager.init_relations()
def test_if_initialized(project_init, project_init_relations):
    assert redmine.issue.all() is not None
    # redmine_manager.create_user_in_rocket_chat()
    # redmine_manager._send_message_to_all_users("12345436456")
def test_if_users_are_created(delete_all_fix, project_init, project_init_relations):
    assert redmine_manager.get_users() is not None
def test_realtions(delete_all_fix, project_init, project_init_relations):
    issue = redmine.issue.get(1)
    print(len(issue.relations))
    assert len(issue.relations) is not None
# def test_memberships(delete_all_fix, project_init, project_init_relations):
#     pass
def teardown():
    redmine.project.delete(PROJECT_ID)
    redmine_manager.clean_rocket_chat()
# update()