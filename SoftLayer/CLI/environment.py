from importlib import import_module

from SoftLayer.CLI.modules import get_module_list


class Environment(object):

    # {'module_name': {'action': 'actionClass'}}
    plugins = {}

    def load_module(self, mod):  # pragma: no cover
        return import_module('SoftLayer.CLI.modules.%s' % mod)

    def add_plugin(self, cls):
        command = cls.__module__.split('.')[-1]
        if command not in self.plugins:
            self.plugins[command] = {}
        self.plugins[command][cls.action] = cls

    def plugin_list(self):
        return get_module_list()


class CLIRunnableType(type):

    env = Environment()

    def __init__(cls, name, bases, attrs):
        super(CLIRunnableType, cls).__init__(name, bases, attrs)
        if cls.env and name != 'CLIRunnable':
            cls.env.add_plugin(cls)
