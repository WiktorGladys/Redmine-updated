from pydantic import BaseModel
import json
from redminelib import Redmine

redmine = Redmine(url="http://192.168.100.5:3000/", username="admin", password="admin123")
issues = redmine.issue.filter(project_id="testing")
for elem in issues:
    elem.delete()