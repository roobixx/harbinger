#!/bin/sh

if ! IW=`/bin/which iw` ; then
        echo "Harbinger prequires 'iw', which is not installed."
        exit 1
fi

if ! PYTHON=`/bin/which python` ; then
        echo "Harbinger prequires 'python', which is not installed."
        exit 1
fi

if ! SCAPY=`/bin/which scapy` ; then
        echo "Harbinger requires 'scapy' which is not installed."
        exit 1
fi

SUDO=''

if test 'root' != `whoami` ; then
        SUDO=sudo
fi

$SUDO $IW dev wlan0 interface add mon0 type monitor
$SUDO ifconfig mon0 up
$SUDO $PYTHON ./sensor.py
$SUDO ifconfig mon0 down
$SUDO $IW dev mon0 del
