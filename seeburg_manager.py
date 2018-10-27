import argparse
import os
import smbus
from seeburg import SeeburgThread
from ioexpand import MCP23017

glo_seeburg = None

def parse_args():
    parser = argparse.ArgumentParser()

    defs = {"vfd": False,
            "interactive": True,
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

    _help = 'Disable interactive console (default: %s)' % defs['interactive']
    parser.add_argument(
        '-N', '--nointeractive', dest='interactive', action='store_false',
        default=defs['interactive'],
        help=_help)

    args = parser.parse_args()

    return args

def startup(args):
    global glo_seeburg
   
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

    glo_seeburg = seeburg
