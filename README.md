pi seeburg


Prevent sd-card wearout

Add to fstab:
tmpfs    /tmp            tmpfs    defaults,noatime,nosuid,size=100m    0 0
tmpfs    /var/tmp        tmpfs    defaults,noatime,nosuid,size=30m    0 0
tmpfs    /var/log        tmpfs    defaults,noatime,nosuid,mode=0755,size=100m    0 0
tmpfs    /var/runxx        tmpfs    defaults,noatime,nosuid,mode=0755,size=2m    0 0

Automatic Start

Add to crontab:
@reboot bash /home/pi/pi-seeburg/start_seeburg.sh &> /dev/null
@reboot bash /home/pi/pi-seeburg/start_controller.sh &> /dev/null
