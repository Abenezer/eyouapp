from pyramid.response import Response
from pyramid.view import view_config, forbidden_view_config
from pyramid.view import exception_view_config
from geopy.exc import GeocoderTimedOut

from sqlalchemy.exc import DBAPIError

from ..models import Place


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    try:
        query = request.dbsession.query(Place)
        place = query.filter(Place.id == 1).first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'place': place, 'project': 'Eyou'}


@forbidden_view_config(renderer='../templates/auth_error.jinja2')
def auth_error(request):

    if request.authenticated_userid is None:
        error = "unauthenticated"
        request.response.status = 401
    else:
        error = "unautherized"
        request.response.status = 403

    return {'error': error}




@exception_view_config(GeocoderTimedOut)
def failed_validation(exc, request):
    response =  Response('Time out')
    response.status_int = 408
    return response


# places = Service(name='places', path='/places', description="Places")
#
#
# @places.get()
# def get_places(request):
#     """Returns a list of all tasks."""
#     return [place.to_json() for place in request.dbsession.query(Place)]
#
#
# @places.post()
# def create_place(request):
#     """Adds a new task."""
#     place = request.json
#     num_existing = request.dbsession.query(Place).filter(Place.name == place['name']).count()
#     if num_existing > 0:
#         raise Exception('That task already exists!')
#     request.dbsession.add(Place.from_json(place))




db_err_msg = """\
Pyramid is having a problem using your SQL database.
"""
