import datetime
from cornice.resource import resource, view
from pyramid.response import Response
from sqlalchemy import desc
from sqlalchemy import func

from models import *
from Schemas import *
from pyramid.security import Allow, Deny, NO_PERMISSION_REQUIRED, Everyone, Authenticated, authenticated_userid


def my_acl(request):
    return [
        (Allow, Authenticated, ['read']),
        (Allow, 'role:User', ['create', 'update']),
        (Allow, 'role:Admin', ['super_update']),
    ]


policy = dict(

    origins=('*',),

)


# @resource(collection_path='/users', path='/users/{id}')
# class User(object):
#
#     def __init__(self, request):
#         self.request = request
#
#     def collection_get(self):
#
#         return {'users': _USERS.keys()}
#
#

@resource(collection_path='/places', path='/places/{id}', acl=my_acl, cors_policy=policy)
class Places(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = PlaceSchema()
        self.schema_c = PlaceSchema(many=True)
        self.user = authenticated_userid(self.request)

    @view(permission='read')
    def collection_get(self):

        type_id = self.request.params.get('type_id')
        area_id = self.request.params.get('area_id')
        cat_id = self.request.params.get('cat_id')
        user_id = self.request.params.get('user_id')
        places = self.request.GET.getall('places')

        sort = self.request.params.get('sort')

        sq = self.DB.query(Feedback.place_id, func.count(Feedback.place_id).label('feedback_count')).group_by(
            Feedback.place_id).subquery()
        # #
        sq2 = self.DB.query(Place.id, func.count(Profile.id).label('fav_count')).outerjoin(profile_place).outerjoin(
            Profile).group_by(Place.id).subquery()
        #
        # q = self.DB.query(Place.id, Place.name, Place.description, Place.type_id, Place.area_id, Place.lat, Place.lon,
        #                   Place.user_id, Place.type_id,
        #                   sq.c.feedback_count, ).outerjoin(sq, sq.c.place_id == Place.id)

        # q = self.DB.query(Place,func.count(Profile.id).label('fav_count')).outerjoin(profile_place).outerjoin(
        # Profile).group_by(Place)

        # q = self.DB.query(Place.id, Place.name, Place.description, Place.type_id, Place.area_id, Place.lat, Place.lon,
        #                   Place.user_id, Place.type_id, sq.c.feedback_count,
        #                   func.count(Profile.id).label('fav_count')).outerjoin(
        #     profile_place).outerjoin(Profile).outerjoin(sq, sq.c.place_id == Place.id).group_by(Place)

        q = self.DB.query(Place.id, Place.name, Place.description, Place.type_id, Place.area_id, Place.lat, Place.lon,
                          Place.user_id, Place.type_id, Place.user_id, sq.c.feedback_count, sq2.c.fav_count).outerjoin(
            sq,
            sq.c.place_id == Place.id).outerjoin(
            sq2, sq2.c.id == Place.id)

        if type_id:
            q = q.filter(Place.type_id == type_id)
        if area_id:
            q = q.filter(Place.area_id == area_id)
        if cat_id:
            q = q.filter(Place.type.has(category_id=cat_id))
        if user_id:
            if int(user_id) == 0:
                user_id = self.user
            q = q.filter(Place.user_id == user_id)
        if places:
            q = q.filter(Place.id.in_(places))
        x = []
        if sort == 'date':
            x = q.order_by(Place.date_added.desc()).limit(50).all()
        elif sort =='fav':
            x = q.order_by(desc('fav_count')).limit(50).all()
        elif sort =='rand':
            x = q.order_by(func.random()).limit(50).all()
        else:
            x = q.limit(50).all()
        return self.schema_c.dump(x)

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['id'])
        return self.schema.dump(self.DB.query(Place).get(id))

    @view(permission='update')
    def collection_post(self):
        place = self.schema.load(self.request.json).data

        # print(self.request.json_body)
        num_existing = self.DB.query(Place).filter(Place.name == place['name']).count()
        if num_existing > 0:
            raise Exception('That place already exists!')

        p = Place(name=place['name'], description=place['description'], type_id=place['type_id'], lon=place['lon'],
                  lat=place['lat'], user_id=self.user, date_added=datetime.datetime.now())
        from eyou.Helpers import toArea
        area = toArea(place['lon'], place['lat'])
        if area is not None:
            area_existing = self.DB.query(Area).filter(Area.OSM_id == area.OSM_id).first()
            if area_existing is not None:
                p.area_id = area_existing.area_id
            else:
                p.area = area

        self.DB.add(p)
        return self.schema.dump(place)


@resource(collection_path='/types', path='/types/{id}', acl=my_acl, cors_policy=policy)
class Types(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = TypeSchema()
        self.schema_c = TypeSchema(many=True)

    @view(permission='read')
    def collection_get(self):
        return self.schema_c.dump(self.DB.query(Type))

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['id'])
        return self.schema.dump(self.DB.query(Type).filter(Type.id == id).first())

    @view(permission='update')
    def collection_post(self):
        type = self.schema.load(self.request.json).data

        # print(self.request.json_body)
        num_existing = self.DB.query(Type).filter(Type.name == type['name']).count()
        if num_existing > 0:
            raise Exception('That Type already exists!')
        self.DB.add(Type(name=type['name'], description=type['description'], category_id=type['category_id']))
        return self.schema.dump(type)


@resource(collection_path='/categories', path='/categories/{id}', acl=my_acl, cors_policy=policy)
class Categories(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = CategorySchema()
        self.schema_c = CategorySchema(many=True)

    @view(permission='read')
    def collection_get(self):
        return self.schema_c.dump(self.DB.query(Category))

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['id'])
        cat = self.DB.query(Category).filter(Category.id == id).first()
        return self.schema.dump(cat)

    def delete(self):
        id = int(self.request.matchdict['id'])
        cat = self.DB.query(Category).filter(Category.id == id).first();
        self.DB.delete(cat)

    @view(permission='update')
    def collection_post(self):
        cat = self.schema.load(self.request.json).data

        # print(self.request.json_body)
        num_existing = self.DB.query(Category).filter(Category.name == cat['name']).count()
        if num_existing > 0:
            raise Exception('That Type already exists!')
        self.DB.add(Category(name=cat['name'], description=cat['description']))
        return self.schema.dump(cat)


@resource(collection_path='/areas', path='/areas/{id}', acl=my_acl, cors_policy=policy)
class Areas(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = AreaSchema()
        self.schema_c = AreaSchema(many=True)

    @view(permission='read')
    def collection_get(self):
        return self.schema_c.dump(self.DB.query(Area))

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['id'])
        area = self.DB.query(Area).filter(Area.id == id).first()
        return self.schema.dump(area)

    def delete(self):
        id = int(self.request.matchdict['id'])
        area = self.DB.query(Area).filter(Area.id == id).first();
        self.DB.delete(area)

    @view(permission='update')
    def collection_post(self):
        area = self.schema.load(self.request.json).data

        # print(self.request.json_body)
        num_existing = self.DB.query(Area).filter(Area.displayName == area['display_name']).count()
        if num_existing > 0:
            raise Exception('That Area already exists!')
        self.DB.add(Area(displayName=area['displayName'], lon=area['lon'], lat=area['lat']))
        return self.schema.dump(area)


@resource(collection_path='/tags', path='/tags/{id}', acl=my_acl, cors_policy=policy)
class Tags(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = PlaceTagDisplay()
        self.schema_c = PlaceTagDisplay(many=True)

    @view(permission='read')
    def collection_get(self):
        res = self.DB.query(PlaceTag.tag, func.count(PlaceTag.id).label('count')).group_by(
            PlaceTag.tag)
        q = self.request.params.get('q')

        if q:
            res = res.filter(PlaceTag.tag.like('%' + q + '%'))

        return self.schema_c.dump(res.all())

    @view(permission='update', validators=('validate_tag',))
    def collection_post(self):
        tag = self.request.json_body
        userid = authenticated_userid(self.request)
        # print(self.request.json_body)
        num_existing = self.DB.query(PlaceTag).filter(PlaceTag.user_id == userid, PlaceTag.place_id == tag['place_id'],
                                                      PlaceTag.tag == tag['tag']).count()

        self.DB.add(PlaceTag(user_id=userid, place_id=tag['place_id'], tag=tag['tag']))
        res = self.DB.query(PlaceTag.tag, func.count(PlaceTag.id).label('count')).group_by(
            PlaceTag.tag).filter(PlaceTag.tag == tag['tag'], PlaceTag.place_id == tag['place_id'])

        return self.schema.dump(res.first())

    def validate_tag(self, request, **args):

        userid = authenticated_userid(request)
        tag = request.json_body
        num_existing = request.dbsession.query(PlaceTag).filter(PlaceTag.user_id == userid,
                                                                PlaceTag.place_id == tag['place_id'],
                                                                PlaceTag.tag == tag['tag']).count()
        if num_existing > 0:
            request.errors.add('url', 'tag', 'This tag already exists!')
            request.errors.status = 409


@resource(collection_path='menus', path='menus/{m_id}', acl=my_acl, cors_policy=policy)
class Menus(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = MenuSchema()
        self.schema_c = MenuSchema(many=True)
        self.user = authenticated_userid(self.request)

    @view(permission='read')
    def collection_get(self):
        sq = self.DB.query(MenuFeedback.menu_id, func.count(MenuFeedback.menu_id).label('feedback_count')).group_by(
            MenuFeedback.menu_id).subquery()
        q = self.DB.query(Menu.id, Menu.name, Menu.description, Menu.cost, Menu.subtype, Menu.user_id, Menu.place_id,
                          Menu.type_id, Menu.image_path,
                          sq.c.feedback_count).outerjoin(sq, sq.c.menu_id == Menu.id)

        return self.schema_c.dump(q.all())

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['m_id'])
        menu = self.DB.query(Menu).get(id)
        return self.schema.dump(menu)

    def put(self):
        id = int(self.request.matchdict['m_id'])
        menu = self.DB.query(Menu).filter(Menu.id == id)
        img_src = self.request.POST['file']
        if img_src:
            import cloudinary.uploader
            response = cloudinary.uploader.upload(img_src, folder="menu/" + str(id) + "/", tags=['menu'],
                                                  width=400, height=320, crop="fit")
            menu.update({Menu.image_path: response['url']})
        return self.schema.dump(menu)

    def delete(self):
        id = int(self.request.matchdict['m_id'])
        menu = self.DB.query(Menu).get(id)
        if self.user == menu.user_id:
            self.DB.delete(menu)
            return id
        raise Exception('you cant remove this meuu')

    @view(permission='update')
    def collection_post(self):
        menu = self.schema.load(self.request.json).data
        menu_db = Menu(name=menu['name'], description=menu['description'], cost=menu['cost'],
                       place_id=menu['place_id'], user_id=self.user, date_added=datetime.datetime.now())
        self.DB.add(menu_db)
        self.DB.flush()
        return self.schema.dump(menu_db)


@resource(collection_path='menus/{m_id}/comments', path='menus/comments/{c_id}', acl=my_acl, cors_policy=policy)
class MenuComments(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = MenuCommentSchema()
        self.schema_c = MenuCommentSchema(many=True)
        self.user = authenticated_userid(self.request)

    @view(permission='read')
    def collection_get(self):
        m_id = int(self.request.matchdict['m_id'])
        return self.schema_c.dump(self.DB.query(MenuFeedback).filter(MenuFeedback.menu_id == m_id).all())

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['c_id'])
        comment = self.DB.query(MenuFeedback).get(id)
        return self.schema.dump(comment)

    @view(permission='update')
    def delete(self):
        id = int(self.request.matchdict['c_id'])
        comment = self.DB.query(MenuFeedback).get(id)
        if self.user == comment.user_id:
            self.DB.delete(comment)
            return id
        raise Exception('you cant remove this comment')

    @view(permission='update')
    def put(self):
        id = int(self.request.matchdict['c_id'])
        com = self.schema.load(self.request.json).data
        comment = self.DB.query(MenuFeedback).fileter(MenuFeedback.id == id)
        if com.get('comment'):
            comment.update({MenuFeedback.comment: com.get('comment')})
        if com.get('tag'):
            comment.update({MenuFeedback.tag: com.get('tag')})
        if com.get('rating'):
            rating = int(com.get('rating'))
            if rating > 5:
                rating = 5
            comment.update({MenuFeedback.rating: rating})

    @view(permission='update')
    def collection_post(self):
        m_id = int(self.request.matchdict['m_id'])
        comment = self.schema.load(self.request.json).data
        feedback = MenuFeedback(comment=comment.get('comment'), tag=comment.get('tag'), rating=comment.get('rating'),
                                menu_id=m_id, user_id=self.user, date_added=datetime.datetime.now())
        self.DB.add(feedback)
        self.DB.flush()
        return self.schema.dump(feedback)


@resource(collection_path='places/{p_id}/menus', path='places/{p_id}/menus/{m_id}', acl=my_acl, cors_policy=policy)
class PlaceMenus(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = MenuSchema()
        self.schema_c = MenuSchema(many=True)

    @view(permission='read')
    def collection_get(self):
        p_id = int(self.request.matchdict['p_id'])
        sq = self.DB.query(MenuFeedback.menu_id, func.count(MenuFeedback.menu_id).label('feedback_count')).group_by(
            MenuFeedback.menu_id).subquery()
        q = self.DB.query(Menu.id, Menu.name, Menu.description, Menu.cost, Menu.subtype, Menu.user_id, Menu.place_id,
                          Menu.type_id, Menu.image_path,
                          sq.c.feedback_count).outerjoin(sq, sq.c.menu_id == Menu.id)
        q = q.filter(Menu.place_id == p_id)
        return self.schema_c.dump(q.all())


@resource(collection_path='places/{p_id}/images', path='places/{p_id}/imgaes/{i_id}', acl=my_acl, cors_policy=policy)
class PlaceImages(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = PlaceImageSchema()
        self.schema_c = PlaceImageSchema(many=True)

    @view(permission='read')
    def collection_get(self):
        p_id = int(self.request.matchdict['p_id'])

        q = self.DB.query(PlaceImage).filter(PlaceImage.place_id == p_id)
        return self.schema_c.dump(q.all())

    @view(permission='update')
    def collection_post(self):
        p_id = int(self.request.matchdict['p_id'])
        import cloudinary.uploader
        tag = self.request.POST['tag']
        # input_file = self.request.POST['file']

        # f = input_file.read()
        # img_src = bytearray(f)
        img_src = self.request.POST['file']
        response = cloudinary.uploader.upload(img_src, folder="place/" + str(p_id) + "/", tags=['place', tag],
                                              width=800, height=600, crop="limit")

        place = PlaceImage(place_id=p_id, tag=tag, image_path=response['public_id'], url=response['url'],
                           date_added=datetime.datetime.now())
        self.DB.add(place)
        return self.schema.dump(place)


@resource(path='/profile', acl=my_acl, cors_policy=policy)
class Profiles(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.user = authenticated_userid(self.request)
        self.schema = ProfileSchema()

    @view(permission='read')
    def get(self):
        id = self.user
        profile = self.DB.query(Profile).get(id)
        return self.schema.dump(profile)

    def put(self):
        id = self.user
        prof = self.request.json_body

        profile = self.DB.query(Profile).filter(Profile.id == id)

        if prof.get('picture_path'):
            profile.update({Profile.picture_path: prof.get('picture_path')})
        if prof.get('gender'):
            profile.update({Profile.gender: prof.get('gender')})
        if prof.get('dob'):
            date = datetime.datetime.strptime(prof.get('dob'), "%Y-%m-%d").date()
            profile.update({Profile.dob: date})
        if prof.get('full_name'):
            p = profile.first();
            if p.full_name is None:
                profile.update({Profile.score: Profile.score + 1000})
            profile.update({Profile.full_name: prof.get('full_name')})
        if prof.get('work_status_id'):
            profile.update({Profile.work_status_id: prof.get('work_status_id')})

        return self.schema.dump(profile.first())


@resource(collection_path='/comments', path='/comments/{id}', acl=my_acl, cors_policy=policy)
class Comments(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = FeedbackSchema()
        self.schema_c = FeedbackSchema(many=True)
        self.user = authenticated_userid(self.request)

    @view(permission='read')
    def collection_get(self):
        return self.schema_c.dump(self.DB.query(Feedback))

    @view(permission='read')
    def get(self):
        id = int(self.request.matchdict['id'])
        feedback = self.DB.query(Feedback).get(id)
        return self.schema.dump(feedback)

    @view(permission='update')
    def delete(self):
        id = int(self.request.matchdict['id'])
        feedback = self.DB.query(Feedback).get(id)
        self.DB.delete(feedback)
        return id


@resource(collection_path='/workstatus', path='/workstaus/{id}', acl=my_acl, cors_policy=policy)
class WorkStatuses(object):
    def __init__(self, context, request):
        self.request = request
        self.DB = request.dbsession
        self.schema = WorkStatusSchema()
        self.schema_c = WorkStatusSchema(many=True)

    @view(permission='read')
    def collection_get(self):
        return self.schema_c.dump(self.DB.query(WorkStatus))

    @view(permission='update')
    def collection_post(self):
        statuses = self.request.json
        for status in statuses:
            s = WorkStatus(name=status['name'])
            self.DB.add(s)
