from server import Server
from platform import system
import keyring


class Auth:

    def __init__(self, ip, user, folder, password=None, service_name="musicSMBsync",
                 store_credential=False, name="DEFAULT", port=139, ntlm=True):

        self.name = name
        self.ip = ip
        self.user = user

        # If required get password from Windows Credential Manager
        if not password or password is None:
            password = Auth.get_password(service_name, self.user)
            assert password, "No password stored for service {} and user {}".format(service_name, self.user)
        else:
            if store_credential and service_name:
                Auth.store_password(service_name, self.user, password)

        self.server = Server(self.ip, self.user, password, folder, name=self.name, port=port, ntlm=ntlm)

    def __str__(self):
        return "Authenticator: SMB server {} at {}, logged by user {}".format(self.name, self.ip, self.user)

    def __bool__(self):
        return self.server.status

    def __call__(self, *args, **kwargs):
        return self.server

    def get_connection(self):
        return self.server

    @staticmethod
    def is_windows():
        return system() == 'Windows'

    @staticmethod
    def get_password(service, user):
        if not Auth.is_windows():
            return False
        password = keyring.get_password(service, user)
        if password is None:
            return False
        else:
            return password

    @staticmethod
    def store_password(service, user, password):
        if Auth.is_windows():
            keyring.set_password(service, user, password)
