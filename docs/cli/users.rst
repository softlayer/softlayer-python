.. _cli_user:

Users
=============
Version 5.6.0 introduces the ability to interact with user accounts from the cli. 

.. _cli_user_create:

user create
-----------
This command will create a user on your account.

Options
^^^^^^^
-e, --email TEXT      Email address for this user. Required for creation.  [required]
-p, --password TEXT   Password to set for this user. If no password is provided, user will be sent an email to generate one, which expires in 24 hours.  '-p generate' will create a password for you (Requires Python 3.6+). Passwords require 8+ characters, upper and lowercase, a number and a symbol.
-u, --from-user TEXT  Base user to use as a template for creating this user. Will default to the user running this command. Information provided in --template supersedes this template.
-t, --template TEXT   A json string describing https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/
-a, --api-key         Create an API key for this user.
-h, --help            Show this message and exit.

::

    slcli user create my@email.com -e my@email.com -p generate -a -t '{"firstName": "Test", "lastName": "Testerson"}'

.. _cli_user_list:

user list
----------
This command will list all Active users on the account that your user has access to view. 
There is the option to also filter by username


.. _cli_user_detail:

user detail <user>
-------------------
Gives a variety of details about a specific user. <user> can be a user id, or username. Will always print a basic set of information about the user, but there are a few extra flags to pull in more detailed information.

user detail <user> -p, --permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Will list the permissions the user has. To see a list of all possible permissions, or to change a user's permissions, see :ref:`cli_user_permissions`

user detail <user> -h, --hardware
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Will list the Hardware and Dedicated Hosts the user is able to access. 


user detail <user> -v, --virtual
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Will list the Virtual Guests the user has access to.

user detail <user> -l, --logins
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Show login history of this user for the last 30 days. IBMId Users will show logins properly, but may not show failed logins. 

user detail <user> -e, --events
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Shows things that are logged in the Event_Log service. Logins, reboots, reloads, and other such actions will show up here.

.. _cli_user_permissions:

user permissions <user>
^^^^^^^^^^^^^^^^^^^^^^^
Will list off all permission keyNames, along with which are assigned to that specific user.

.. _cli_user_permissions_edit:

user edit-permissions
---------------------
Enable or Disable specific permissions. It is possible to set multiple permissions in one command as well.

::

    $ slcli user edit-permissions USERID --enable -p TICKET_EDIT -p TICKET_ADD -p TICKET_SEARCH

Will enable TICKET_EDIT, TICKET_ADD, and TICKET_SEARCH permissions for the USERID

.. _cli_user_edit_details:

user edit-details
-----------------
Edit a User's details

JSON strings should be enclosed in '' and each item should be enclosed in "\"

::

  slcli user edit-details testUser -t '{"firstName": "Test", "lastName": "Testerson"}'

Options
^^^^^^^

-t, --template TEXT  A json string describing `SoftLayer_User_Customer <https://softlayer.github.io/reference/datatypes/SoftLayer_User_Customer/>`_ .  [required]
-h, --help           Show this message and exit.

