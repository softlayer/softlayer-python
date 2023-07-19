from SoftLayer.CLI import environment
from click.testing import CliRunner
from SoftLayer.CLI.core import cli
import itertools

runner = CliRunner()
env = environment.Environment()
env.load()
TopLevelCommands = env.list_commands()


def findHelp(Table):
    for row in Table:
        if '--help' in row:
            return True
    return False


def findCorrectFlagTable(arrayCommandByLine):
    cont = 0
    arrayTable = []
    for line in arrayCommandByLine:
        if '─' in line:
            cont += 1
        if cont == 2:
            if not findHelp(arrayTable):
                arrayTable = []
            cont = 0
        if '│' in line:
            arrayTable.append(line)
    return arrayTable


def getFlags(arrayCommandByLine):
    flags = []
    arrayFlagsTable = findCorrectFlagTable(arrayCommandByLine)

    for line in arrayFlagsTable:
        arrayFlags = line.split('│')
        if arrayFlags[1].strip() != '':
            flags.append(f'{arrayFlags[1].strip()},{arrayFlags[2].strip()}: {arrayFlags[3].strip()}')
        else:
            flags.append(f'{arrayFlags[2].strip()}: {arrayFlags[3].strip()}')
    return flags


def findCommandNested(arrayCommandByLine):
    commandNested = False
    commands = []
    for line in arrayCommandByLine:
        if commandNested:
            nestedCommand = line.split(' ')
            commands.append(nestedCommand[2])
        if 'Commands:' in line:
            commandNested = True
    return commands


def printCommandName(TopLevelCommand, command, nestedCommandName=''):
    if nestedCommandName != '':
        f.write(f'slcli {TopLevelCommand} {command} {nestedCommandName}\n')
    else:
        f.write(f'slcli {TopLevelCommand} {command}\n')


def printBody(commandArray):
    for flag in getFlags(commandArray):
        f.write(f'\tFlag: {flag}\n')
    f.write("\t--------------------------------\n")
    f.write(f'\tDescription: {commandArray[2].strip()}\n')
    f.write("\t--------------------------------\n")
    list_of_strings = "".join(commandArray[0])
    command_strings=list_of_strings.replace("Usage: cli","Usage: slcli")
    grouped_strings = ["".join(g) for k, g in itertools.groupby(command_strings, lambda x: x == " ") if not k]
    f.write(f'\t{" ".join(grouped_strings)}\n')
    f.write("==============================================================\n")


# Main Function
with open('output.txt', "w", encoding="utf-8") as f:
    f.write('SLCLI Command Directory\n')
    f.write("==============================================================\n")

    for TopLevelCommand in TopLevelCommands:
        commands = env.list_commands(TopLevelCommand)
        for command in commands:
            result = runner.invoke(cli, [TopLevelCommand, command, '--help'])
            commandArray = result.output.splitlines()
            nestedCommands = findCommandNested(commandArray)
            if len(nestedCommands) != 0:
                for nestedCommand in nestedCommands:
                    result = runner.invoke(cli, [TopLevelCommand, command, nestedCommand, '--help'])
                    commandArray = result.output.splitlines()
                    printCommandName(TopLevelCommand, command, nestedCommand)
                    printBody(commandArray)
            else:
                printCommandName(TopLevelCommand, command)
                printBody(commandArray)
