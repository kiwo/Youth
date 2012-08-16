#coding=utf-8

import datetime

from youth import bot
from youth import itinerary
from youth import place
from youth import maps
from youth import stuff
from youth import view
from youth import param
from youth import router
from youth import utils
from youth import rater

def do_home(request, response):
    view.to_html(None, 'home', request, response)
    
def do_about(request, response):
    view.to_html(None, 'about' if utils.get_language() != 'ru' else 'about_ru', request, response)
    
def do_directions(request, response):
    # get request parameters
    start_time = get_start_time(request)
    view_mode = request.get('out', 'html')
    engine = request.get('e', 'o')
    force = request.get('f', '')
    try:
        date = datetime.datetime.strptime(request.get('date', ''), '%Y-%m-%d')
    except:
        date = datetime.date.today() + datetime.timedelta(days=1)
        
    # get from and to (hotel name, attraction name or if not found - address)
    [from_place, from_location] = get_place(request, 'from', 'fll')
    [to_place, to_location] = get_place(request, 'to', 'tll')

    # produce data            
    data = itinerary.get_directions(from_place, from_location, to_place, to_location, date, start_time, engine, force)              
    
    # populate the requested view
    if view_mode == 'none':
        view.empty(response);
    elif view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'directions', request, response)

def do_hotels(request, response):
    ratings = rater.get_all()
    data = { 'ratings': ratings }
    view.to_html(data, 'hotels', request, response)
        
def do_hotel(request, response, name):
    hotel = place.get(name)[0]
    ratings = rater.get(hotel)
    data = { 'hotel': hotel, 'ratings': ratings }
    view.to_html(data, 'hotel', request, response)
        
def do_place(request, response):
    # get request parameters        
    view_mode = request.get('out', 'html')
    term = request.get('term', '')
    
    # produce data        
    data = place.get(term)
    
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'hotel', request, response)
        
def post_hotel(request):
    # get request parameters        
    name = request.get('name')
    name_rus = request.get('nameRus')
    file_name = request.get('fileName')
    rating = float(request.get('rating'))
    image_id = request.get('imageId')
    address = request.get('address')
    min_rate = float(request.get('minRate')) if request.get('minRate') != '' else None 
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    hotel_type = request.get('type')
    place.add_hotel(name, name_rus, file_name, rating, image_id, address, min_rate, lat, lng, hotel_type)
    
def delete_hotel(request):
    # get request parameters        
    name = request.get('name')
    place.delete_hotel(name)        

def post_attraction(request):
    # get request parameters        
    name = request.get('name')
    name_rus = request.get('nameRus')
    lat = float(request.get('lat'))
    lng = float(request.get('lng'))
    place.add_attraction(name, name_rus, lat, lng)
    
def delete_attraction(request):
    # get request parameters        
    name = request.get('name')
    place.delete_attraction(name) 
        
def do_transit(request, response):
    # get request parameters
    from_location = maps.GeoPoint(*[float(x) for x in request.get('from').split(',')])
    to_location = maps.GeoPoint(*[float(x) for x in request.get('to').split(',')])    
    view_mode = request.get('out', 'html')

    # produce data        
    #data = maps.get_transit_routes(from_location, to_location)
    data = maps.get_rusavtobus_routes(from_location, to_location) + maps.get_google_routes(from_location, to_location) 
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'transit', request, response)    

def do_routing(request, response):
    # get request parameters
    from_location = maps.GeoPoint(*[float(x) for x in request.get('from').split(',')])
    to_location = maps.GeoPoint(*[float(x) for x in request.get('to').split(',')])    
    view_mode = request.get('out', 'html')

    # produce data        
    data = router.get_route(from_location, to_location)
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'routing', request, response)    
        
def do_train(request, response):
    # get request parameters
    view_mode = request.get('out', 'html')

    # produce data        
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    data = bot.fetch_trains('Санкт-Петербург', 'Новый Петергоф', tomorrow)
        
    # populate the requested view
    if view_mode == 'json':
        view.to_json(data, response)
    else:
        view.to_html(data, 'train', request, response)
        
def post_param(request, response):
    name = request.get('name')
    value = request.get('value')
    param.add(name, value)

def do_test(request, response):
    from google.appengine.tools import dev_appserver 
    dev_appserver.TearDownStubs()
    response.out.write(stuff.test())
    
def do_cleanup(request, response):
    hotels = place.cleanup()
    for x in hotels:
        rater.cleanup(x)
    response.out.write('Done')
    
def do_notfound(request, response):
    view.to_html(None, 'notfound', request, response)
    
def get_start_time(request):
    try: 
        start_time = datetime.datetime.strptime(request.get('time', '09-30'), '%H-%M').time()
    except:
        start_time = datetime.time(hour=10, minute=0)
    return start_time
    
def get_place(request, name_param, coord_param):
    name = request.get(name_param, '')
    coord = request.get(coord_param, '').replace('-', ',')
    return place.get_by_name(name, coord)