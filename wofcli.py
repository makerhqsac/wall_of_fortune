#!/usr/bin/env python3
###############################################################################
# wofcli.py                                                                   #
#                                                                             #
#    Command line interface for running Wall of Fortune                       #
#                                                                             #
#    For more information, see https://github.com/makerhqsac/wall_of_fortune  #
#                                                                             #
#    Written By Mike Machado <mike@machadolab.com>                            #
#    Sponsored by MakerHQ - http://www.makerhq.org                            #
#                                                                             #
#    Licensed under the GPLv3 - https://www.gnu.org/licenses/gpl-3.0.txt      #
###############################################################################

import argparse
from utils import comms

def run_main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', action='store', help='set source name, defaults to admin')
    parser.add_argument('-m', '--message', action='store', help='message to send')
    args = parser.parse_args()

    wof = comms.Comms()

    if args.name:
        wof.begin(args.name)
    else:
        wof.begin('admin')

    wof.send(args.message)


# Main program logic follows:
if __name__ == '__main__':
    run_main()