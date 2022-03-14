"""Makes sure all routes have documentation"""
import SoftLayer
from SoftLayer.CLI import routes
from pprint import pprint as pp
import glob
import logging
import os
import sys
import re

class Checker():

    def __init__(self):
        pass

    def getDocFiles(self, path=None):
        files = []
        if path is None:
            path = ".{seper}docs{seper}cli".format(seper=os.path.sep)
        for file in glob.glob(path + '/*', recursive=True):
            if os.path.isdir(file):
                files = files + self.getDocFiles(file)
            else:
                files.append(file)
        return files

    def readDocs(self, path=None):
        files = self.getDocFiles(path)
        commands = {}
        click_regex = re.compile(r"\.\. click:: ([a-zA-Z0-9_\.:]*)")
        prog_regex = re.compile(r"\W*:prog: (.*)")

        for file in files:
            click_line = ''
            prog_line = ''
            with open(file, 'r') as f:
                for line in f:
                    click_match = re.match(click_regex, line)
                    prog_match = False
                    if click_match:
                        click_line = click_match.group(1)

                    # Prog line should always be directly after click line.
                        prog_match = re.match(prog_regex, f.readline())
                    if prog_match:
                        prog_line = prog_match.group(1).replace(" ", ":")
                        commands[prog_line] = click_line
                        click_line = ''
                        prog_line = ''
        # pp(commands)
        return commands

    def checkCommand(self, command, documented_commands):
        """Sees if a command is documented

        :param tuple command: like the entry in the routes file ('command:action', 'SoftLayer.CLI.module.function')
        :param documented_commands: dictionary of commands found to be auto-documented.
        """

        # These commands use a slightly different loader. 
        ignored = [
            'virtual:capacity',
            'virtual:placementgroup',
            'object-storage:credential'
        ]
        if command[0] in ignored:
            return True
        if documented_commands.get(command[0], False) == command[1]:
            return True
        return False


    def main(self, debug=0):
        existing_commands = routes.ALL_ROUTES
        documented_commands = self.readDocs()
        # pp(documented_commands)
        exitCode = 0
        for command in existing_commands:
            if (command[1].find(":") == -1):  # Header commands in the routes file, dont need documentaiton.
                continue
            else:
                if self.checkCommand(command, documented_commands):
                    if debug:
                        print("{} is documented".format(command[0]))
                    
                else:
                    print("===> {} {} IS UNDOCUMENTED <===".format(command[0], command[1]))
                    exitCode = 1
        sys.exit(exitCode)


if __name__ == "__main__":
    main = Checker()
    main.main()
