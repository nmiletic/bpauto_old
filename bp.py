#!/usr/bin/python3
"""Library for generating BreakingPoint TCL commands."""

from io import StringIO
import yaml
from itertools import cycle

class TCLFiles(object):
    def __init__(self):
        self._createbuf = StringIO()
        self._deletebuf = StringIO()

    def pcreate(self, command):
        print(command, file=self._createbuf)

    def pdelete(self, command):
        print(command, file=self._deletebuf)

    def save_create(self, prefix):
        filename = prefix + 'create.tcl'
        with open(filename, 'w') as createfile:
            createfile.write(self._createbuf.getvalue())


class BreakingPoint(object):
    def __init__(self, *, prefix=None):
        self._prefix = prefix
        self.tfiles = TCLFiles()
        self._network = None

    def connect(self, *, hostname=None, login='admin', password='admin'):
        command = ('set bps [bps::connect "{HOSTNAME}" "{LOGIN}" "{PASSWORD}" '
                   '-onclose exit -shortcuts true]')
        self.tfiles.pcreate(command.format(HOSTNAME=hostname, LOGIN=login, PASSWORD=password))

    def save(self):
        self.tfiles.save_create(self._prefix)

    def create_network(self, name='NN'):
        command = ('set n [$bps createNetwork -name "{PREFIX}{NAME}"]')
        self.tfiles.pcreate(command.format(NAME=name, PREFIX=self._prefix))
        self._network = Network(self.tfiles, self._prefix + name)
        command = ('$n begin')
        self.tfiles.pcreate(command)
        return self._network


class Network(object):
    def __init__(self, tfiles, name):
        self._name = name
        self.tfiles = tfiles
        self._interfaces = []
        self._containers = []
        self._ip_static_hosts = []
        self._paths = []

    def add_interface(self, name, number, mac_address, duplicate_mac_address=False):
        if duplicate_mac_address:
            duplicate_mac_address = 1
        else:
            duplicate_mac_address = 0
        command = '$n add interface -number {NUMBER} -id "{ID}" -mac_address "{MAC}" -duplicate_mac_address {DMA}'
        self.tfiles.pcreate(command.format(NUMBER=number,
                                           ID=name,
                                           MAC=mac_address,
                                           DMA=duplicate_mac_address))
        self._interfaces.append(name)
        self._containers.append(name)

    def add_vlan(self, name, container, vlan, mac_address):
        command = '$n add vlan -id {ID} -default_container "{CONTAINER}" -inner_vlan {VLAN} -mac_address "{MAC}" -duplicate_mac_address 1'
        self.tfiles.pcreate(command.format(ID=name, CONTAINER=container, VLAN=vlan, MAC=mac_address))
        self._containers.append(name)

    def add_ip_router(self, name, container, ip_address, gateway, netmask):
        command = ('$n add ip_router -id "{NAME}" '
                   '-default_container "{CONTAINER}" -ip_address "{IP}" '
                   '-gateway_ip_address "{GATEWAY}" -netmask {NETMASK}')
        self.tfiles.pcreate(command.format(NAME=name,
                                           CONTAINER=container,
                                           IP=ip_address,
                                           NETMASK=netmask,
                                           GATEWAY=gateway))
        self._containers.append(name)

    def add_ip_static_hosts(self, name, tag, container, ip_address, count, netmask, gateway):
        if gateway is not None:
            command = ('$n add ip_static_hosts -id "{NAME}" '
                       '-tags [list "{NAME}" "{TAG}"] '
                       '-default_container "{CONTAINER}" -ip_address "{IP}" '
                       '-count {COUNT} -netmask {NETMASK} '
                       '-gateway_ip_address "{GATEWAY}"')
            self.tfiles.pcreate(command.format(NAME=name,
                                               TAG=tag,
                                               CONTAINER=container,
                                               IP=ip_address,
                                               COUNT=count,
                                               NETMASK=netmask,
                                               GATEWAY=gateway))
        else:
            command = ('$n add ip_static_hosts -id "{NAME}" '
                       '-tags [list "{NAME}" "{TAG}"] '
                       '-default_container "{CONTAINER}" -ip_address "{IP}" '
                       '-count {COUNT} -netmask {NETMASK}')
            self.tfiles.pcreate(command.format(NAME=name,
                                               TAG=tag,
                                               CONTAINER=container,
                                               IP=ip_address,
                                               COUNT=count,
                                               NETMASK=netmask))

        self._ip_static_hosts.append(name)

    def get_interface_group(self, prefix):
        return [i for i in self._interfaces if (i.startswith(prefix))]

    def get_container_group(self, prefix):
        return [i for i in self._containers if (i.startswith(prefix))]

    def get_ip_static_hosts_group(self, prefix):
        return [i for i in self._ip_static_hosts if (i.startswith(prefix))]

    def add_path(self, clientid, serverid):
        command = '$n addPath "{CLI_ID}" "{SER_ID}"'
        self.tfiles.pcreate(command.format(CLI_ID=clientid, SER_ID=serverid))
        self._paths.append({clientid, serverid})

    def path_exists(self, clientid, serverid):
        if {clientid, serverid} in self._paths:
            return True
        else:
            return False

    def save(self):
        command = ('$n commit\n'
                   '$n save -name "{NAME}" -force')
        self.tfiles.pcreate(command.format(NAME=self._name))




def main():
    pass

if __name__ == "__main__":
    main()
