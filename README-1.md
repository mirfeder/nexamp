Nexamp Challenge
================

prototype application that provides an HTTP API for retrieving data about some solar farms.

Installation
------------
- clone the project [nexamp](https://github.com/mirfeder/nexamp)
- cd to project root directory
- Note: project was built using python 3.10.11
### - create and activate the virtual environment
```
python -m venv venv
source venv/bin/activate
``` 

### - install dependencies
```
pip install -r requirements.txt
```

## Run the Server:
``` 
cd src
uvicorn main:app
```
- Swagger docs available at http://localhost:8000/docs
- OpenAPI docs available at http://localhost:8000/reDoc

Notes
-----
- Application built using FastAPI. This has the advantage of automated documentation and testing via Swagger at localhost:8000/docs. A more robust application might require a different framework to be used.
- Application loads project metadata (projects.json) into memory at startup
- Generation data is loaded on request and then cached. In a full-featured application, it is likely that both metadata and generation data would be loaded into a relational database for querying. This might be done in a batch process as the data appears to be already aggregated by day, so is unlikely to be real-time data. It could still be cached once queried, with attention paid to cache invalidation (probably any monthly aggregations for current month and "maximum" calculations should be invalidated whenever new data is loaded)
- In a full-fledged application
  - code would be broken out into a more modular form rather than have everything in a single main.py file
  - robust error handling would be added
  - full data validation would be added
  - authentication and authorization would likely be added
  - unit tests would be added

