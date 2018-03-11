#! /bin/bash
cd /home/pi/pi-controller
nohup python ./controller.py --nokp1 --nokp2 --noelk > /tmp/pi-controller.out 2> /tmp/pi-controller.err &
