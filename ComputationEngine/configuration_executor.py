import sys
import array
import random

from deap import benchmarks, algorithms, base, creator, tools
from CommonTools import my_rand


__author__ = 'pita'

def execute(configuration, toolbox, comp_prop):
    try:
        # process each line in configuration
        for command in configuration.split('\n'):
            if command:
                # if line is command
    #            if " = " in command:
                    print "executing", command
                    exec command
                # if line should be evaluated
    #            else:
    #                print "evaluating: ", command
    #                eval(command)

    except SyntaxError as e:
        print "Syntax error", e.filename, e.offset, e.lineno, e.text
        return []
    except NameError as e:
        print "Name error", e.message
        return []
    except:
        print "Unexpected error in evaluating configuration:", sys.exc_info()[0]
        print configuration
        return []
    #else:
    #    return toolbox, comp_prop
