from scapy.all import *
from datetime import datetime
import socket, os, re, sys, sqlite3

DB_FILE = 'node.db'
PROBE_REQUEST_TYPE=0
PROBE_REQUEST_SUBTYPE=4

newfile = False
if not os.path.exists(DB_FILE): 
    print "creating .db"
    newfile = True

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

if newfile == True:
    # cursor.execute("CREATE TABLE clients (id, node_id, macaddr, dstaddr, ssid, rssi, timestamp);")

    conn.execute('''CREATE TABLE clients
       (ID INTEGER PRIMARY KEY autoincrement NOT NULL,
       node_id char(20) NOT NULL,
       macaddr char(50) NOT NULL,
       dstaddr char(50) NOT NULL,
       ssid text NOT NULL,
       rssi char(4) NOT NULL,
       timestamp char(50) NOT NULL);''')

    conn.execute('''CREATE TABLE aps
       (ID INTEGER PRIMARY KEY autoincrement NOT NULL,
       node_id char(20) NOT NULL,
       macaddr char(50) NOT NULL,
       ssid text NOT NULL,
       rssi char(10) NOT NULL,
       timestamp char(50) NOT NULL);''')

def updateClients(mac, dstaddr, ssid, rssi, timestamp) :

    conn.execute("insert into clients (node_id, macaddr, dstaddr, ssid, rssi, timestamp) values (?,?,?,?,?,?)", ("test", mac, dstaddr, ssid, rssi, timestamp))
    conn.commit()

def updateAP(mac, ssid, rssi, timestamp) :

    cursor.execute("SELECT * FROM aps WHERE macaddr=?", (mac,))
    dat = cursor.fetchone()
    if not dat:
        print "New AP found: %s" %(mac)
        conn.execute("insert into aps (node_id, macaddr, ssid, rssi, timestamp) values (?,?,?,?,?)", ("test", mac, ssid, rssi, timestamp))
        conn.commit()



def PacketHandler(pkt):
    if pkt.haslayer(Dot11):
        if pkt.type==PROBE_REQUEST_TYPE and pkt.subtype == PROBE_REQUEST_SUBTYPE:
            recordClient(pkt)
        elif pkt.type==PROBE_REQUEST_TYPE and pkt.subtype == 8:
            recordAP(pkt)

def recordClient(pkt):
    #print "Probe Request Captured:"
    try:
        extra = pkt.notdecoded
    except:
        extra = None
    if extra!=None:
        signal_strength = -(256-ord(extra[-4:-3]))
    else:
        signal_strength = -100
        print "No signal strength found"    
    print "Target: %s Source: %s SSID: %s RSSi: %d TIMESTAMP: %s"%(pkt.addr3,pkt.addr2,pkt.getlayer(Dot11ProbeReq).info,signal_strength,datetime.now())
    updateClients(pkt.addr2, pkt.addr3, pkt.info, signal_strength, datetime.now())

def recordAP(pkt):
    try:
        extra = pkt.notdecoded
    except:
        extra = None
    if extra!=None:
        signal_strength = -(256-ord(extra[-4:-3]))
    else:
        signal_strength = -100
        print "No signal strength found"
    updateAP(pkt.addr2, pkt.info, signal_strength, datetime.now())


def main():
    from datetime import datetime
    print "[%s] Starting scan"%datetime.now()
    sniff(iface='mon0',prn=PacketHandler, store=0)
 
connection = sqlite3.connect(DB_FILE)

ouis = open("manuf").read().split('\n')

if __name__=="__main__":
    main()

connection.close