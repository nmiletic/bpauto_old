#!/usr/bin/python3
"""Library for generating BreakingPoint TCL commands."""

from io import StringIO
import yaml
from itertools import cycle
from bp import BreakingPoint
import argparse
from pykwalify.core import Core

class AutoNetwork(object):

    def __init__(self, net_conf, bps):
        self._net_conf = net_conf
        self._network = bps.create_network(name=net_conf["Name"])
        self._mac = self._gen_mac()

    def save(self):
        self._network.save()

    def _gen_mac(self):
        for i in range(197, 255):
            for j in range(1, 255):
                yield "02:1A:{:02x}:{:02x}:00:00".format(i, j)

    def _get_ip_gen(self, ip_address, inc_mask):
        def gen_ip_address1(template, start, inc):
           for i in range(start, 255, inc):
               yield template.format(i)

        def gen_ip_address2(template, start1, start2, inc):
           for i in range(start1, 255):
               for j in range(start2, 255, inc):
                   yield template.format(i, j)

        octets = ip_address.split(sep='.')
        mask = inc_mask.split(sep='.')
        change_first = False
        if mask[0] != '0':
           start = octets[0]
           inc = mask[0]
           octets[0] = '{}'
           change_first = True
        elif mask[1] != '0':
           start1 = octets[0]
           start2 = octets[1]
           inc = mask[1]
           octets[0] = '{}'
           octets[1] = '{}'
        elif mask[2] !='0':
           start1 = octets[1]
           start2 = octets[2]
           inc = mask[2]
           octets[1] = '{}'
           octets[2] = '{}'
        elif mask[3] !='0':
           raise ErrorError
        template = '.'
        template = template.join(octets)
        if change_first:
           return gen_ip_address1(template, int(start), int(inc))
        else:
           return gen_ip_address2(template, int(start1), int(start2), int(inc))

    def generate_interfaces(self):
       def gen_int_num(start, inc):
           for i in range(start, 255, inc):
               yield i

       def gen_int_name(prefix, start, inc):
           for i in range(start, 255, inc):
               yield prefix + str(i)

       int_mac = self._mac
       for interface in self._net_conf["Interfaces"]:
           int_num = gen_int_num(interface["Start Number"], interface["Increment"])
           int_name = gen_int_name(interface["Name"], interface["Start Number"], interface["Increment"])
           for _ in range(interface["Count"]):
               self._network.add_interface(name=next(int_name),
                                           number=next(int_num),
                                           mac_address=next(int_mac),
                                           duplicate_mac_address=interface['Duplicate MAC address'])

    def generate_vlans(self):
        def gen_vlan_id(start, inc):
            for i in range(start, 4096, inc):
                yield i
        
        def gen_vlan_name(prefix, start, inc):
           for i in range(start, 4096, inc):
               yield prefix + str(i)

        for vlan in self._net_conf['VLANs']:
            vlan_name = gen_vlan_name(vlan['Name'], vlan['VLAN ID'], vlan['Increment'])
            container = cycle(self._network.get_container_group(vlan["Container"]))
            vlanid = gen_vlan_id(vlan['VLAN ID'], vlan['Increment'])
            vlan_mac = self._mac
            for _ in range(vlan['Count']):
                self._network.add_vlan(name=next(vlan_name), container=next(container), vlan=next(vlanid), mac_address=next(vlan_mac))

    def generate_ip_routers(self):
        def gen_ip_router_name(prefix):
           for i in range(1, 1000):
               yield prefix + str(i)

        for ip_routers in self._net_conf['IP Routers']:
            ip_address = self._get_ip_gen(ip_routers['IP Address'], ip_routers['Increment Mask'])
            gw_address = self._get_ip_gen(ip_routers['Gateway'], ip_routers['Increment Mask'])
            ip_router_name = gen_ip_router_name(ip_routers['Name'])
            container = cycle(self._network.get_container_group(ip_routers["Container"]))

            for _ in range(ip_routers['Count']):
                self._network.add_ip_router(name=next(ip_router_name), container=next(container),
                                            ip_address=next(ip_address), gateway=next(gw_address),
                                            netmask=ip_routers['Netmask'])

    def generate_hosts(self):
        def gen_hosts_name(prefix):
           for i in range(1, 1000):
               yield prefix + str(i)

        for hosts in self._net_conf['IP Static Hosts']:
           ip_address = self._get_ip_gen(hosts['IP Address'], hosts['Increment Mask'])
           if hosts['Gateway'] is not None:
               gw_address = self._get_ip_gen(hosts['Gateway'], hosts['Increment Mask'])
           else:
               gw_address = cycle([None])
           hosts_name = gen_hosts_name(hosts['Name'])
           tag = hosts['Name']
           container = cycle(self._network.get_container_group(hosts["Container"]))

           for _ in range(hosts['Count']):
               self._network.add_ip_static_hosts(name=next(hosts_name), tag=tag, container=next(container),
                                           ip_address=next(ip_address), count=hosts['IP Count'], netmask=hosts['Netmask'],
                                           gateway=next(gw_address))

        for hosts in self._net_conf['IP Static Hosts']:
            names = self._network.get_ip_static_hosts_group(hosts['Name'])
            peernames = self._network.get_ip_static_hosts_group(hosts['Path'])
            if len(names) > len(peernames):
                peernames = cycle(peernames)
            elif len(peernames) > len(names):
                names = cycle(names)
            for name, peer in zip(names, peernames):
                if not self._network.path_exists(name, peer):
                    self._network.add_path(name, peer)
                



class AutoBP(object):

    def __init__(self, conf):
        self._conn_conf = conf['Connection']
        self._gen_conf = conf['General']
        self._net_conf = conf['Network']

        self._bps = BreakingPoint(prefix=self._gen_conf['Prefix'])
        self._bps.connect(hostname=self._conn_conf['Tester IP'], login=self._conn_conf['Login'], password=self._conn_conf['Password'])

    def generate_network(self):
        self._network = AutoNetwork(self._net_conf, self._bps) 
        return self._network

    def save(self):
        self._bps.save()


def main():

    parser = argparse.ArgumentParser(
                 description='BP test automation.')
    parser.add_argument('config', metavar='conf.yaml',
               help='Configuration file in yaml.')
    parser.add_argument('-i', '--tester-ip',
               help='Tester management password.')
    parser.add_argument('-l', '--login',
               help='Tester management login username.')
    parser.add_argument('-p', '--password',
               help='Tester management password.')

    args = parser.parse_args()

    c = Core(source_file=args.config, schema_files=["schema.yaml"])
    c.validate(raise_exception=True)

    with open(args.config) as configfile:
        conf = yaml.load(configfile)

    if args.tester_ip:
        conf['Connection']['Tester IP'] = args.tester_ip
    if args.login:
        conf['Connection']['Login'] = args.login
    if args.password:
        conf['Connection']['Password'] = args.password

    autobp = AutoBP(conf)
    if 'Network' in conf:
        network = autobp.generate_network()
        if 'Interfaces' in conf['Network']:
            network.generate_interfaces()
        if 'VLANs' in conf['Network']:
            network.generate_vlans()
        if 'IP Routers' in conf['Network']:
            network.generate_ip_routers()
        if 'IP Static Hosts' in conf['Network']:
            network.generate_hosts()
        network.save()

    autobp.save()


if __name__ == "__main__":
    main()
