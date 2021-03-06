#!/usr/bin/env python3

'''
Basic IPv4 router (static routing) in Python.
'''

import sys
import os
import time

from switchyard.lib.packet.util import *
from switchyard.lib.userlib import *

class Router(object):
    def __init__(self, net):
        self.net = net
        # other initialization stuff here
        arp_table = dict()
        my_interfaces = net.interfaces()
        self.my_ips = [intf.ipaddr for intf in my_interfaces]
        self.mac_ip_dict = dict((intf.ipaddr, intf.ethaddr) for intf in my_interfaces)

    def router_main(self):    
        '''
        Main method for router; we stay in a loop in this method, receiving
        packets until the end of time.
        '''
        while True:
            gotpkt = True
            try:
                timestamp,dev,pkt = self.net.recv_packet(timeout=1.0)
                if pkt.has_header(Arp):
                    arp = pkt.get_header(Arp)
                    if arp.targetprotoaddr in self.my_ips:
                        senderhwaddr = self.mac_ip_dict[arp.targetprotoaddr]
                        senderprotoaddr = arp.targetprotoaddr
                        targethwaddr = arp.senderhwaddr
                        targetprotoaddr = arp.senderprotoaddr
                        arp_reply = create_ip_arp_reply(senderhwaddr, targethwaddr, senderprotoaddr, targetprotoaddr)
                        self.net.send_packet(dev, arp_reply)
            except NoPackets:
                log_debug("No packets available in recv_packet")
                gotpkt = False
            except Shutdown:
                log_debug("Got shutdown signal")
                break

            if gotpkt:
                log_debug("Got a packet: {}".format(str(pkt)))



def main(net):
    '''
    Main entry point for router.  Just create Router
    object and get it going.
    '''
    r = Router(net)
    r.router_main()
    net.shutdown()
