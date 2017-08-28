from marshmallow import Schema, fields


class TypeSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    popularity = fields.Int()
    category_id = fields.Int()


class PlaceSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    type_id = fields.Int()
    area_id = fields.Int()
    user_id = fields.Int()
    area = fields.Nested('AreaSchema', only='localName')
    type = fields.Nested('TypeSchema')
    lat = fields.Float()
    lon = fields.Float()
    feedback_count = fields.Int()
    fav_count = fields.Int()
    date_added = fields.Date()
    profiles = fields.Nested("ProfileSchema", many=True, only='id')


class CategorySchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    popularity = fields.Int()
    types = fields.Nested('TypeSchema', many=True, only=('id', 'name'))


class AreaSchema(Schema):
    id = fields.Int()
    lon = fields.Float()
    lat = fields.Float()
    country = fields.Str()
    city = fields.Str()
    localName = fields.Str()
    displayName = fields.Str()
    description = fields.Str()


class PlaceTagDisplay(Schema):
    tag = fields.Str()
    count = fields.Int()


class UserSchema(Schema):
    username = fields.Str()
    profile = fields.Nested('ProfileSchema', only='full_name')


class FeedbackSchema(Schema):
    id = fields.Int()
    point = fields.Int()
    comment = fields.Str()
    place_id = fields.Int()
    user_id = fields.Int()
    date_added = fields.Date()
    user = fields.Nested("UserSchema")


class MenuSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    cost = fields.Float()
    subtype = fields.Str()
    place_id = fields.Int()
    type_id = fields.Int()
    user_id = fields.Int()
    image_path = fields.Str()
    feedback_count = fields.Int()
    place = fields.Nested("PlaceSchema", only='name')
    user = fields.Nested("UserSchema", only='username')


class MenuCommentSchema(Schema):
    id = fields.Int()
    tag = fields.Str()
    comment = fields.Str()
    rating = fields.Float()
    user_id = fields.Int()
    date_added = fields.Date()
    user = fields.Nested("UserSchema", only='username')


class PlaceImageSchema(Schema):
    id = fields.Int()
    tag = fields.Str()
    image_path = fields.Str()
    place_id = fields.Int()
    url = fields.Str()
    users = fields.Nested("UserSchema", many=True, only='id')


class ProfileSchema(Schema):
    id = fields.Int()
    picture_path = fields.Str()
    score = fields.Str()
    gender = fields.Str()
    dob = fields.Date()
    full_name = fields.Str()
    work_status_id = fields.Int()
    places = fields.Nested("PlaceSchema", many=True, only='id')
    user = fields.Nested("UserSchema", only='username')


class LocationSchema(Schema):
    address = fields.Str()
    lat = fields.Float()
    lon = fields.Float()


class WorkStatusSchema(Schema):
    id = fields.Int()
    name = fields.Str()
