from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet,arp,ipv4
from ryu.lib.packet import ether_types

from collections import deque

class SwitchAccessControl(app_manager.RyuApp):

    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    def __init__(self, *args, **kwargs):
        super(SwitchAccessControl, self).__init__(*args, **kwargs)
        self.dp_graph = {
            1: [2, 3, 4, 5, 6, 7, 8],
            2: [1],
            3: [1],
            4: [1],
            5: [1],
            6: [1],
            7: [1],
            8: [1]
        }
        self.mac_table = {}  #  {MAC1: (dpid, portNo), MAC2: (dpid, portNo)}
        self.arp_table = {}  #  {IP: MAC}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, event): # this method handles switch feature requests and we install initial flow to forward all the packets to the controller incase of a table miss.
        print("Initialising Datapath %d" %event.msg.datapath.id)
        self.install_init_rules(event) # send to the controller

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, event):
        pkt = packet.Packet(data=event.msg.data) # creating a packet with msg's data as payload
        eth = pkt.get_protocols(ethernet.ethernet)[0] # fetching ethernet dataframe
        if eth.ethertype == ether_types.ETH_TYPE_ARP: # handling ARP requests
            self.handle_ARP(event)
        elif eth.ethertype == ether_types.ETH_TYPE_IP: # handle Ip packet.
            self.handle_IP(event)

    def handle_ARP(self,event): # handle ARP packets
        datapath = event.msg.datapath # datapath connection
        ofproto = datapath.ofproto #ofproto of the datapath

        in_port = event.msg.match['in_port'] # port through which the switch recieved this packet
        parser = datapath.ofproto_parser
        pkt = packet.Packet(data=event.msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0] # fetching ethernet dataframe

        arp_pkt = pkt.get_protocol(arp.arp) # Extract ARP information from the received packet
        out_port = self.get_out_port(datapath.id, arp_pkt.dst_mac) or ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)] # Set action to forwarding packet out of "out port"
        match = parser.OFPMatch(eth_dst=eth.dst)
        self.add_flow(datapath, 1, match, actions, buffer_id=None) # Add flow to switch

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

        if self.check_access():  # TODO: Implement filtering in check_access() method
            out_port = self.get_out_port(datapath.id, eth.dst)
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

        else:
            # Add flow to drop packet
            self.block_traffic(datapath, 10, match)


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
            if dpid == dst_dpid:
                return dst_port
            else:
                return self.find_shortest_path(self.dp_graph, dpid, dst_dpid)[1]

    def check_access(self):
        #  TODO: Implement filtering logic here
        '''

        :return: True when access checks out for the packet
        '''
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

        # Flood all ARP traffic
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_ARP) #.
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match, instructions=inst)
        datapath.send_msg(mod)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):# Send flow_mod message to switch
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        idle_timeout=45 # idle-timeout set to 45 seconds
        hard_timeout=600
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
