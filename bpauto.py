#!/usr/bin/python3
"""Library for generating BreakingPoint TCL commands."""

from io import StringIO
import yaml
from itertools import cycle
from bp import BreakingPoint
import argparse
from pykwalify.core import Core
from ipaddress import IPv4Address
from payload import PayloadFile
from copy import deepcopy

class AutoTest(object):

    def __init__(self, prefix, test_conf, bps, app_profile_conf):
        self._prefix = prefix
        self._bps = bps
        self._test_conf = test_conf
        self._app_profile_conf = app_profile_conf
        self._test = self._bps.create_test(name=self._prefix + test_conf['Name'])
        self._test.configure('-neighborhood', '"{0}"'.format(self._prefix + test_conf['Network']))

    def _gen_comp(self, comp_conf):
        comp = self._test.create_component(comp_conf['Type'], comp_conf['Name'])
        comp.configure('-description', '""')
        comp.configure('-profile', '"{0}"'.format(comp_conf['Application Profile']))
        comp.configure('-rampDist.up', comp_conf['Ramp Up Duration'])
        comp.configure('-rampDist.upBehavior', 'full+data+close')
        comp.configure('-rampDist.steady', comp_conf['Steady State Duration'])
        comp.configure('-rampDist.steadyBehavior', 'cycle')
        comp.configure('-rampDist.down', comp_conf['Ramp Down Duration'])
        comp.configure('-rampDist.downBehavior', 'full')
        comp.configure('-rampUpProfile.max', comp_conf['Max Sessions per sec'])
        comp.configure('-rampUpProfile.interval', '1')
        comp.configure('-rampUpProfile.min', '1')
        comp.configure('-rampUpProfile.type', 'step')
        comp.configure('-rateDist.scope', 'per_if')
        increment = max(1, round(comp_conf['Max Sessions per sec']/comp_conf['Ramp Up Duration']))
        comp.configure('-rampUpProfile.increment', increment)
        comp.configure('-sessions.max', comp_conf['Max Sessions'])
        comp.configure('-sessions.maxPerSecond', comp_conf['Max Sessions per sec'])
        comp.configure('-tcp.retries', '7')
        comp.configure('-tcp.retry_quantum_ms', '2000')
        comp.configure('-srcPortDist.type', 'range')
        comp.configure('-client_tags', comp_conf['Client Tags'])
        comp.configure('-server_tags', comp_conf['Server Tags'])

    def generate_components(self):
        for comp_conf in self._test_conf['Components']:
            if comp_conf['Name'] == 'AUTOMATIC':
                profile = next(item for item in self._app_profile_conf if item['Name'] == comp_conf['Application Profile'])
                comp_conf_cpy = deepcopy(comp_conf)
                total_weight = sum(superflow['Weight'] for superflow in profile['Super Flows'])
                for superflow in profile['Super Flows']:
                    ap = self._bps.create_app_profile(self._prefix + superflow['Name'] + ' ap')
                    ap.add_superflow(self._prefix + superflow['Name'], 100)
                    ap.save()
                    comp_conf_cpy['Name'] = superflow['Name']
                    comp_conf_cpy['Application Profile'] = self._prefix + superflow['Name'] + ' ap'
                    comp_conf_cpy['Max Sessions per sec'] = round((superflow['Weight']/total_weight)*comp_conf['Max Sessions per sec'])
                    self._gen_comp(comp_conf_cpy)
            else:
                self._gen_comp(comp_conf)
            
    def save(self):
        self._test.save()


class AutoNetwork(object):

    def __init__(self, prefix, net_conf, bps):
        self._net_conf = net_conf
        self._network = bps.create_network(name=prefix + net_conf["Name"])
        self._mac = self._gen_mac()

    def save(self):
        self._network.save()

    def _gen_mac(self):
        for i in range(197, 255):
            for j in range(1, 255):
                yield "02:1A:{:02x}:{:02x}:00:00".format(i, j)

    def _gen_ip(self, ip_address, inc_mask):
        ip = IPv4Address(ip_address)
        inc = IPv4Address(inc_mask)
        while True:
            ip = ip + int(inc)
            yield ip

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
            ip_address = self._gen_ip(ip_routers['IP Address'], ip_routers['Increment Mask'])
            gw_address = self._gen_ip(ip_routers['Gateway'], ip_routers['Increment Mask'])
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
           ip_address = self._gen_ip(hosts['IP Address'], hosts['Increment Mask'])
           if hosts['Gateway'] is not None:
               gw_address = self._gen_ip(hosts['Gateway'], hosts['Increment Mask'])
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
        self._conf = conf
        self._conn_conf = conf['Connection']
        self._gen_conf = conf['General']
        self._prefix=self._gen_conf['Prefix']

        self._bps = BreakingPoint(prefix=self._prefix)
        self._bps.connect(hostname=self._conn_conf['Tester IP'], login=self._conn_conf['Login'], password=self._conn_conf['Password'])

    def generate_network(self):
        self._net_conf = self._conf['Network']
        self._network = AutoNetwork(self._prefix, self._net_conf, self._bps) 
        return self._network

    def generate_test(self):
        self._test_conf = self._conf['Test']
        self._app_profile_conf = self._conf['Application Profiles']
        self._test = AutoTest(self._prefix, self._test_conf, self._bps, self._app_profile_conf) 
        return self._test

    def generate_superflows(self):
        payload = PayloadFile()
        upload_conf = self._conf['FileUpload']
        for superflow in self._conf['Super Flows']:
            sf = self._bps.create_superflow(self._prefix + superflow['Name'], superflow['Application'])
            if 'File Type' in superflow:
                filename = self._gen_conf['Prefix'] + superflow['File Type'] + str(superflow['Transation Size'])
                filename = filename.replace(" ", "_")
                payload.generate_file(filename, superflow['Transation Size'], superflow['File Type'])
                payload.upload_file(filename, upload_conf['Tester IP'], upload_conf['Login'], upload_conf['Password'])

                sf.modify(tsize=superflow['Transation Size'], filename=filename)
            elif 'Transation Size' in superflow:
                sf.modify(tsize=superflow['Transation Size'])
            sf.save()

    def generate_app_profiles(self):
        for app_profile in self._conf['Application Profiles']:
            ap = self._bps.create_app_profile(self._prefix + app_profile['Name'])
            ap.configure(app_profile['Weight According to'])
            for superflow in app_profile['Super Flows']:
                ap.add_superflow(self._gen_conf['Prefix'] + superflow['Name'], superflow['Weight'])
            ap.save()

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

#    c = Core(source_file=args.config, schema_files=["schema.yaml"])
#    c.validate(raise_exception=True)

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
    if 'Super Flows' in conf:
        autobp.generate_superflows()
    if 'Application Profiles' in conf:
        autobp.generate_app_profiles()
    if 'Test' in conf:
        test = autobp.generate_test()
        test.generate_components()
        test.save()

    autobp.save()


if __name__ == "__main__":
    main()
