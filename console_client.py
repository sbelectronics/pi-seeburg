import argparse
import os
import select
import sys
import termios
import tty

import smbus
from seeburg import SeeburgThread
from ioexpand import MCP23017

def getchar():
    fd = sys.stdin.fileno()
    old_tcattr = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_tcattr)
    return ch

def parse_args():
    parser = argparse.ArgumentParser()

    defs = {"vfd": False,
            "stereo_url": None}

    _help = 'Enable VFD display (default: %s)' % defs['vfd']
    parser.add_argument(
        '-V', '--vfd', dest='vfd', action='store_true',
        default=defs['vfd'],
        help=_help)

    _help = 'URL of Stereo to control (default: %s)' % defs['stereo_url']
    parser.add_argument(
        '-S', '--stereo_url', dest='stereo_url', action='store',
        default=defs['stereo_url'],
        help=_help)

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    print "q - quarter"
    print "d - dime"
    print "n - nickle"
    print "r - simulate a result (B1)"
    print "x - exit"

    print ""

    bus = smbus.SMBus(1)

    if args.vfd:
        from vfdcontrol import VFDController
        display = VFDController(MCP23017(bus, 0x20), enablePoller = False)
        display.setDisplay(True, False, False)
        display.cls()
        display.writeStr("Ready!")
        display.set_color(0)
    else:
        display = None

    if os.path.exists("titles/song_table.py"):
        from titles.song_table import song_table
    else:
        song_table = {}

    seeburg = SeeburgThread(bus, 0x21, vfd=display, stereo_url=args.stereo_url, song_table=song_table)
    seeburg.start()

    stdin_fd = sys.stdin.fileno()
    new_term = termios.tcgetattr(stdin_fd)
    old_term = termios.tcgetattr(stdin_fd)
    new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, new_term)

    try:
        while True:
            dr,dw,de = select.select([sys.stdin], [], [], 0.1)
            if dr != []:
                ch = sys.stdin.read(1)

                if (ch == "q"):
                    seeburg.insert_quarter()
                elif (ch == "d"):
                    seeburg.insert_dime()
                elif (ch == "n"):
                    seeburg.insert_nickle()
                elif (ch == "r"):
                    seeburg.handle_result(2,1)
                elif (ch == "x"):
                    break
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)

if __name__ == "__main__":
    main()