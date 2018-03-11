#! /bin/bash
cd /home/pi/pi-seeburg
nohup python ./console_client.py -S http://198.0.0.215/stereo --nointeractive > /tmp/pi-seeburg.out 2> /tmp/pi-seeburg.err &
