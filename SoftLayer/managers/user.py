"""
    SoftLayer.user
    ~~~~~~~~~~~~~
    User Manager/helpers

    :license: MIT, see LICENSE for more details.
"""
import datetime
import logging
from operator import itemgetter

from SoftLayer import exceptions
from SoftLayer import utils

LOGGER = logging.getLogger(__name__)


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
        self.all_permissions = None

    def list_users(self, objectmask=None, objectfilter=None):
        """Lists all users on an account

        :param string objectmask: Used to overwrite the default objectmask.
        :param dictionary objectfilter: If you want to use an objectfilter.
        :returns: A list of dictionaries that describe each user

        Example::
            result = mgr.list_users()
        """

        if objectmask is None:
            objectmask = """mask[id, username, displayName, userStatus[name], hardwareCount, virtualGuestCount,
                                 email, roles]"""

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

    def get_current_user(self, objectmask=None):
        """Calls SoftLayer_Account::getCurrentUser"""

        if objectmask is None:
            objectmask = "mask[userStatus[name], parent[id, username]]"
        return self.account_service.getCurrentUser(mask=objectmask)

    def get_all_permissions(self):
        """Calls SoftLayer_User_CustomerPermissions_Permission::getAllObjects

        Stores the result in self.all_permissions
        :returns: A list of dictionaries that contains all valid permissions
        """
        if self.all_permissions is None:
            permissions = self.client.call('User_Customer_CustomerPermission_Permission', 'getAllObjects')
            self.all_permissions = sorted(permissions, key=itemgetter('keyName'))
        return self.all_permissions

    def add_permissions(self, user_id, permissions):
        """Enables a list of permissions for a user

        :param int id: user id to set
        :param list permissions: List of permissions keynames to enable
        :returns: True on success, Exception otherwise

        Example::
            add_permissions(123, ['BANDWIDTH_MANAGE'])
        """
        pretty_permissions = self.format_permission_object(permissions)
        LOGGER.warning("Adding the following permissions to %s: %s", user_id, pretty_permissions)
        return self.user_service.addBulkPortalPermission(pretty_permissions, id=user_id)

    def remove_permissions(self, user_id, permissions):
        """Disables a list of permissions for a user

        :param int id: user id to set
        :param list permissions: List of permissions keynames to disable
        :returns: True on success, Exception otherwise

        Example::
            remove_permissions(123, ['BANDWIDTH_MANAGE'])
        """
        pretty_permissions = self.format_permission_object(permissions)
        LOGGER.warning("Removing the following permissions to %s: %s", user_id, pretty_permissions)
        return self.user_service.removeBulkPortalPermission(pretty_permissions, id=user_id)

    def permissions_from_user(self, user_id, from_user_id):
        """Sets user_id's permission to be the same as from_user_id's

        Any permissions from_user_id has will be added to user_id.
        Any permissions from_user_id doesn't have will be removed from user_id.

        :param int user_id: The user to change permissions.
        :param int from_user_id: The use to base permissions from.
        :returns: True on success, Exception otherwise.
        """

        from_permissions = self.get_user_permissions(from_user_id)
        self.add_permissions(user_id, from_permissions)
        all_permissions = self.get_all_permissions()
        remove_permissions = []

        for permission in all_permissions:
            # If permission does not exist for from_user_id add it to the list to be removed
            if _keyname_search(from_permissions, permission['keyName']):
                continue
            else:
                remove_permissions.append({'keyName': permission['keyName']})

        self.remove_permissions(user_id, remove_permissions)
        return True

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
            date_object = datetime.datetime.today() - datetime.timedelta(days=30)
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
        :param string start_date: "%Y-%m-%dT%H:%M:%s.0000-06:00" is the full formatted string.
                                  The Timezone part has to be HH:MM, notice the : there.
        :returns: https://softlayer.github.io/reference/datatypes/SoftLayer_Event_Log/
        """

        if start_date is None:
            date_object = datetime.datetime.today() - datetime.timedelta(days=30)
            start_date = date_object.strftime("%Y-%m-%dT00:00:00")

        object_filter = {
            'userId': {
                'operation': user_id
            },
            'eventCreateDate': {
                'operation': 'greaterThanDate',
                'options': [{'name': 'date', 'value': [start_date]}]
            }
        }

        events = self.client.call('Event_Log', 'getAllObjects', filter=object_filter)
        if events is None:
            events = [{'eventName': 'No Events Found'}]
        return events

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
        elif len(user) > 1:
            raise exceptions.SoftLayerError("Multiple users found with the name: %s" % username)
        else:
            raise exceptions.SoftLayerError("Unable to find user id for %s" % username)

    def format_permission_object(self, permissions):
        """Formats a list of permission key names into something the SLAPI will respect.

        :param list permissions: A list of SLAPI permissions keyNames.
                                 keyName of ALL will return all permissions.
        :returns: list of dictionaries that can be sent to the api to add or remove permissions
        :throws SoftLayerError: If any permission is invalid this exception will be thrown.
        """
        pretty_permissions = []
        available_permissions = self.get_all_permissions()
        # pp(available_permissions)
        for permission in permissions:
            # Handle data retrieved directly from the API
            if isinstance(permission, dict):
                permission = permission['keyName']
            permission = permission.upper()
            if permission == 'ALL':
                return available_permissions
            # Search through available_permissions to make sure what the user entered was valid
            if _keyname_search(available_permissions, permission):
                pretty_permissions.append({'keyName': permission})
            else:
                raise exceptions.SoftLayerError("'%s' is not a valid permission" % permission)
        return pretty_permissions

    def create_user(self, user_object, password):
        """Blindly sends user_object to SoftLayer_User_Customer::createObject

        :param dictionary user_object: https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/
        """
        LOGGER.warning("Creating User %s", user_object['username'])
        return self.user_service.createObject(user_object, password, None)

    def edit_user(self, user_id, user_object):
        """Blindly sends user_object to SoftLayer_User_Customer::editObject

        :param int user_id: User to edit
        :param dictionary user_object: https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/
        """
        return self.user_service.editObject(user_object, id=user_id)

    def add_api_authentication_key(self, user_id):
        """Calls SoftLayer_User_Customer::addApiAuthenticationKey

        :param int user_id: User to add API key to
        """
        return self.user_service.addApiAuthenticationKey(id=user_id)


def _keyname_search(haystack, needle):
    for item in haystack:
        if item.get('keyName') == needle:
            return True
    return False
