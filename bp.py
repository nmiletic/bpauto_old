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
        self._test = None
        self._superflows = []

    def connect(self, *, hostname=None, login='admin', password='admin'):
        command = ('set bps [bps::connect "{HOSTNAME}" "{LOGIN}" "{PASSWORD}" '
                   '-onclose exit -shortcuts true]')
        self.tfiles.pcreate(command.format(HOSTNAME=hostname, LOGIN=login, PASSWORD=password))

    def save(self):
        self.tfiles.save_create(self._prefix)

    def create_network(self, name='NN'):
        command = ('set n [$bps createNetwork -name "{NAME}"]')
        self.tfiles.pcreate(command.format(NAME=name))
        self._network = Network(self.tfiles, name)
        command = ('$n begin')
        self.tfiles.pcreate(command)
        return self._network

    def create_test(self, name):
        command = ('set test [$bps createTest -name "{NAME}"]')
        self.tfiles.pcreate(command.format(NAME=name))
        self._test = Test(self.tfiles, self._prefix + name)
        return self._test

    def create_superflow(self, name, app):
        command = ('set superflow [$bps createSuperflow -template {TMPL} -name "{NAME}"]')
        self.tfiles.pcreate(command.format(NAME=name, TMPL='TMPL_' + app))
#        sf = Superflow(self.tfiles, self._prefix + name, app)
        sf = globals()[app](self.tfiles, self._prefix + name, app)
        self._superflows.append(sf)
        return sf
    
    def create_app_profile(self, name):
        command = ('set appprofile [$bps createAppProfile -name "{NAME}"]')
        self.tfiles.pcreate(command.format(NAME=name))
        ap = AppProfile(self.tfiles, name)
        return ap


class Test(object):
    def __init__(self, tfiles, name):
        self._name = name
        self.tfiles = tfiles
        self._components = []

    def configure(self, option, value):
        command = ('$test configure {OPTION} {VALUE}')
        self.tfiles.pcreate(command.format(OPTION=option, VALUE=value))

    def create_component(self, comp_type, name):
        command = ('set comp [$test createComponent {COMP_TYPE} "{NAME}" 1 2]')
        self.tfiles.pcreate(command.format(COMP_TYPE=comp_type, NAME=name))
        comp = Component(self.tfiles, name)
        self._components.append(comp)
        return comp

    def save(self):
        command = ('$test save -force')
        self.tfiles.pcreate(command)

class Component(object):
    def __init__(self, tfiles, name):
        self._name = name
        self.tfiles = tfiles

    def configure(self, option, value):
        command = ('$comp configure {OPTION} {VALUE}')
        self.tfiles.pcreate(command.format(OPTION=option, VALUE=value))


class SuperFlow(object):
    def __init__(self, tfiles, name, app):
        self._name = name
        self._app = app
        self.tfiles = tfiles

    def modify(self, *, tsize=None, filename=None):
        pass

    def save(self):
        command = ('$superflow save -force')
        self.tfiles.pcreate(command)


class HTTP(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -response-data-gen-exact {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class NFSv3(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 11 -datafile {FILENAME}')
        self.tfiles.pcreate(command.format(FILENAME=filename))

class ORACLE_SELECT(SuperFlow):
    pass

class HTTPS_SIM(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)


class AppProfile(object):
    def __init__(self, tfiles, name):
        self._name = name
        self.tfiles = tfiles
    def configure(self, weight_type):
        command = ('$appprofile configure -weightType {WEIGHT_TYPE}')
        self.tfiles.pcreate(command.format(WEIGHT_TYPE=weight_type))
    def add_superflow(self, name, weight):
        command = ('$appprofile addSuperflow "{NAME}" {WEIGHT}')
        self.tfiles.pcreate(command.format(NAME=name, WEIGHT=weight))
    def save(self):
        command = ('$appprofile save -force')
        self.tfiles.pcreate(command)


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
    bps = BreakingPoint(prefix='ASD')
    bps.connect(hostname='1.1.1.1', login='admin', password='admin')
    sf = bps.create_superflow('HTTP', 'HTTP')
    sf.modify(tsize=12123)
    sf.save()
    ap = bps.create_app_profile('AP')
    ap.configure('bandwidth')
    ap.add_superflow('HTTP', 100) 
    ap.save()
    bps.save()
    pass

if __name__ == "__main__":
    main()
