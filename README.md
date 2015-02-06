# Harbinger Sensor Network Project


Summary:


Features:
   - stores data in sqlite .db
   - db.py finds all interactions for a given ssid|essid

Getting started
===============
```
# git https://github.com/roobixx/harbinger.git
# cd harbinger/
# ./harbinger.sh

OR

# git https://github.com/roobixx/harbinger.git
# cd harbinger/
# airmon-ng start $wlan_interface
# python sensor.py
```
Viewing Data
============
To see all located data type:
```
# db.py -a 
```
To see all captured probes:
```
# ./db.py -p
```
To see all clients captured:
```
# ./db.py -s
```
To see all bssids captured:
```
# ./db.py -b
```
To see all essid captured:
```
# ./db.py -e
```
Core Contributers
=================

[Roobixx](https://github.com/roobixx) - Creator and Maintainer

[AL14S](https://twitter.com/al14s) - Original Code

Credits
=======
These are the projects that inspired this work. Check them out and support them if possible.

[CreepyDol](https://media.blackhat.com/us-13/US-13-OConnor-CreepyDOL-Cheap-Distributed-Stalking-Slides.pdf) by Malice Afterthought

[Snoopy](https://github.com/sensepost/snoopy-ng) & [Snoopy-NG](https://github.com/sensepost/Snoopy) by Sensepost

Licensing
=========
HSPN is licensed under the GNU Public License, Version 3.0. See
[LICENSE](https://github.com/docker/docker/blob/master/LICENSE) for the full
license text.


