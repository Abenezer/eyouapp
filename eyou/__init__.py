from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from services import AuthenticationService, IAuthenticationService, auth_factory
import os
import cloudinary


def expandvars_dict(settings):
    """Expands all environment variables in a settings dictionary."""
    return dict((key, os.path.expandvars(value)) for
                key, value in settings.iteritems())


def main(global_config, **settings):

    cloudinary.config(
        cloud_name='damadigital',
        api_key='214196132319438',
        api_secret='EqPRPiQ96ZlNShQeEpV8Qx1KXWQ'
    )

    """ This function returns a Pyramid WSGI application.
    """
    sqlalchemy_url = os.path.expandvars(settings.get('sqlalchemy.url'))
    settings['sqlalchemy.url'] = sqlalchemy_url
    print (sqlalchemy_url+"from main")

    config = Configurator(settings=settings)

    # Pyramid requires an authorization policy to be active.
    config.set_authorization_policy(ACLAuthorizationPolicy())
    # Enable JWT authentication.
    config.include('pyramid_jwt')

    config.include('pyramid_jinja2')
    config.include('pyramid_services')

    config.include('cornice')

    config.include('.models')
    config.include('.routes')

    def add_role_principals(userid, request):
        return ['role:%s' % role for role in request.jwt_claims.get('roles', [])]

    config.set_jwt_authentication_policy('eyou_key', callback=add_role_principals)

    config.register_service_factory(auth_factory, IAuthenticationService)

    config.scan()

    return config.make_wsgi_app()
