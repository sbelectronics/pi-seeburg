import os
import select
import sys
import termios
import time
import traceback
import tty

import smbus
from seeburg_manager import parse_args
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

def main():
    args = parse_args()

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

    if args.interactive:
        print "q - quarter"
        print "d - dime"
        print "n - nickel"
        print "r - simulate a result"
        print "x - exit"

        print ""

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
                        seeburg.insert_nickel()
                    elif (ch == "r"):
                        selection = raw_input("Code (letter+digit):")
                        try:
                            print
                            seeburg.handle_result(seeburg.letter_to_number(selection[0]), int(selection[1:]))
                        except:
                            traceback.print_exc()
                    elif (ch == "x"):
                        break
        finally:
            termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)

    else:
        while True:
            time.sleep(1);

if __name__ == "__main__":
    main()