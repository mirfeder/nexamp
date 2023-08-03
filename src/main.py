import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from os import path
from typing import List

from cachetools import cached
from dataclass_csv import DataclassReader, dateformat
from dataclass_wizard import JSONWizard
from fastapi import FastAPI, HTTPException

app = FastAPI()

@dataclass
class Project(JSONWizard):
    id: int
    name: str
    capacity_kw: float
    address: str
    city: str
    state: str
    zip: str

@dataclass
@dateformat('%Y-%m-%dT00:00:00')
class TimeSeries:
    ts: datetime
    total: float

# load projects json data into memory
with open('../data/projects.json') as file:
    data = json.load(file)

projects = {}
for project in data:
    project = Project.from_dict(project)
    projects[project.id] = project
#---end load projects json data into memory

@cached(cache={})
def read_csv(id: int) -> List[TimeSeries]:
    if path.isfile(f'../data/generation_data/{id}_data.csv'):
      result: List[TimeSeries] = []
      with open(f'../data/generation_data/{id}_data.csv') as datafile:
          reader = DataclassReader(datafile, TimeSeries)
          reader.map('Generation Meter RM - 01').to('total')
          for row in reader:
              result.append(row)
      return result

@cached(cache={})
def calculate_max(id):
    project_data = read_csv(id)
    monthly_data = defaultdict(int)
    for row in project_data:
        key = f'{row.ts.month}/{row.ts.year}'
        monthly_data[key] += row.total
    values = sorted(monthly_data.items(), key=lambda x:x[1], reverse=True)
    return {"month": values[0][0], "output": '%.2f' % values[0][1]}

# get general project data by project id
@app.get("/project/{id}")
async def get_project(id:int) -> Project:
    if id in projects:
        result = projects.get(id)
        return result
    else:
        error_msg = f'Project {id} not found'
        raise HTTPException(status_code=404, detail=error_msg)

# get maximum output month for a project
@app.get("/project/output/{id}")
async def get_max_output_month(id):
    result = calculate_max(id)
    return result

# get information about projects in a state    
@app.get("/projects/state/{state}")
async def get_projects_by_state(state) -> list[str]:
    state_projs = [value.name for value in projects.values() if value.state == state]
    if state_projs:
        return state_projs
    else:
        error_msg = f'No projects found for state {state}'
        raise HTTPException(status_code=404, detail=error_msg)

@app.get("projects/capacity-range/{lower}/{upper}")
async def get_projects_in_capacity_range(lower, upper):
    result = [project.name for project in projects.values() if float(lower) <= project.capacity_kw <= float(upper)]
    return result