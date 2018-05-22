"""
    SoftLayer.user
    ~~~~~~~~~~~~~
    User Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import datetime
from operator import itemgetter

from SoftLayer import exceptions
from SoftLayer import utils


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
        self.user_service = self.client['SoftLayer_User_Customer']
        self.account_service = self.client['SoftLayer_Account']
        self.resolvers = [self._get_id_from_username]

    def list_users(self, objectmask=None, objectfilter=None):
        """Lists all users on an account

        :param string objectmask: Used to overwrite the default objectmask.
        :param dictionary objectfilter: If you want to use an objectfilter.
        :returns: A list of dictionaries that describe each user

        Example::
            result = mgr.list_users()
        """

        if objectmask is None:
            objectmask = "mask[id, username, displayName, userStatus[name], hardwareCount, virtualGuestCount]"

        return self.account_service.getUsers(mask=objectmask, filter=objectfilter)

    def get_user(self, user_id, objectmask=None):
        """Calls SoftLayer_User_Customer::getObject

        :param int user_id: Id of the user
        :param string objectmask: default is 'mask[userStatus[name], parent[id, username]]'
        :returns: A user object.
        """
        if objectmask is None:
            objectmask = "mask[userStatus[name], parent[id, username]]"
        return self.user_service.getObject(id=user_id, mask=objectmask)

    def get_all_permissions(self):
        """Calls SoftLayer_User_CustomerPermissions_Permission::getAllObjects

        :returns: A list of dictionaries that contains all valid permissions
        """
        permissions = self.client.call('User_Customer_CustomerPermission_Permission', 'getAllObjects')
        return sorted(permissions, key=itemgetter('keyName'))

    def add_permissions(self, user_id, permissions):
        """Enables a list of permissions for a user

        :param int id: user id to set
        :param list permissions: List of permissions keynames to enable
        :returns: True on success, Exception otherwise

        Example::
            add_permissions(123, ['BANDWIDTH_MANAGE'])
        """
        pretty_permissions = format_permission_object(permissions)
        return self.user_service.addBulkPortalPermission(pretty_permissions, id=user_id)

    def remove_permissions(self, user_id, permissions):
        """Disables a list of permissions for a user

        :param int id: user id to set
        :param list permissions: List of permissions keynames to disable
        :returns: True on success, Exception otherwise

        Example::
            remove_permissions(123, ['BANDWIDTH_MANAGE'])
        """
        pretty_permissions = format_permission_object(permissions)
        return self.user_service.removeBulkPortalPermission(pretty_permissions, id=user_id)

    def get_user_permissions(self, user_id):
        """Returns a sorted list of a users permissions"""
        permissions = self.user_service.getPermissions(id=user_id)
        return sorted(permissions, key=itemgetter('keyName'))

    def get_logins(self, user_id, start_date=None):
        """Gets the login history for a user, default start_date is 30 days ago

        :param int id: User id to get
        :param string start_date: "%m/%d/%Y %H:%M:%s" formatted string.
        :returns: list https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer_Access_Authentication/
        Example::
            get_logins(123, '04/08/2018 0:0:0')
        """

        if start_date is None:
            date_object = datetime.date.today() - datetime.timedelta(days=30)
            start_date = date_object.strftime("%m/%d/%Y 0:0:0")

        date_filter = {
            'loginAttempts': {
                'createDate': {
                    'operation': 'greaterThanDate',
                    'options': [{'name': 'date', 'value': [start_date]}]
                }
            }
        }
        login_log = self.user_service.getLoginAttempts(id=user_id, filter=date_filter)
        return login_log

    def get_events(self, user_id, start_date=None):
        """Gets the event log for a specific user, default start_date is 30 days ago

        :param int id: User id to view
        :param string start_date: "%Y-%m-%dT%H:%M:%s.0000-06:00" formatted string. Anything else wont work
        :returns: https://softlayer.github.io/reference/datatypes/SoftLayer_Event_Log/
        """

        if start_date is None:
            date_object = datetime.date.today() - datetime.timedelta(days=30)
            start_date = date_object.strftime("%Y-%m-%dT00:00:00.0000-06:00")

        object_filter = {
            'userId': {
                'operation': user_id
            },
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [{'name': 'date', 'value': [start_date]}]
            }
        }

        return self.client.call('Event_Log', 'getAllObjects', filter=object_filter)

    def _get_id_from_username(self, username):
        """Looks up a username's id

        :param string username: Username to lookup
        :returns: The id that matches username.
        """
        _mask = "mask[id, username]"
        _filter = {'users': {'username': utils.query_filter(username)}}
        user = self.list_users(_mask, _filter)
        if len(user) == 1:
            return [user[0]['id']]
        else:
            # Might eventually want to throw an exception if len(user) > 1
            raise exceptions.SoftLayerError("Unable to find user id for %s" % username)


def format_permission_object(permissions):
    """Formats a list of permission key names into something the SLAPI will respect"""
    pretty_permissions = []
    for permission in permissions:
        pretty_permissions.append({'keyName': permission})
    return pretty_permissions
