from server import Server
import keyring


class Auth:

    def __init__(self, ip, user, folder, password=False, service_name=False,
                 store_credential=False, name="DEFAULT", port=139, ntlm=True):

        self.name = name
        self.ip = ip
        self.user = user
        self.service_name = service_name

        # If service_name is false try use the default one
        if self.service_name is False:
            self.get_service_name()

        # If required get password from Windows Credential Manager
        if password is False:
            password = Auth.get_password(self.service_name, self.user)
            assert password, "No password stored for service {} and user {}".format(self.service_name, self.user)
        else:
            if store_credential and self.service_name:
                Auth.store_password(self.service_name, self.user, password)

        self.server = Server(self.ip, self.user, password, folder, name=self.name, port=port, ntlm=ntlm)

    def __str__(self):
        return "Authenticator: SMB server {} at {}, logged by user {}".format(self.name, self.ip, self.user)

    def __bool__(self):
        return self.server.status

    def get_connection(self):
        return self.server

    def get_service_name(self):
        self.service_name = "musicSMBsync"

    @staticmethod
    def get_password(service, user):
        password = keyring.get_password(service, user)
        if password is None:
            return False
        else:
            return password

    @staticmethod
    def store_password(service, user, password):
        keyring.set_password(service, user, password)
