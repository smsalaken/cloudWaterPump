import logging
import requests
import json

import azure.functions as func


#def main(req: func.HttpRequest) -> func.HttpResponse:
def main(req: func.HttpRequest) :

    logging.info('Python ServianAgroPump function processed a http request.')

    cityName = req.params.get('cityName')
    countryCode = req.params.get('countryCode')
    API_key = '7d3849399a71576f9a2e6eb4ec6946c2'
    if not cityName:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            cityName = req_body.get('cityName')
            countryCode = req_body.get('countryCode')

    if cityName:

        # we are getting the result for only next 3 hours by setting cnt=1
        url = 'http://api.openweathermap.org/data/2.5/forecast?q='+cityName+','+countryCode+'&APPID='+API_key+'&cnt=1&units=metric'
        logging.info(url)
        r = requests.get(url).json()['list']#[0]#['main']

        logging.info(r)
        
        max_temp = r[0]['main']['temp_max']#[3]#r.values()
        humidity = r[0]['main']['humidity']
        
        # rain information is not always available
        try:
            rain = r[0]['rain']['3h']
        except: 
            rain = 0
        
        # response data
        response = {}
        response['max_temp_Celsius'] = max_temp
        response['humidity_precent'] = humidity
        response['rain_next_3hr_block_mm'] = rain # this paramter is the forecasted value of rain water in mm in the current forecasting time block

        # make a recommendation to start pump
        # This value should take some contextual factors into consideration. This is the place where we will introduce ML and intelligence

        # related info:
        #   source: http://anpsa.org.au/APOL2006/aug06-2.html
        #   One millimetre of rain will add about 1 litre of water per square metre to a soil.
        #   A sprinkler delivering 10 litres per minute (600 litres per hour) will supply an area of 40 square metres with 600/40 =15 litres per sq. metre/hour = 15 mm per hour.
        #
        # A practical idea of the moisture level in clay and loam soils can be obtained by taking a sample from at least 20cm down. 
        # Squeeze the soil in your fist. If it has any tendency to stick together and maintain its moulded shape, it is moist enough to maintain most plant life. If it is impossible to mould it, then it needs watering. 
        # This test will not work in sandy soils, but an inspection of the soil at a similar depth will give an indication of the moisture content.

        # source: https://aggie-horticulture.tamu.edu/earthkind/drought/drought-management-for-commercial-horticulture/so-what-constitutes-an-effective-rain-event/
        # Lastly, the best time to water is actually during a rain event, of course if it is raining “cats and dogs” one would 
        # not want to water, because the water is already coming so fast that it will run off anyway. But mist and drizzle is a different story. 
        # No water will be evaporating since it is raining and the amount you apply along with the mist or drizzle will 
        # help wet the soil to a greater depth.

        # Table 1. General soil water storage and depletion characteristics for three different soil types.
        #                                                           Soil Texture
        #                                                       Sands	        Loams	        Clays
        # Water infiltration rate (inches per hour)	            2.0 – 6.0	    0.6 – 2.0	    0.2 – 0.6
        # Available water (inches per ft.)	                    1.0 – 1.5	    1.5 – 2.5	    2.5 – 4.0
        # Days to depletion when ET = .2 inches/day	            5 – 7.5	        7.5 – 12.5	    12.5 – 20.0
        # Amount of water to wet to 12 in a dry soil (inches)	1.0	            1.5 – 2.0	    2.5

        rainThreshold = 1 # an arbitrary value for now
        if (response['rain_next_3hr_block_mm'] < rainThreshold):
            response['recommendation_start_pump'] = True
        else:
            response['recommendation_start_pump'] = False

        # convert to json format
        response = json.dumps(response)

        
        return func.HttpResponse(f"{response}")
    else:
        return func.HttpResponse(
             "Please pass a valid city name along with country code on the query string or in the request body",
             status_code=400
        )
