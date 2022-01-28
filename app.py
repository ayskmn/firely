from flask import Flask, render_template, redirect, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from forms import AddressForm
import requests
import json
import os 

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY","5b8d2239ec52c1b98c292b3db811c2adf89cb6f617e5708674c3826186f76f05")

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

"""
Renders the homepage with form, 
redirects to homepage when the form is invalid.
"""

@app.route('/', methods=['GET', 'POST'])
def home_page():
    form = AddressForm()

    if form.validate_on_submit():
        address = form.address.data
        return redirect('/map')
    else:
        return render_template('home.html', form=form)


"""
Makes an API request to Ambeedata API to retrieve
closest fire info based on coordinates.
Renders a not found message if there are no fires detected
in the area.

Get a new api key from https://api.ambeedata.com/latest/fire and
replace it with the x-api-key's value.
"""

@app.route('/map', methods=['GET', 'POST'])
def pass_coords():
    try:
        form = AddressForm()
        search_text = form.address.data
        coords = request_coords(search_text)

        url = "https://api.ambeedata.com/latest/fire"
        querystring = {"lat": coords["lat"], "lng": coords["lng"]}
        headers = {
            'x-api-key': "5b8d2239ec52c1b98c292b3db811c2adf89cb6f617e5708674c3826186f76f05",
            'Content-type': "application/json"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        
        latest_fires = json.loads(response.text)
        lat = latest_fires['data'][0]['lat']
        lng = latest_fires['data'][0]['lng']
        distance = round(latest_fires['data'][0]['distance'], 2)

        # Renders the map with `lat`, `long` and 
        # `distance of the fire from the user's location` data. 

        return render_template('map.html', coords=coords, fire_lat=lat, fire_lng=lng, distance=distance)
    except KeyError:
        print("Invalid input")
        return render_template('404.html')



"""
Makes API calls to Mapbox with a street address, and the API access token
to retrieve coordinates of the address passed by the user.
Returns coordinates.
"""

def request_coords(location):
    access_token = "pk.eyJ1IjoiYXlzb2siLCJhIjoiY2tzZ25jZ3JnMWx3MjJ0cm80aTZhaG5oaSJ9.2zzHPMv_COMuSjPn8wmypw"
    form = AddressForm()
    search_text = form.address.data

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{search_text}.json?access_token=pk.eyJ1IjoiYXlzb2siLCJhIjoiY2tzZ25jZ3JnMWx3MjJ0cm80aTZhaG5oaSJ9.2zzHPMv_COMuSjPn8wmypw"
    params = {'sensor': 'false', 'address': 'search_text' }

  
    r = requests.get(url, params=params)
    results = r.json()
    if (results['features'] == []):
        flash('No fires detected in the area!')
    else: 
        location = results['features'][0]['geometry']['coordinates']
        coords = location[0], location[1]
        lat = location[1]
        lng = location[0]

        return {"lat": lat, "lng": lng}


@app.route('/button', methods=['GET'])
def go_back_home():
    return redirect('/')


if __name__ == "__main__":
    app.run()
