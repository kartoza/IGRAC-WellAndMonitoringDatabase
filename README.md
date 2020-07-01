# postgis-gwml2
A PostgreSQL schema implementing the groundwater interchange schema defined in GWML2

# groundwater
Groundwater is django app. to add it, you need to put <b>gwml2</b> into INSTALLED_APP <br>
And this into urls 
```
url(r'^groundwater/', include('gwml2.urls')),
```