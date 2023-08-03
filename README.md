Nexamp Challenge
================

For this task, you'll be developing a prototype application that provides an HTTP API for
retrieving data about some solar farms. We suggest using python, but you may complete the 
exercise in any language that you prefer.

Included in this directory is a json file (projects.json) containing a list of solar farms,
and a folder of csv files containing simulated generation data for each of the farms. The
csv files are named `{farm_id}_data.csv`, where `farm_id` matches up to the id of a
solar farm in the projects.json file.

Task Description
----------------
Using any libraries or frameworks you're comfortable with, create an application that provides 
an HTTP API with endpoints that allow the caller to accomplish the following tasks. (Implement as 
many of the endpoints as you feel comfortable with):

  - Get basic info about a solar farm by id (name, capacity, city, state, etc.)

  - Get a list of solar farms in a given state (MA, NY, RI)

  - Given a capacity range (minimum capacity and maximum capacity) return a list of solar farms 
    with capacity within the specified range (ex. 100kw - 500kW)

  - Given a solar farm id, return the month in which it generated the most energy (generated 
    energy is in the `total` column of the project's generation data file)

Parameters may be provided however you prefer (query string, url path, request body, etc)
Response data may be in any format of your choosing (json, html, plain text, etc).


Evaluation
----------
We will want to review your application, the code behind it, and the process you used to generate it.
Please take the opportunity to show the breadth of your work, and do not focus on trying to complete 
every task. 

Feel free to reach out with any questions! 

