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

