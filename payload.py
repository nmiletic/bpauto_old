from itertools import repeat
from paramiko import SSHClient
from scp import SCPClient

class PayloadFile(object):
    def __init__(self, *, prefix=None):
        self._prefix = prefix
    
    def generate_file(self, filename, size, filetype):
        if filetype == "asterisk":
            data = bytes(repeat(ord('*'), size))
        elif filetype == "binary":
            data = bytes(urandom(size))
        elif filetype == "ascii":
            random_ascii = (ord(random.choice(string.ascii_letters)) for _ in range(size))
            data = bytes(random_ascii)

        with open(filename, "wb") as datafile:
            datafile.write(data)

    def upload_file(self, filename, hostname, adminlogin, adminpassword):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname, username=adminlogin, password=adminpassword)

        # SCPCLient takes a paramiko transport as its only argument
        scp = SCPClient(ssh.get_transport())

        scp.put(filename, "/resources/" + filename)

        scp.close()

    def delete_file(self, filename, hostname, adminlogin, adminpassword):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname, username=adminlogin, password=adminpassword)

        command = "rm -f /resources/" + quote(filename)
        ssh.exec_command(command)
        ssh.close()

