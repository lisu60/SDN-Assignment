from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from sys import argv

'''
Use --remote option to specify remote controller
'''

net = Mininet()

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

# Hosts
recp1 = net.addHost('recp1', ip='10.0.1.176')  # Reception
ogf1 = net.addHost('ogf1', ip='10.0.1.162')    # Ground Floor Office
ogf2 = net.addHost('ogf2', ip='10.0.1.173')
sl1 = net.addHost('sl1', ip='10.0.1.83')       # Software Lab
sl2 = net.addHost('sl2', ip='10.0.1.115')
sr1 = net.addHost('sr1', ip='10.0.1.24')       # Seminar Room
sr2 = net.addHost('sr2', ip='10.0.1.51')
srLect = net.addHost('srLect', ip='10.0.1.60') # Lectern/Instructor PC
pl1 = net.addHost('pl1', ip='10.0.1.122')      # Proto Lab
pl2 = net.addHost('pl2', ip='10.0.1.138')
o2f1 = net.addHost('o2f1', ip='10.0.1.153')    # 2nd Floor Office
o2f2 = net.addHost('o2f2', ip='10.0.1.156')
o2fRsch = net.addHost('o2fRsch', ip='10.0.1.151')  # Manager Researcher in 2nd Floor Office, has access to R&D servers
dr = net.addHost('dr', ip='10.0.1.158')        # Demo room
obld21 = net.addHost('obld21', ip='10.0.2.33') # Building 2 Office

server1 = net.addHost('server1', ip='10.0.0.5')         # A generic intranet server, running a dummy HTTP service
rnd1 = net.addHost('rnd1', ip='10.0.0.129')             # R&D server
backup1 = net.addHost('backup1', ip='10.0.0.172')       # Backup server
videoFeed1 = net.addHost('videoFeed', ip='10.0.0.167')  # Video feed server feeding demo room display

#
#
#########

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

#
#
#########

# Add controller
if '--remote' in argv:
    c0 = net.addController('c0', controller=RemoteController)
else:
    c0 = net.addController('c0')

# Start HTTP service on server1
server1.cmd('cd server1')
server1.cmd('python3 -m http.server 80 &')


net.start()
CLI(net)
net.stop()
