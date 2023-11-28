from pydantic import BaseModel
import json
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
    url_rocket: str
    username_rocket: str
    password_rocket: str
    oldest: str

with open('data_testing.json') as json_file:
    data = json.load(json_file)
instance = RedmineConfig(**data)
print(instance.url)