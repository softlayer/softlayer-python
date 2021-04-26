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
        self.override_service = self.client['Network_Service_Vpn_Overrides']
        self.account_service = self.client['SoftLayer_Account']
        self.subscription_service = self.client['SoftLayer_Email_Subscription']
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
                                 email, roles, externalBindingCount,apiAuthenticationKeyCount]"""

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

    def get_all_notifications(self):
        """Calls SoftLayer_Email_Subscription::getAllObjects

        Stores the result in self.all_permissions
        :returns: A list of dictionaries that contains all valid permissions
        """
        return self.subscription_service.getAllObjects(mask='mask[enabled]')

    def enable_notifications(self, notifications_names):
        """Enables a list of notifications for the current a user profile.

        :param list notifications_names: List of notifications names to enable
        :returns: True on success

        Example::
            enable_notifications(['Order Approved','Reload Complete'])
        """

        result = False
        notifications = self.gather_notifications(notifications_names)
        for notification in notifications:
            notification_id = notification.get('id')
            result = self.subscription_service.enable(id=notification_id)
            if not result:
                return False
        return result

    def disable_notifications(self, notifications_names):
        """Disable a list of notifications for the current a user profile.

        :param list notifications_names: List of notifications names to disable
        :returns: True on success

        Example::
            disable_notifications(['Order Approved','Reload Complete'])
        """

        result = False
        notifications = self.gather_notifications(notifications_names)
        for notification in notifications:
            notification_id = notification.get('id')
            result = self.subscription_service.disable(id=notification_id)
            if not result:
                return False
        return result

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

    def gather_notifications(self, notifications_names):
        """Gets a list of notifications.

        :param list notifications_names: A list of notifications names.
        :returns: list of notifications.
        """
        notifications = []
        available_notifications = self.get_all_notifications()
        for notification in notifications_names:
            result = next((item for item in available_notifications
                           if item.get('name') == notification), None)
            if result:
                notifications.append(result)
            else:
                raise exceptions.SoftLayerError("{} is not a valid notification name".format(notification))
        return notifications

    def create_user(self, user_object, password):
        """Blindly sends user_object to SoftLayer_User_Customer::createObject

        :param dictionary user_object: https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/
        """
        LOGGER.warning("Creating User %s", user_object['username'])

        try:
            return self.user_service.createObject(user_object, password, None)
        except exceptions.SoftLayerAPIError as ex:
            if ex.faultCode == "SoftLayer_Exception_User_Customer_DelegateIamIdInvitationToPaas":
                raise exceptions.SoftLayerError("Your request for a new user was received, but it needs to be "
                                                "processed by the Platform Services API first. Barring any errors on "
                                                "the Platform Services side, your new user should be created shortly.")
            raise

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

    def vpn_manual(self, user_id, value):
        """Enable or disable the manual config of subnets.

        :param int user_id: User to edit.
        :param bool value: Value for vpnManualConfig flag.
        """
        user_object = {'vpnManualConfig': value}
        return self.edit_user(user_id, user_object)

    def vpn_subnet_add(self, user_id, subnet_ids):
        """Add subnets for a user.

        :param int user_id: User to edit.
        :param list subnet_ids: list of subnet Ids.
        """
        overrides = [{"userId": user_id, "subnetId": subnet_id} for subnet_id in subnet_ids]
        return_value = self.override_service.createObjects(overrides)
        update_success = self.user_service.updateVpnUser(id=user_id)
        if not update_success:
            raise exceptions.SoftLayerAPIError("Overrides created, but unable to update VPN user")
        return return_value

    def vpn_subnet_remove(self, user_id, subnet_ids):
        """Remove subnets for a user.

        :param int user_id: User to edit.
        :param list subnet_ids: list of subnet Ids.
        """
        overrides = self.get_overrides_list(user_id, subnet_ids)
        return_value = self.override_service.deleteObjects(overrides)
        update_success = self.user_service.updateVpnUser(id=user_id)
        if not update_success:
            raise exceptions.SoftLayerAPIError("Overrides deleted, but unable to update VPN user")
        return return_value

    def get_overrides_list(self, user_id, subnet_ids):
        """Converts a list of subnets to a list of overrides.

        :param int user_id: The ID of the user.
        :param list subnet_ids: A list of subnets.
        :returns: A list of overrides associated with the given subnets.
        """

        overrides_list = []
        matching_overrides = {}
        output_error = "Subnet {} does not exist in the subnets assigned for user {}"
        _mask = 'mask[id,subnetId]'
        overrides = self.user_service.getOverrides(id=user_id, mask=_mask)
        for subnet in subnet_ids:
            for override in overrides:
                if int(subnet) == override.get('subnetId'):
                    matching_overrides = override
                    break
            if matching_overrides.get('subnetId') is None:
                raise exceptions.SoftLayerError(output_error.format(subnet, user_id))

            overrides_list.append(matching_overrides)

        return overrides_list


def _keyname_search(haystack, needle):
    for item in haystack:
        if item.get('keyName') == needle:
            return True
    return False
