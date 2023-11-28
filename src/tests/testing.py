import sys
import json
from redminelib import Redmine
from pydantic import BaseModel
from icecream import ic
import pytest
import time
sys.path.append('src/app')
import app

def create_project(name_of_project: str) -> None:
    while True:
        try:
            redmine.project.create(name=name_of_project, identifier=name_of_project.lower())
            return name_of_project.lower()
        except Exception as e:
            print(f"Error creating project: {e}")

def create_wiki_page(title: str) -> None:
    try:
        with open("graph.txt", "r") as f:
            redmine.wiki_page.create(project_id=redmine_config.project_id, title=title, text=f.read())
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Error creating wiki page: {e}")


# Configuration
with open('data_testing.json') as json_file:
    data = json.load(json_file)
redmine_config = app.RedmineConfig(**data)
redmine = Redmine(url=redmine_config.url, username=redmine_config.username, password=redmine_config.password)
create_project("Testing")
create_wiki_page("Foo")
redmine_manager = app.RedmineManager(redmine_config)


def setup():
    # redmine_manager.create_user("test8956","test123456","Jan1","Nowak", "examp1le@op.pl")
    # redmine_manager.create_user("test123675","test456789","Jan1","Banas","example21137@op.pl")
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
    assert redmine_manager.get_users() is not None


def test_memberships():
    """Test if membership have been initialized"""
    assert redmine.project_membership.filter(project_id=redmine_config.project_id) is not None


def test_if_initialized(project_init, project_init_relations):
    """Test to check if initialized properly"""
    assert redmine.issue.all() is not None
    # redmine_manager.create_user_in_rocket_chat()
    # redmine_manager._send_message_to_all_users("12345436456")


def test_realtions(delete_all_fix, project_init, project_init_relations):
    """Test if relations are initialized"""
    issue = redmine.issue.get(1)
    print(len(issue.relations))
    assert len(issue.relations) is not None


def find_issue_with_dependencies():
    """Finds issue with more than 2 dependecies"""
    issues = redmine_manager.get_issues
    ic(issues)
    for elem in issues:
        number = redmine_manager.get_number(elem.subject)
        if number >= 2:
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
    ic(issue.status.id)
    assert issue.status.id == redmine_config.status_id_ready


def teardown():
    redmine.project.delete(redmine_config.project_id)
    redmine_manager.clean_rocket_chat()


# update()
