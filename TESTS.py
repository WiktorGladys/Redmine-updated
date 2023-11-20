import time
import pytest
import adding_docker
from icecream import ic
# Configuration
REDMINE_URL = "http://172.17.0.2:3000/"
REDMINE_USERNAME = "admin"
REDMINE_PASSWORD = "admin123"
PROJECT_ID = "project"
STATUS_ID_COMPLETE = 4
STATUS_ID_READY = 3
STATUS_ID_NEW = 1
TRACKER_ID = 1
PRIORITY_ID = 1

redmine_manager = adding_docker.RedmineManager(
    REDMINE_URL,
    REDMINE_USERNAME,
    REDMINE_PASSWORD,
    PROJECT_ID,
    STATUS_ID_COMPLETE,
    STATUS_ID_READY,
    TRACKER_ID,
    PRIORITY_ID,
)

# INITIALIZATION
list_graph = redmine_manager.prepare_list()
@pytest.fixture
def delete_all_fix():
    """Pytest fixture deletes all taska"""
    return redmine_manager.delete_all()


@pytest.fixture
def project_init():
    """Pytest fixture initializes project"""
    return redmine_manager.init_project()


def test_if_initialized(delete_all_fix, project_init):
    """Test if initialized properly"""
    # redmine_manager.delete_all()
    # redmine_manager.init_project()
    issue = redmine_manager.get_issue(redmine_manager.find_task(list_graph[0][0]))
    for i in range(0, 1000):
        if issue.status.id == STATUS_ID_NEW:
            break
    assert issue.status.id == STATUS_ID_NEW


def test_single_case(delete_all_fix, project_init):
    """Test single dependency"""
    issue = redmine_manager.get_issue(redmine_manager.find_task(list_graph[0][0]))
    issue.status_id = STATUS_ID_COMPLETE
    issue.save()
    redmine_manager.update()
    issue_second = redmine_manager.get_issue(
        redmine_manager.find_task(list_graph[0][1])
    )
    assert issue_second.status.id == STATUS_ID_READY


def find_issue_with_dependencies():
    """Finds issue with more tahn 2 dependecies"""
    issues = redmine_manager.get_issues()
    for elem in issues:
        number = redmine_manager.get_number(elem.subject)
        if number >= 2:
            return elem



def test_auto_multi(delete_all_fix, project_init):
    """Test multi dependency"""
    issue = find_issue_with_dependencies()
    time.sleep(5)
    ids = redmine_manager.get_ids(issue.subject)
    for elem in ids:
        issue_sub = redmine_manager.get_issue(elem)
        issue_sub.status_id = STATUS_ID_COMPLETE
        issue_sub.save()
    redmine_manager.update()
    issue = find_issue_with_dependencies()
    time.sleep(5)
    assert issue.status.id == STATUS_ID_READY
