class SuperFlow(object):
    def __init__(self, tfiles, name, app):
        self.name = name
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

class HTTPS_TLS12_RSA2K_AES256_SHA384_RESUME(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 4 -response-data-gen-exact {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class GOOGLE_BASE(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -response-data-gen-exact {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class FACEBOOK_BASE(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -response-data-gen-exact {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class SOAP(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -response-data-gen-exact {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class FTP(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 6 -download-size {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class SMBv2(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 14 -file_size {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class POP3(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -attachment_size {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class IMAP(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 2 -attachment_size {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class SMTP(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 10 -attachment-size {TSIZE}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class NFSv3(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 11 -datafile {FILENAME}')
        self.tfiles.pcreate(command.format(FILENAME=filename))

class RSYNC(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 5 -raw_message_file {FILENAME}')
        self.tfiles.pcreate(command.format(TSIZE=tsize))

class SSH(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 3 -raw_message_file {FILENAME}')
        self.tfiles.pcreate(command.format(FILENAME=filename))

class QUIC(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        command = ('$superflow modifyAction 5 -stream_data_file {FILENAME}')
        self.tfiles.pcreate(command.format(FILENAME=filename))

class HTTPS_SIM(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class GOOGLE_HTTPS(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class PAN_UPDATES(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class FACEBOOK_BASE_HTTPS(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class OUTLOOK_WEB_ONLINE_HTTPS(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class SHAREPOINT_ONLINE_HTTPS(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 7250:
            tsize = 7250
        loop = round((tsize - 5700)/1400)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server application -appdata-min 1400 -appdata-max 1400')
            self.tfiles.pcreate(command)

class NETFLOWv9(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 1500:
            tsize = 1500 
        loop = round((tsize - 94)/1309)
        for i in range(1, loop):
            command = ('$superflow addAction 1 client data_records -num_records 40')
            self.tfiles.pcreate(command)

class SYSLOG(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 1500:
            tsize = 1500
        loop = round((tsize - 94)/470)
        for i in range(1, loop):
            command = ('$superflow addAction 1 client syslog_message -content "This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message.This is a syslog message."')
            self.tfiles.pcreate(command)

class LDAP_SEARCH(SuperFlow):
    def modify(self, *, tsize=None, filename=None):
        if tsize < 3000:
            tsize = 3000 
        loop = round((tsize - 1500)/212)
        for i in range(1, loop):
            command = ('$superflow addAction 1 server search_response_resultentry -objectname "CN=Admins,OU=Access Groups,OU=Groups,OU=Test,DC=Test,DC=com" -attributes "Attribute1,Attribute2,Attribute3,Attribute4,Attribute5,Attribute6"')
            self.tfiles.pcreate(command)

class ORACLE_SELECT(SuperFlow):
    pass

class MSSQL_SELECT(SuperFlow):
    pass

class MYSQL_SELECT(SuperFlow):
    pass

class POSTGRESQL(SuperFlow):
    pass

class DB2(SuperFlow):
    pass

class LPD(SuperFlow):
    pass

class RDP(SuperFlow):
    pass

class FIX(SuperFlow):
    pass

class TELNET(SuperFlow):
    pass

class TFTP(SuperFlow):
    pass

class MSRPC(SuperFlow):
    pass

class RTSP(SuperFlow):
    pass

class SCCP(SuperFlow):
    pass

class SIP(SuperFlow):
    pass

class SNMPv1(SuperFlow):
    pass

class SNMPv2c(SuperFlow):
    pass

class SNMPv3(SuperFlow):
    pass

class SNMP_TIMEOUT(SuperFlow):
    pass

class NETBIOS(SuperFlow):
    pass

class DNS(SuperFlow):
    pass

class DNS_TIMEOUT(SuperFlow):
    pass

class NTPv4(SuperFlow):
    pass

class NTPv4_TIMEOUT(SuperFlow):
    pass

class CITRIX(SuperFlow):
    pass

