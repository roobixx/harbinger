#!/usr/bin/env python
import socket, os, re, sys, sqlite3

from time import *
import time
import threading

DB_FILE = 'node.db'
MON_IFACE = 'mon0'

os.system('clear')

def getvendor(mac):
	prefix = mac[0:6].upper()
	if prefix == "FFFFFF":
		return "unk"

	for i in [s for s in ouis if prefix in s.replace("-", '').replace(":", '')]:
		if "#" in i:	delim = "#"
		else:	delim = "\t"

		return i.split(delim)[1].strip()

	return "unk"


def recordData(src, bssid, dst):
	cursor.execute("SELECT pcount FROM data WHERE ssid=? and bssid=? and dst=?", (src, bssid, dst))
	count = cursor.fetchone()
	if not count:
		#print "new data - %s >> %s >> %s"%(src,bssid,dst)
		cursor.execute("INSERT INTO data VALUES (?, ?, ?, '1', current_timestamp)", (src, bssid, dst))

	else:
		#print "updated probe - %s >> %s [%s]" % (src, essid, str(int(count[0])+1))
		cursor.execute("UPDATE data SET datetime=current_timestamp, pcount=? WHERE ssid=? and bssid=? and dst=?", (str(int(count[0])+1), src, bssid, dst))

	conn.commit()


def recordProbe(src, bssid, name, essid):
	cursor.execute("SELECT pcount FROM probes WHERE ssid=? and essid=?", (src, essid))
	count = cursor.fetchone()
	if essid != " ":
		if not count:
			print "new probe - %s (%s) >> %s (%s)  [%s]"%(src, getvendor(src), bssid, getvendor(bssid), essid)
			cursor.execute("INSERT INTO probes VALUES (?, ?, ?, '1', current_timestamp)", (src, essid, name))

		else:
			#print "updated probe - %s >> %s [%s]" % (src, essid, str(int(count[0])+1))
			cursor.execute("UPDATE probes SET datetime=current_timestamp, pcount=? WHERE ssid=? and essid=?", (str(int(count[0])+1), src, essid))

	conn.commit()


def recordAP(bssid, essid):
	cursor.execute("SELECT pcount,essid FROM ap WHERE bssid=?", (bssid,))
	dat = cursor.fetchone()
	if not dat:
		print "new ap - %s (%s) [%s]" % (bssid, getvendor(bssid), essid)
		cursor.execute("INSERT INTO ap VALUES (?, ?, '1', current_timestamp)", (bssid, essid))

	else:
		if essid not in "na|<hidden>|%s" % dat[1]:
			print "updated essid - %s [%s] (%s)  [%s pkts] " % (bssid, essid, getvendor(bssid), str(int(dat[0])+1))
			cursor.execute("UPDATE ap SET datetime=current_timestamp, essid=?, pcount=? WHERE bssid=?", (essid, str(int(dat[0])+1), bssid))
		else:
			#print "updated ap - %s [%s] (%s)  [%s]" % (bssid, essid, vendor, str(int(count[0])+1))
			cursor.execute("UPDATE ap SET datetime=current_timestamp, pcount=? WHERE bssid=?", (str(int(dat[0])+1), bssid))

	#cursor.execute("UPDATE probes SET essid=? WHERE bssid=?", (essid, bssid))
	conn.commit()	


def recordClient(src):
	cursor.execute("SELECT pcount FROM clients WHERE ssid=?", (src,))
	count = cursor.fetchone()
	if not count:
		print "new client - %s (%s) "%(src,getvendor(src))
		cursor.execute("INSERT INTO clients VALUES (?, '1', current_timestamp)", (src,))
	else:
		#print "updated client - %s [%s]"%(src,str(int(count[0])+1))
		cursor.execute("UPDATE clients SET datetime=current_timestamp, pcount=? WHERE ssid=?", (str(int(count[0])+1), src))

	conn.commit()	


def parsepkt(raw):

	pkt = raw.encode('hex')
	pkt_type = raw[26].encode('hex')

	if pkt_type == "40":	# client probe
		src = pkt[72:84]
		bssid = pkt[84:96]
		dst = pkt[60:72]
		name = ""
		if len(raw) > 51 and ord(raw[51]) > 0:	
			essid = raw[52:52+ord(raw[51])].replace("'","\'")
			for c in [ord(i) for i in essid]:
				if ( 126 < c < 160 ) or ( -1 < c < 32 ):
					essid = '<junk>'
					break
		else:
			essid = " "

		#print raw
		recordClient(src)
		recordProbe(src, bssid, name, essid)
	
	elif pkt_type == "80":	# AP beacon
		bssid = pkt[72:84]
		if len(raw) > 63 and ord(raw[63]) > 0:	
			essid = raw[64:64+ord(raw[63])].replace("'","\'")
			for c in [ord(i) for i in essid]:
				if ( 126 < c < 160 ) or ( -1 < c < 32 ):
					essid = ""
					break
		else:
			essid = "<hidden>"

		recordAP(bssid, essid)

	elif pkt_type in "a0|b0|10|c0|30|48|c8|08|88":   # [unk]  Client <--> AP
		dst = pkt[60:72]
		src = pkt[72:84]
		bssid = pkt[84:96]
		recordAP(bssid, "na")
		recordData(src, bssid, dst)

	elif pkt_type in "20|50|d0":   # [unk]  Client <--> AP with essid
		dst = pkt[60:72]
		src = pkt[72:84]
		bssid = pkt[84:96]
		if len(raw) > 63 and ord(raw[63]) > 0:	
			essid = raw[64:64+ord(raw[63])].replace("'","\'")
			for c in [ord(i) for i in essid]:
				if ( 126 < c < 160 ) or ( -1 < c < 32 ):
					essid = ""
					break
		else:
			essid = "<hidden>"

		recordAP(bssid, essid)
		recordData(src, bssid, dst)

	elif pkt_type in "00|37|41|42|6e|94|a4|b4|c4|d4|e4":   # mute these oddities
		pass
		#print
		#print raw
		#print "dst: "+pkt[60:72]
		#print pkt_type
		#print pkt
		#print
		
	else:
		# 84
		o = "\n%s" % (pkt_type)
		o += "\ndst: %s [%s]" % (pkt[60:72], getvendor(pkt[60:72]))
		o += "\nsrc: %s [%s]" % (pkt[72:84], getvendor(pkt[72:84]))
		o += "\nbssid: %s [%s]" % (pkt[84:96], getvendor(pkt[84:96]))
		o += "\n%s" % raw
		o += "\n%s\n" % pkt
		print "!!! Unknown !!!\n%s" % o
		open("log.txt", 'a').write(o)
 


rawSocket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0003))
try:
	rawSocket.bind((MON_IFACE, 0x0003))

except socket.error, ex:
	print str(ex) + "(%s)" % MON_IFACE
	exit(1)

newfile = False
if not os.path.exists(DB_FILE): 
	print "creating .db"
	newfile = True

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

if newfile == True:
	cursor.execute("CREATE TABLE clients (ssid, pcount, datetime);")
	cursor.execute("CREATE TABLE probes (ssid, essid, name, pcount, datetime);")
	cursor.execute("CREATE TABLE data (ssid, bssid, dst, pcount, datetime);")
	cursor.execute("CREATE TABLE ap (bssid, essid, pcount, datetime);")
	cursor.execute("CREATE TABLE misc (dst, src, bssid, pcount, datetime);")

ouis = open("manuf").read().split('\n')

try:
	while True:
		raw = rawSocket.recvfrom(2048)[0]
		parsepkt(raw)

except (KeyboardInterrupt, SystemExit):
	print "\nKilling Thread..."
	conn.close()


print "Done.\nExiting."
