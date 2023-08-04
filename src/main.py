import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
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
@dateformat("%Y-%m-%dT00:00:00")
class TimeSeries:
    ts: datetime
    total: float


class ValidStates(str, Enum):
    NY = "NY"
    RI = "RI"
    MA = "MA"


# --load projects json data into memory
try:
    with open("../data/projects.json") as file:
        data = json.load(file)

    projects = {}
    for project in data:
        project = Project.from_dict(project)
        projects[project.id] = project
except Exception as e:
    raise e
# ---end load projects json data into memory


@cached(cache={})
def read_csv(id: int) -> List[TimeSeries]:
    """reads in csv file with generation data for a given project, if it exists.
      Results are cached. By reading into a specific dataclass and using csv
      DataClassReader library, only the necessary columns are loaded, which
      standardizes the format of the loaded data

    Args:
        id (int): ID of project to load

    Returns:
        List[TimeSeries]: a list of days with corresponding totals
    """
    try:
        if path.isfile(f"../data/generation_data/{id}_data.csv"):
            result: List[TimeSeries] = []
            with open(f"../data/generation_data/{id}_data.csv") as datafile:
                reader = DataclassReader(datafile, TimeSeries)
                reader.map("Generation Meter RM - 01").to("total")
                for row in reader:
                    result.append(row)
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@cached(cache={})
def calculate_max(id):
    """finds the month with maximum output for a given project. Caches reults.

    Args:
        id (int): project id

    Returns:
        dict: month and year of max output, formatted maximum output for that month
    """
    try:
        project_data = read_csv(id)
        if project_data:
            monthly_data = defaultdict(int)
            for row in project_data:
                key = f"{row.ts.month}/{row.ts.year}"
                monthly_data[key] += row.total
            values = sorted(monthly_data.items(), key=lambda x: x[1], reverse=True)
            return {"month": values[0][0], "output": "%.2f" % values[0][1]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@app.get("/project/{id}")
async def get_project(id: int) -> Project:
    """Gets metadata for a project

    Args:
        id (int): project id

    Raises:
        HTTPException: Returns 404 if project is not found

    Returns:
        Project: metadata for the project
    """

    if id in projects:
        result = projects.get(id)
        return result
    else:
        error_msg = f"Project {id} not found"
        raise HTTPException(status_code=404, detail=error_msg)


@app.get("/project/output/{id}")
async def get_max_output_month(id: int):
    """Gets maximum output month for a project

    Args:
        id (int): project id

    Returns:
        dict: month and year of max output, formatted maximum output for that month
    """
    if id in projects:
        result = calculate_max(id)
        return result
    else:
        error_msg = f"Project {id} not found"
        raise HTTPException(status_code=404, detail=error_msg)


@app.get("/projects/state/{state}")
async def get_projects_by_state(state: ValidStates) -> list[str]:
    """Gets information about projects in a state

    Args:
        state (str): Two-letter state code. Uses Enum to take advantage of
        FastAPI built-in validation

    Raises:
        HTTPException: Returns 404 if no projects found for state

    Returns:
        list[str]: A list of project names for projects in the state
    """
    state_projs = [
        value.name for value in projects.values() if value.state == state.upper()
    ]
    if state_projs:
        return state_projs
    else:
        error_msg = f"No projects found for state {state}"
        return HTTPException(status_code=404, detail=error_msg)


@app.get("/projects/capacity-range/{lower}/{upper}")
async def get_projects_in_capacity_range(lower: float, upper: float) -> list[str]:
    """Finds projects that have a capacity within the range specified

    Args:
        lower (float): lower limit of range
        upper (float): upper limit of range

    Returns:
        list[str]: list of project names that have capacity within range specified
    """
    try:
        result = [
            project.name
            for project in projects.values()
            if float(lower) <= project.capacity_kw <= float(upper)
        ]
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
