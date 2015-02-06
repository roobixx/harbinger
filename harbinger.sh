sudo iw dev wlan0 interface add mon0 type monitor
sudo ifconfig mon0 up
sudo python ./sensor.py
sudo ifconfig mon0 down
sudo iw dev mon0 del
