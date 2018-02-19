import select
import sys
import termios
import tty

import smbus
from seeburg import SeeburgThread
from ioexpand import MCP23017
from vfdcontrol import VFDController

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
    print "q - quarter"
    print "d - dime"
    print "n - nickle"
    print "x - exit"

    print ""

    bus = smbus.SMBus(1)

    if True:
        display = VFDController(MCP23017(bus, 0x20), enablePoller = False)
        display.setDisplay(True, False, False)
        display.cls()
        display.writeStr("scott")
        display.set_color(0)
    else:
        display = None

    seeburg = SeeburgThread(bus, 0x21, vfd=display)
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
                elif (ch == "x"):
                    break
    finally:
        termios.tcsetattr(stdin_fd, termios.TCSAFLUSH, old_term)

if __name__ == "__main__":
    main()