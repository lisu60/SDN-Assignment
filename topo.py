#!/usr/bin/env python

from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mininet.node import RemoteController
from mn_wifi.link import wmediumd
from sys import argv

'''
Use --remote option to specify remote controller
'''

net = Mininet_wifi(link=wmediumd)

########
# Nodes
#

# Switches
s1 = net.addSwitch('s1')  # core switch
s2 = net.addSwitch('s2')  # reception
s3 = net.addSwitch('s3')  # ground floor offices
s4 = net.addSwitch('s4')  # software lab
s5 = net.addSwitch('s5')  # seminar rooms
s6 = net.addSwitch('s6')  # proto lab
s7 = net.addSwitch('s7')  # 2nd floor offices
s8 = net.addSwitch('s8')  # building 2 office

# APs

ap1 = net.addAccessPoint('ap1', dpid='11') #17
ap2 = net.addAccessPoint('ap2', dpid='12') #18

# Hosts
recp1 = net.addHost('recp1', ip='10.0.1.176', defaultRoute='via 10.0.0.2')  # Reception
ogf1 = net.addHost('ogf1', ip='10.0.1.162', defaultRoute='via 10.0.0.2')    # Ground Floor Office
ogf2 = net.addHost('ogf2', ip='10.0.1.173', defaultRoute='via 10.0.0.2')
sl1 = net.addHost('sl1', ip='10.0.1.83', defaultRoute='via 10.0.0.2')       # Software Lab
sl2 = net.addHost('sl2', ip='10.0.1.115', defaultRoute='via 10.0.0.2')
sr1 = net.addHost('sr1', ip='10.0.1.24', defaultRoute='via 10.0.0.2')       # Seminar Room
sr2 = net.addHost('sr2', ip='10.0.1.51', defaultRoute='via 10.0.0.2')
srLect = net.addHost('srLect', ip='10.0.1.60', defaultRoute='via 10.0.0.2') # Lectern/Instructor PC
pl1 = net.addHost('pl1', ip='10.0.1.122', defaultRoute='via 10.0.0.2')      # Proto Lab
pl2 = net.addHost('pl2', ip='10.0.1.138', defaultRoute='via 10.0.0.2')
o2f1 = net.addHost('o2f1', ip='10.0.1.153', defaultRoute='via 10.0.0.2')    # 2nd Floor Office
o2f2 = net.addHost('o2f2', ip='10.0.1.156', defaultRoute='via 10.0.0.2')
o2fRsch = net.addHost('o2fRsch', ip='10.0.1.151', defaultRoute='via 10.0.0.2')  # Manager Researcher in 2nd Floor Office, has access to R&D servers
dr = net.addHost('dr', ip='10.0.1.158', defaultRoute='via 10.0.0.2')        # Demo room
obld21 = net.addHost('obld21', ip='10.0.2.33', defaultRoute='via 10.0.0.2') # Building 2 Office

server1 = net.addHost('server1', ip='10.0.0.5', defaultRoute='via 10.0.0.2')         # A generic intranet server, running a dummy HTTP service
rnd1 = net.addHost('rnd1', ip='10.0.0.129', defaultRoute='via 10.0.0.2')             # R&D server
backup1 = net.addHost('backup1', ip='10.0.0.172', defaultRoute='via 10.0.0.2')       # Backup server
videoFeed1 = net.addHost('videoFeed', ip='10.0.0.167', defaultRoute='via 10.0.0.2')  # Video feed server feeding demo room display
gateway = net.addHost('gateway', ip='0.0.0.0')          # Gateway to internet
inet1 = net.addHost('inet1', ip='37.54.205.13')         # A dummy internet server

# Stations

sta1 = net.addStation('sta1', ip='10.0.3.58')
sta2 = net.addStation('sta2', ip='10.0.3.161')


#
#
#########

net.configureWifiNodes()

#########
# Links
#

# Inter-switch Links
net.addLink(s1, s2, 2, 1)  # Core and Reception
net.addLink(s1, s3, 3, 1)  # Core and Ground Floor Offices
net.addLink(s1, s4, 4, 1)  # Core and Software Lab
net.addLink(s1, s5, 5, 1)  # Core and Seminar Rooms
net.addLink(s1, s6, 6, 1)  # Core and Proto Lab
net.addLink(s1, s7, 7, 1)  # Core and 2nd Floor Offices
net.addLink(s1, s8, 8, 1)  # Core and Building 2 Office

net.addLink(s1, ap1, 17, 2) # Core and AP1
net.addLink(s1, ap2, 18, 2) # Core and AP2


# Host Links
net.addLink(server1, s1)
net.addLink(rnd1, s1)
net.addLink(backup1, s1)
net.addLink(videoFeed1, s1)

net.addLink(recp1, s2)
net.addLink(ogf1, s3)
net.addLink(ogf2, s3)
net.addLink(sl1, s4)
net.addLink(sl2, s4)
net.addLink(sr1, s5)
net.addLink(sr2, s5)
net.addLink(srLect, s5)
net.addLink(pl1, s6)
net.addLink(pl2, s6)
net.addLink(o2f1, s7)
net.addLink(o2f2, s7)
net.addLink(o2fRsch, s7)
net.addLink(dr, s7)
net.addLink(obld21, s8)
net.addLink(s1, gateway)
net.addLink(gateway, inet1)

net.addLink(ap1, sta1)
net.addLink(ap2, sta2)

#
#
#########

# Add controller
if '--remote' in argv:
    c0 = net.addController('c0', controller=RemoteController)
else:
    c0 = net.addController('c0')

net.start()

# Start HTTP service on inet1
inet1.cmd('cd inet1')
inet1.cmd('python3 -m http.server 80 &')

# Start HTTP service on server1
server1.cmd('cd server1')
server1.cmd('python3 -m http.server 80 &')

# Enable routing and NAT on Gateway
gateway.setIP(ip='10.0.0.2', intf='gateway-eth0')
gateway.setIP(ip='37.54.205.12', intf='gateway-eth1')
gateway.cmd('echo "1" > /proc/sys/net/ipv4/ip_forward')
gateway.cmd('iptables -t nat -A POSTROUTING -o gateway-eth1 -j MASQUERADE')
gateway.cmd('iptables -A FORWARD -i gateway-eth1 -o gateway-eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
gateway.cmd('iptables -A FORWARD -i gateway-eth0 -o gateway-eth1 -j ACCEPT')

#c0.start()
ap1.start([c0])
ap2.start([c0])
CLI(net)
net.stop()
