#!/usr/bin/env python
import socket, os, re, sys, sqlite3, inspect

def getvendor(mac):
	prefix = mac[0:6].upper()
	if prefix == "FFFFFF":
		return "Broadcast"

	for i in [s for s in ouis if prefix in s.replace("-", '').replace(":", '')]:
		if "#" in i:	delim = "#"
		else:	delim = "\t"

		return i.split(delim)[1].strip()

	return "unk"

DB_FILE = 'node.db'

if len(sys.argv) > 1:
	if sys.argv[1] in ("-a","--all","-b","--bssid","-e","--essid","-s","--source","-p","--probes"):
		mode = sys.argv[1]
		
		if len(sys.argv) > 2:
			target = "%"+sys.argv[2].replace("%",'')+"%"

		else:
			target = "%%"

	else:
		print "unhandled option"
		exit(1)

	if len(sys.argv) > 2:
		if os.path.isfile(sys.argv[-1]):
			DB_FILE = sys.argv[-1]

else:
	print "missing arguments..."
	exit(1)


if not os.path.exists(DB_FILE): 
	print ".db not found"
	exit(1)

ouis = open("manuf").read().split('\n')
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

os.system('clear')
print "\n\n"

if '-e' in mode:
	cursor.execute("SELECT * FROM probes WHERE essid LIKE ?", (target,))
	print "Probes:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM ap WHERE essid LIKE ?", (target,))
	print "APs:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)

elif '-b' in mode:
	cursor.execute("SELECT * FROM data WHERE ssid LIKE ? OR bssid LIKE ? OR dst LIKE ?", (target,target,target))
	print "Data:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM ap WHERE bssid LIKE ?", (target,))
	print "APs:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)

elif '-s' in mode:
	cursor.execute("SELECT * FROM clients WHERE ssid LIKE ?", (target,))
	print "Clients:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM data WHERE ssid LIKE ? OR bssid LIKE ? OR dst LIKE ?", (target,target,target))
	print "Data:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM probes WHERE ssid LIKE ?", (target,))
	print "Probes:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)

elif '-p' in mode:
	cursor.execute("SELECT * FROM probes WHERE ssid LIKE ?", (target,))
	print "\nProbes:\n"
	print "   %12s   %26s   %26s   %26s   %6s   %19s" % ("BSSID", "VENDOR", "ID", "ESSID", "#", "DATETIME")
	for i in cursor.fetchall():
		n = i[2]
		if len(n) > 26:
			n = n[:22] + '...'

		e = i[1]
		if len(e) > 26:
			e = e[:22] + '...'

		v = getvendor(str(i[0]))
		if len(v) > 26:
			v = v[:22] + '...'

		print "   %s   %26s   %26s   %26s   %6s   %s" % (i[0], v, n, e, i[3], i[4])

	cursor.execute("SELECT * FROM ap WHERE bssid LIKE ?", (target,))
	print "\n\nAPs:\n"
	print "   %12s   %26s   %26s   %6s   %19s" % ("BSSID", "ESSID", "VENDOR", "#", "DATETIME")

	for i in cursor.fetchall():
		b = i[1]
		if len(b) > 26:
			b = b[:22] + '...'
		v = getvendor(str(i[0]))
		if len(v) > 26:
			v = v[:22] + '...'

		print "   %s   %26s   %26s   %6s   %s" % (i[0], b, v, i[2], i[4])

elif '-a' in mode:
	cursor.execute("SELECT * FROM clients WHERE ssid LIKE ?", (target,))
	print "Clients:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM data WHERE ssid LIKE ? OR bssid LIKE ? OR dst LIKE ?", (target,target,target))
	print "Data:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM probes WHERE ssid LIKE ?", (target,))
	print "Probes:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)
	cursor.execute("SELECT * FROM ap WHERE bssid LIKE ?", (target,))
	print "APs:"
	for i in cursor.fetchall():
		print '   '+'   '.join(i)

print "\n\n"
