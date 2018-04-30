# Visualizing Untappd User Data

## The Data

Untappd is a social networking app that allows users to check-in beers they drink and share with friends on the app. A user can search for a beer to see information about the beer (ABV, brewery), the average rating of the beer on the network, other users' check-ins of the beer, including photographs, locales where the beer is available, and similar beers. 

When users check in to a beer, there are a few things they can record (all optional):

> Rating (out of 5)
> Description
> Location
> Serving style (draught, nitro, taster, etc)
> Flavor Profile (as keywords)

Users that are Supporting Members ($5/mo to Untappd) can download their check-in data history as a .csv or .json format.

## The Analysis

This is a work in progress and works with the .csv format of user data. To run, save a user data file in /data/userdata.csv.

[beermap.py](beermap.py) 

Creates an interactive html bubble map of breweries using `folium` package (saved as `checkins_map.html`), with bubble size proportional to number of checkins to beers from that brewery.