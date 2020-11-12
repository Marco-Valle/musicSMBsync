from smb.SMBConnection import SMBConnection
from os import remove


class Server:

    MP3_HEADER_SIZE = 25000

    def __init__(self, ip, user, password, folder, name="DEFAULT", port=139, ntlm=True):

        self.ip = ip
        self.port = port
        self.name = name
        self.user = user
        self.folder = folder
        self.conn = SMBConnection(self.user, password, self.ip, self.name, use_ntlm_v2=ntlm)
        self.status = self.conn.connect(self.ip, self.port)

    def __str__(self):
        return "SMB server {} at {}, logged by user {}".format(self.name, self.ip, self.user)

    def __bool__(self):
        return self.status

    def get_folder(self, dir):
        return self.conn.listPath(self.folder, dir)

    def get_file(self, path, local_file):
        self.conn.retrieveFile('smb', path, local_file)

    def update_header(self, path, local_file):
        with open(local_file, 'rb') as file:
            buf = file.read()
        buf = buf[:Server.MP3_HEADER_SIZE]
        # Write the HEADER to tmp file
        with open('tmp', 'wb') as tmp:
            tmp.write(buf)
        # Write the HEADER to server file
        with open('tmp', 'rb') as tmp:
            bytes_written = self.conn.storeFileFromOffset('smb', path, tmp, offset=0, truncate=False)
        remove('tmp')
        if bytes_written == Server.MP3_HEADER_SIZE:
            return True
        else:
            return False
