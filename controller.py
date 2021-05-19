from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet,arp,ipv4
from ryu.lib.packet import ether_types

from collections import deque

# Liying: testing
import ipaddress

class SwitchAccessControl(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(SwitchAccessControl, self).__init__(*args, **kwargs)
        self.dp_graph = {
            1: [2, 3, 4, 5, 6, 7, 8, 17],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: [1],
            7: [1],
            8: [1, 18],
            17: [1],
            18: [8]
        }
        self.ap_dpid = [17, 18]
        self.mac_table = {}  #  {MAC1: (dpid, portNo), MAC2: (dpid, portNo)}
        self.arp_table = {}  #  {IP: MAC}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, event): # this method handles switch feature requests and we install initial flow to forward all the packets to the controller incase of a table miss.
        self.logger.info("Initialising Datapath %d" %event.msg.datapath.id)
        self.install_init_rules(event) # send to the controller

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        pkt = packet.Packet(data=event.msg.data) # creating a packet with msg's data as payload
        eth = pkt.get_protocols(ethernet.ethernet)[0] # fetching ethernet dataframe
        if eth.ethertype == ether_types.ETH_TYPE_ARP: # handling ARP requests
            self.handle_ARP(event)
        elif eth.ethertype == ether_types.ETH_TYPE_IP: # handle Ip packet.
            self.handle_IP(event)

    def handle_IP(self, event):  # handle IP packets
        datapath = event.msg.datapath  # datapath connection
        ofproto = datapath.ofproto  # ofproto of the datapath
        in_port = event.msg.match['in_port']  # port through which the switch received this packet
        parser = datapath.ofproto_parser
        pkt = packet.Packet(data=event.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]  # Extract ethernet frame
        ip_pkt = pkt.get_protocol(ipv4.ipv4)  # extract Ip payload
        if eth.src not in self.mac_table:
            self.mac_table[eth.src] = (datapath.id, in_port)
        self.arp_table[ip_pkt.src] = eth.src

        # Use strict match to ensure filtering works
        match = parser.OFPMatch(eth_src=eth.src, eth_dst=eth.dst, in_port=in_port)
        # match = parser.OFPMatch(eth_src=eth.src, eth_dst=eth.dst, ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst, in_port=in_port)
        # ipv4_src and ipv4_dst fields somehow cause the flow not added to the switches


        #liying: pass 2 arguments in_pkt.src and in_pkt.dst
        if self.check_access(ip_pkt.src, ip_pkt.dst):  # TODO: Implement filtering in check_access() method
            # To filter flooded-back packets
            if not self.is_on_path(eth.src, datapath.id, in_port):
                return
            out_port = self.get_out_port(datapath.id, eth.dst)
            if in_port == out_port:
                return
            if not out_port:
                # Flood the packet if out_port not found
                self.switchport_out(pkt, datapath, ofproto.OFPP_FLOOD)
            else:
                # Create a flow
                actions = [parser.OFPActionOutput(port=out_port)]
                if event.msg.buffer_id != ofproto.OFP_NO_BUFFER:
                    self.add_flow(datapath, 10, match, actions, event.msg.buffer_id)
                else:
                    self.add_flow(datapath, 10, match, actions)
                self.switchport_out(pkt, datapath, out_port)

        else:
            # Add flow to drop packet
            self.block_traffic(datapath, 10, match)

    def is_on_path(self, eth_src, current_dpid, in_port):
        if self.mac_table[eth_src][0] == current_dpid:
            return True
        previous_dpid = self.dp_graph[current_dpid][0] if current_dpid in self.ap_dpid else in_port
        if previous_dpid in self.find_shortest_path(self.dp_graph, self.mac_table[eth_src][0], current_dpid):
            return True
        else:
            return False



    def find_shortest_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in graph:
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = self.find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

    def get_out_port(self, dpid, dst_mac):

        if dst_mac in self.mac_table:
            dst_dpid, dst_port = self.mac_table[dst_mac]
            if dpid in self.ap_dpid:
                if dpid == dst_dpid:
                    return 1
                else:
                    return 2
            if dpid == dst_dpid:
                return dst_port
            else:
                return self.find_shortest_path(self.dp_graph, dpid, dst_dpid)[1]

    def check_access(self, ipSrc, ipDst):
        #  TODO: Implement filtering logic here
        '''
        :return: True when access checks out for the packet
        '''
        # test
        # Check ip address (source): Demo room can only access the video feed server
        if ipSrc == '10.0.1.158':
            if ipDst == '10.0.0.167': # Video Feed Server:
                return True
            else:
                return False
        # Check ip address (dst): video feed server only can be accessed by the demo room
        elif ipDst == '10.0.0.167':
            if ipSrc == '10.0.1.158':
                return True
            else:
                return False

        # Check ip address (dst): backup servers can be accessed by all hosts but not demo room and Building 2 IoT 
        elif ipDst == '10.0.0.172':
            if ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.160/28') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.176/30') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.64/26') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.0/26') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.128/28') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.144/28') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.3.0/24') or \
                ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.2.32/29'):
                return True
            else:
                return False

        # Check ip address (dst): R&D servers can only be accessed by 1 researcher in mgmt and Proto lab
        elif ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.128/30'):
            if ipSrc == '10.0.1.151' or ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.128/28'):
                return True
            else:
                return False

        # Check ip address (source): laptops (wireless access) can only access the backup servers and internet
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.3.0/24'):
            if ipDst == '10.0.0.172' or ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8'):
                return True
            else:
                return False
  
        # Check ip address (source): Reception and Building 2 Office including IoT can only access intranet
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.176/30') or \
            ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.2.32/29') or \
            ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.2.0/27'):
            if ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.0/24'):
                return True
            else: 
                return False

        # Check ip address (source): only GF Offices, Software Lab, Serminar Room (Lectern) can have access to
        # to both intranet and internet
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.160/28') or \
            ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.64/26') or \
            ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.60/31'):
             if ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.0/24') or \
                 ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8'):
                return True
             else: 
                return False

        # Check ip address (source): Seminar Rooms (Lab PCs) can have access to Internet
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.0/26'):
            if ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8'):
                return True
            else: 
                return False

        # Check ip address (source): 1 researcher in mgmt office can access internet and R&D server
        elif ipSrc == '10.0.1.151':
            if ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.128/30') or \
                ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8'):
                return True
            else: 
                return False
     
        # Check ip address (source): mgmt offices can have access to Internet
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.144/28'):
            if ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8'):
                return True
            else: 
                return False

        # Check ip address (source): Proto lab can access intranet, internet and R&D server:
        elif ipaddress.IPv4Address(ipSrc) in ipaddress.IPv4Network('10.0.1.128/28'):
            if ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.0/24') or \
                ipaddress.IPv4Address(ipDst) not in ipaddress.IPv4Network('10.0.0.0/8') or \
                ipaddress.IPv4Address(ipDst) in ipaddress.IPv4Network('10.0.0.128/30'):
                return True
            else: 
                return False

        # All servers are allowed to return traffic
        else:
            return True

    def install_init_rules(self, event): # initial installation of table miss flow
        datapath = event.msg.datapath #.
        ofproto = datapath.ofproto #.
        parser = datapath.ofproto_parser #.
        match = parser.OFPMatch() #.
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)] # send to controller
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)

        if event.msg.datapath.id in self.ap_dpid:
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP, in_port=1)  # .
            actions = [parser.OFPActionOutput(2)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
            datapath.send_msg(mod)
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP, in_port=2)  # .
            actions = [parser.OFPActionOutput(1)]
            inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
            datapath.send_msg(mod)

        else:

             # Flood all ARP traffic
             match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP) #.
             actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
             inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
             mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
             datapath.send_msg(mod)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):# Send flow_mod message to switch
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        idle_timeout=600
        hard_timeout=1800
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)] #forming instructions
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id, priority=priority, idle_timeout=idle_timeout, hard_timeout=hard_timeout, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, idle_timeout=idle_timeout, hard_timeout=hard_timeout, instructions=inst)

        self.logger.info("added flow for %s",mod)
        datapath.send_msg(mod)

    def block_traffic(self, datapath, priority, match):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        idle_timeout=45 # idle-timeout set to 45 seconds
        hard_timeout=600
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_CLEAR_ACTIONS, [])] #forming instructions
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, idle_timeout=idle_timeout, hard_timeout=hard_timeout, instructions=inst)
        datapath.send_msg(mod)


    #### request the packet to be forwarded onto a specific port from the switch ###
    def switchport_out(self, pkt, datapath, port): #.
        '''accept raw data , serialise it and packetout from a OF switch ''' #
        ofproto = datapath.ofproto #.
        parser = datapath.ofproto_parser #.
        pkt.serialize() #. serialise packet (ie convert raw data)
        self.logger.info("packet-out %s" %(pkt,)) #.
        data = pkt.data #.
        actions = [parser.OFPActionOutput(port=port)] #.
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=ofproto.OFPP_CONTROLLER, actions=actions, data=data) #.
        datapath.send_msg(out) #.
