from eyou.models import User


class AuthenticationService(object):
    def __init__(self, dbsession):
        self.dbsession = dbsession

    def authenticate(self, login, password):
        """

        :rtype: User
        """
        user = self.dbsession.query(User).filter(User.username == login).first()  # type: User
        if user:
            if user.check_password(password):
                return user

        return False


def auth_factory(context, request):
    return AuthenticationService(request.dbsession)
