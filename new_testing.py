from redminelib import Redmine
import testing_variant
from pydantic import BaseModel
def create_project(name_of_project: str) -> None:
    redmine = Redmine(
        url=REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWORD
    )
    redmine.project.create(name=name_of_project, identifier=name_of_project.lower())
    return name_of_project.lower()
def create_wiki_page(title: str) -> None:
    redmine = Redmine(
        url=REDMINE_URL, username=REDMINE_USERNAME, password=REDMINE_PASSWORD
    )
    f = open("graph.txt", "r")
    redmine.wiki_page.create(project_id="testing", title=title, text=f.read())
# Configuration
REDMINE_URL: str = "http://172.17.0.2:3000/"
REDMINE_USERNAME: str = "admin"
REDMINE_PASSWORD: str = "admin123"

# ic(list_)
# redmine_manager.update_issues()
# redmine_manager.delete_all()
# redmine_manager.create_user("test8956","test123456","Jan1","Nowak", "examp1le@op.pl")
# redmine_manager.create_user("test123675","test456789","Jan1","Banas","example21137@op.pl")
# redmine_manager.clean_rocket_chat()
def setup():
    STATUS_ID_COMPLETE: int = 4
    STATUS_ID_READY: int = 3
    STATUS_ID_NEW: int = 1
    TRACKER_ID: int = 1
    PRIORITY_ID: int = 1
    ROOM_ID: str = "aQTNDBmpk2jDXBCLTu7bXji4aeLzsMFCgE"
    OLDEST: str = "2016-05-30T13:42:25.304Z"
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
        room_id=ROOM_ID,
        oldest=OLDEST
    )
    create_wiki_page("Foo")
    redmine_manager = testing_variant.RedmineManager(redmine_config)
    redmine_manager.init_project()
    redmine_manager.init_relations()
    redmine_manager.update()
    
setup()