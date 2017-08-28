
from zope.interface import Interface

class IAuthenticationService(Interface):
  def authenticate(login,password):
    pass