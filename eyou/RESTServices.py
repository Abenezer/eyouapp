import datetime
from cornice import Service
from sqlalchemy import func

from eyou.Schemas import AreaSchema, PlaceTagDisplay, FeedbackSchema, PlaceImageSchema, PlaceSchema
from services import IAuthenticationService
from models import User, Role, PlaceTag, Place, Feedback, PlaceImage, Profile

import pyramid.httpexceptions as exc
from pyramid.security import Allow, Deny, NO_PERMISSION_REQUIRED, Everyone, DENY_ALL, authenticated_userid

auth = Service('auth', '/auth', 'authentication service', cors_origins=('*',))


@auth.post()
def create_token(request):
    login = request.json['login']
    password = request.json['password']

    print (login)
    auth_svc = request.find_service(IAuthenticationService)
    user = auth_svc.authenticate(login, password)  # type: User
    if user:

        return {
            'result': 'ok',
            'token': request.create_jwt_token(user.id, name=user.username, roles=[r.name for r in user.roles])
        }
    else:
        return {
            'result': 'error'
        }


reg = Service('reg', '/register', 'registration service')


@reg.post()
def register_user(request):
    login = request.json_body.get('login')
    password = request.json_body.get('password')
    num_existing = request.dbsession.query(User).filter(User.username == login).count()
    if num_existing > 0:
        raise Exception('That user already exists!')
    user = User(username=login)
    user.set_password(password)
    user.profile = Profile(score=0, date_added=datetime.datetime.now())
    role = request.dbsession.query(Role).filter(Role.name == 'User').first()
    if role:
        user.roles.append(role)
    request.dbsession.add(user)


locate = Service('locate_area', '/locate', 'geocode an area', cors_origins=('*',))


@locate.get()
def locate_area(request):
    from geopy.geocoders import Nominatim
    q = request.params['q']
    print (q)
    geolocator = Nominatim(format_string='%s, addis ababa', timeout=10, country_bias='Ethiopia')
    location = geolocator.geocode(q)
    if location == None:
        raise exc.HTTPNotFound()
    return {'address': location.address, 'lat': location.latitude, 'lon': location.longitude}


reverse = Service('reverse_area', '/reverse', 'reverse geocode an area', cors_origins=('*',))


@reverse.get()
def reverse_area(request):
    lat = request.params['lat']
    lon = request.params['lon']
    from eyou.Helpers import toArea
    area = toArea(lon, lat)
    return AreaSchema().dump(area)


tag = Service('palce_tags', '/places/{id}/tags', 'get tags of specific place', cors_origins=('*',))


@tag.get()
def place_tags(request):
    place_id = int(request.matchdict['id'])
    res = request.dbsession.query(PlaceTag.tag, func.count(PlaceTag.user_id).label('count')).group_by(
        PlaceTag.tag).filter(
        PlaceTag.place_id == place_id)
    # print (res)
    schema = PlaceTagDisplay(many=True)
    return schema.dump(res)


comments = Service('palce_comments', '/places/{id}/comments', 'get comments of specific place', cors_origins=('*',))


@comments.get()
def place_comments(request):
    place_id = int(request.matchdict['id'])
    place = request.dbsession.query(Feedback).filter(Feedback.place_id == place_id)
    schema = FeedbackSchema(many=True)
    return schema.dump(place.all())


@comments.post()
def post_palce_comments(request):
    place_id = int(request.matchdict['id'])
    user_id = authenticated_userid(request)
    com = request.json_body
    feedback = Feedback(comment=com.get('comment'), point=com.get('point'), user_id=user_id, place_id=place_id,
                        date_added=datetime.datetime.now())
    schema = FeedbackSchema()
    request.dbsession.add(feedback)
    request.dbsession.flush()
    return schema.dump(feedback)


placeImageRating = Service('place image rating', '/placeImages/{id}/rate', 'give point to place images',
                           cors_origins=('*',))


@placeImageRating.put()
def rate_place_images(request):
    image_id = int(request.matchdict['id'])
    user = request.dbsession.query(User).get(authenticated_userid(request))
    place_image = request.dbsession.query(PlaceImage).get(image_id)
    rate = request.params.get('rate')

    if rate == "up":
        place_image.users.append(user)
    elif rate == "down":
        place_image.users.remove(user)

    return PlaceImageSchema().dump(place_image)


placeFav = Service('when profile favs places', '/places/{id}/fav', 'like fav', cors_origins=('*',))


@placeFav.put()
def fav_place(request):
    profile = request.dbsession.query(Profile).get(authenticated_userid(request))
    place = request.dbsession.query(Place).get(int(request.matchdict['id']))
    fav = request.params.get('fav')

    if fav == "yes":
        place.profiles.append(profile)
    elif fav == "no":
        place.profiles.remove(profile)

    return PlaceSchema().dump(place)

