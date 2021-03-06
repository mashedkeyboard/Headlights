# Give me all the libraries
from six.moves import urllib
import json
import handlers


# Fetch the text-based regional forecast from DataPoint
def fetchRegionFrcAsText(regioncode, key):
    url = 'http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/regionalforecast/json/' + regioncode + '?key=' + key
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Headlights Client')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request).read().decode('UTF-8')  # Tries to read, will throw exception on 403 etc
    except urllib.error.HTTPError as e:
        if e.code == 403:
            handlers.criterr(
                'HTTP error 403 (access denied). Check your API key and try again.')  # This is probably them forgetting to put their key in (correctly)
        else:
            handlers.criterr('Unknown HTTP error. Error code ' + str(
                e.code) + '. Maybe the Met Office API (or your internet) is dead?')  # Something very odd.
    except Exception:
        import traceback
        handlers.criterr('Generic urllib exception: ' + traceback.format_exc())  # Something even odder
    weatherobj = json.loads(response)
    try:
        shortWthrText = weatherobj['RegionalFcst']['FcstPeriods']['Period'][0]['Paragraph'][1][
            '$']  # wahey the text! let's hope they never change the way their API returns...
    except KeyError:
        handlers.criterr(
            'Could not parse weather data. Sounds like the Met Office changed their API, but not their endpoint. :/')  # oh noes! they changed their API?!?
    return str(shortWthrText)


# Fetch the actual more local forecast general daily data from DataPoint
def fetchLocalFrc(stationcode, key):
    url = 'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/' + stationcode + '?res=daily&key=' + key
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Headlights Client')
    request.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(request).read().decode('UTF-8')
    except urllib.error.HTTPError as e:
        if e.code == 403:
            handlers.criterr('HTTP error 403 (access denied). Check your API key and try again.')
        else:
            handlers.criterr('Unknown HTTP error. Error code ' + str(
                e.code) + '. Maybe the Met Office API (or your internet) is dead?')
    except Exception:
        import traceback
        handlers.criterr('Generic urllib exception: ' + traceback.format_exc())
    weatherobj = json.loads(response)
    try:
        weather = weatherobj['SiteRep']['DV']['Location']['Period'][0]['Rep'][0]
        return weather
    except KeyError:
        handlers.criterr(
            'Could not parse weather data. Sounds like the Met Office changed their API, but not their endpoint. :/')  # oh noes! they changed their API?!?
