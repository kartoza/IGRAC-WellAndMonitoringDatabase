# postgis-gwml2
A PostgreSQL schema implementing the groundwater interchange schema defined in GWML2

# groundwater
Groundwater is django app. to add it, you need to put <b>gwml2</b> into INSTALLED_APP <br>
And this into urls 
```
url(r"^groundwater/", include("gwml2.urls")),
```

# Database
the groundwater will be added into your "default" database. <br>
if you want to add it into new database, please prepare:
```
1. create database from your postgres with specific database name
2. add postgis config in the database by "CREATE EXTENSION postgis;"
3. on django settings add secondary database config
4. add GWML2_DATABASE_CONFIG for the name of the config database that you create before
5. add Router for gwml2 in settings by DATABASE_ROUTERS = ["gwml2.router.GWML2Router"]
6. to migrate the data, do on django "python manage.py migrate --database=<database config name>. e.g: python manage.py migrate --database=gwml2"
```
example of settings:
```
GWML2_DATABASE_CONFIG = "gwml2"

DATABASES = {
  "default": {
    "NAME": "django", 
    "USER": "password", 
    "PASSWORD": "password", 
    "HOST": "postgres", 
    "PORT": 5432, 
    "ENGINE": "django.contrib.gis.db.backends.postgis"
    }, 
  "gwml2": {
    "NAME": "groundwater", 
    "USER": "user", 
    "PASSWORD": "password", 
    "HOST": "postgres", 
    "PORT": 5432,
    "ENGINE": "django.contrib.gis.db.backends.postgis"
   }
 }
 
DATABASE_ROUTERS = ["gwml2.router.GWML2Router"]
```


# Model diagram
Here is model diagram of gwml2

![Model diagram](https://raw.githubusercontent.com/kartoza/gwml2/master/model_diagram.png)


# Generating the model diagram
Here's a nifty way to do it using pycharm:
1. Connect your database using pycharm, so it will appear on the database tab as below:
<img width="595" alt="Screen Shot 2020-07-01 at 14 06 11" src="https://user-images.githubusercontent.com/26101337/86213546-0fa93700-bba4-11ea-84c1-6190073ce16a.png">
2. Select your tables that you want to visualise then hit right click and click show visualisation
<img width="604" alt="Screen Shot 2020-07-01 at 14 10 14" src="https://user-images.githubusercontent.com/26101337/86213974-bbeb1d80-bba4-11ea-82ae-2e8635737bda.png">
3. Your diagrams will show on a separate tab.


# Library needed
Some views in GWML2 need specific libraries as follows in order to work properly:
- django-braces==1.14.0
- pyexcel-xls
- pyexcel-xlsx
- django-crispy-forms==1.8.1
