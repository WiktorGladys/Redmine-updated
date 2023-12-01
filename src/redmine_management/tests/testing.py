import sys
import argparse
import json
import redminelib
from redminelib import Redmine
from pydantic import BaseModel
from icecream import ic
import pytest

sys.path.append("src/redmine_management/app")
import app


def create_project(name_of_project: str) -> None:
    try:
        redmine.project.create(name=name_of_project, identifier=name_of_project.lower())
    except Exception as e:
        print(f"Error creating project: {e}")


def create_wiki_page(title: str) -> None:
    try:
        with open("graph.txt", "r") as f:
            redmine.wiki_page.create(
                project_id=redmine_config.project_name.lower(),
                title=title,
                text=f.read(),
            )
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except redminelib.exceptions.ResourceNotFoundError as e:
        print(f"Error creating wiki page: {e}")


def init_parser() -> None:
    """Creating parser, project and wiki page"""
    parser = argparse.ArgumentParser(description="An addition program")
    parser.add_argument(
        "wiki_page_name",
        nargs="?",
        metavar="wiki_page_string",
        type=str,
        help="Enter name of wiki page.",
        default="Initialized graph",
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        metavar="project_id_string",
        type=str,
        help="Enter name of project",
        default="testing",
    )
    args = parser.parse_args()
    args.wiki_page_name = "Initialized graph"
    if data["project_name"] == "":
        redmine_config.project_name  = args.project_name
        create_project(args.project_name)
    else:
        create_project(data["project_name"])
    if data["wiki_page_name"] == "":
        redmine_config.wiki_page_name = args.wiki_page_name
        create_wiki_page(args.wiki_page_name)
    else:
        create_wiki_page(data["wiki_page_name"])


# Loading json file with config
with open("data_testing.json") as json_file:
    data = json.load(json_file)

redmine_config = app.RedmineConfig(**data)
if redmine_config.key != "":
    redmine = Redmine(url=redmine_config.url, key=redmine_config.key)
else:
    redmine = Redmine(
        url=redmine_config.url,
        username=redmine_config.username,
        password=redmine_config.password,
    )

init_parser()
redmine_manager = app.RedmineManager(redmine_config)


def setup():
    """Setup enviroment for testing"""
    redmine_manager.create_user(
        "test8956", "test123456", "Jan1", "Nowak", "examp1le@op.pl"
    )
    redmine_manager.create_user(
        "test123675", "test456789", "Jan1", "Banas", "example21137@op.pl"
    )
    redmine_manager.create_user_in_rocket_chat()
    redmine_manager.create_memberships()


# TESTS
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
    """Pytest fixture initializes relations in project"""
    redmine_manager.init_relations()


def test_if_users_are_created():
    """Test if users are created"""
    assert len(redmine_manager.get_users()) > 1


def test_memberships():
    """Test if membership have been initialized"""
    assert (
        redmine.project_membership.filter(
            project_id=redmine_config.project_name.lower()
        )
        is not None
    )


def test_create_project():
    """Test if project creation is working properly"""
    PROJECT_NAME = "test_create_project"
    redmine_manager.create_project(PROJECT_NAME)
    assert redmine.project.get(PROJECT_NAME)
    redmine.project.delete(PROJECT_NAME)


def test_wiki_page():
    """Test to check wiki page creation"""
    WIKI_PAGE_NAME = "test_creation_wiki_page"
    FILE_PATH = "graph.txt"
    redmine_manager.create_wiki_page(WIKI_PAGE_NAME, FILE_PATH)
    assert redmine.wiki_page.get(
        WIKI_PAGE_NAME, project_id=redmine_config.project_name
    )


def test_if_initialized(project_init, project_init_relations):
    """Test to check if initialized properly"""
    assert redmine.issue.all() is not None
    # redmine_manager.create_user_in_rocket_chat()
    # redmine_manager._send_message_to_all_users("12345436456")


def test_realtions(delete_all_fix, project_init, project_init_relations):
    """Test if relations are initialized"""
    for elem in redmine.issue.filter(project_id=redmine_config.project_name.lower()):
        assert len(elem.relations) is not None


def find_issue_with_dependencies():
    """Finds issue with more than 3 dependecies"""
    issues = redmine_manager.get_issues
    for elem in issues:
        number = redmine_manager.get_number(elem.subject)
        if number >= 3:
            return elem


def test_auto_multi(delete_all_fix, project_init, project_init_relations):
    """Test multi dependency"""
    issue = find_issue_with_dependencies()
    ids = redmine_manager.get_ids(issue.subject)
    for elem in ids:
        issue_sub = redmine_manager.get_issue(elem)
        issue_sub.status_id = redmine_config.status_id_complete
        issue_sub.save()
    redmine_manager.update()
    issue = find_issue_with_dependencies()
    # assert 3 == 2
    assert issue.status.id == redmine_config.status_id_ready
    


def test_creating_another_project():
    """Test to check creating another project"""
    PROJECT_NAME = "test_multi_project"
    WIKI_PAGE_NAME = "Initialized graph"
    FILE_PATH = "graph.txt"
    redmine_manager.create_another_project(
        PROJECT_NAME, WIKI_PAGE_NAME, FILE_PATH
    )
    redmine_manager.init_all()
    issue = find_issue_with_dependencies()
    ids = redmine_manager.get_ids(issue.subject)
    for elem in ids:
        issue_sub = redmine_manager.get_issue(elem)
        issue_sub.status_id = redmine_config.status_id_complete
        issue_sub.save()
    redmine_manager.update()
    issue = find_issue_with_dependencies()
    assert issue.status.id == redmine_config.status_id_ready
    redmine.project.delete(PROJECT_NAME)
def test_all_tasks():
    pass

def teardown():
    """Teardown the test"""
    redmine.project.delete(redmine_config.project_name.lower())
    redmine_manager.clean_rocket_chat()
    for elem in redmine.user.all():
        if elem.id != 1:
            redmine.user.delete(elem.id)


# update()
