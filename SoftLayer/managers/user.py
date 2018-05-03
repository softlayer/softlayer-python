"""
    SoftLayer.user
    ~~~~~~~~~~~~~
    User Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
from SoftLayer import exceptions
from SoftLayer import utils

from operator import itemgetter


class UserManager(utils.IdentifierMixin, object):
    """Manages Users.

    See: https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/

    Example::

       # Initialize the Manager.
       import SoftLayer
       client = SoftLayer.create_client_from_env()
       mgr = SoftLayer.UserManager(client)

    :param SoftLayer.API.BaseClient client: the client instance

    """

    def __init__(self, client):
        self.client = client
        self.userService = self.client['SoftLayer_User_Customer']
        self.accountService = self.client['SoftLayer_Account']
        self.resolvers = [self._get_id_from_username]

    def list_users(self, objectMask=None, objectFilter=None):
        """Lists all users on an account

        :param string objectMask: Used to overwrite the default objectMask.
        :param dictionary objectFilter: If you want to use an objectFilter.
        :returns: A list of dictionaries that describe each user
        
        Example::
            result = mgr.list_users()
        """

        if objectMask is None:
            objectMask = "mask[id, username, displayName, userStatus[name], hardwareCount, virtualGuestCount]"

        return self.accountService.getUsers(mask=objectMask, filter=objectFilter)

    def get_user(self, user_id, objectMask=None):
        if objectMask is None:
            objectMask = """mask[userStatus[name], parent[id, username]]"""
        return self.userService.getObject(id=user_id, mask=objectMask)

    def get_all_permissions(self):
        permissions = self.client.call('User_Customer_CustomerPermission_Permission', 'getAllObjects')
        return sorted(permissions, key=itemgetter('keyName'))

    def add_permissions(self, user_id, permissions):
        pretty_permissions = format_permission_object(permissions)
        return self.userService.addBulkPortalPermission(pretty_permissions, id=user_id)

    def remove_permissions(self, user_id, permissions):
        pretty_permissions = format_permission_object(permissions)
        return self.userService.removeBulkPortalPermission(pretty_permissions, id=user_id)

    def _get_id_from_username(self, username):
        _mask = "mask[id, username]"
        _filter = {'users' : {'username': utils.query_filter(username)}}
        user = self.list_users(_mask, _filter)
        if len(user) == 1:
            return [user[0]['id']]
        else:
            raise exceptions.SoftLayerError("Unable to find user id for %s" % username)

def format_permission_object(permissions):
    pretty_permissions = []
    for permission in permissions:
        pretty_permissions.append({'keyName': permission})
    return pretty_permissions


