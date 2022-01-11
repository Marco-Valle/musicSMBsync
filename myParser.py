import argparse


class Parser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="SMB sync")
        self.add_arguments()

    def __call__(self, *args, **kwargs):
        args = self.parser.parse_args()
        if args.port is not None and args.port < 1:
            self.parser.error('The port must be a positive integer')
        if args.white_list is not None and args.black_list is not None:
            self.parser.error("Can't use both white and black list")
        return args

    def add_arguments(self):
        self.parser.add_argument('host', type=str, help='The hostname of the server')
        self.parser.add_argument('user', type=str, help='The server username')
        self.parser.add_argument('folder', type=str, help='The main SMB folder')
        self.parser.add_argument('--port', type=int, nargs='?', help='The server port (default 139)')
        self.parser.add_argument('--password', type=str, nargs='?', help='The server password')
        self.parser.add_argument('--local_folder', type=str, nargs='?', help='The local folder')
        self.parser.add_argument('--music_folder', type=str, nargs='?', help='The name of the remote folder where the music is located')
        self.parser.add_argument('--group', type=str, nargs='?', help='The name of the samba group')
        self.parser.add_argument('--service_name', type=str, nargs='?', help='The service name in windows credential manager (default: musicSMBsync)')
        self.parser.add_argument('--store_password', action='store_true', help='Store the password in the keyring')
        self.parser.add_argument('--verbose', action='store_true', help='Verbosity')
        self.parser.add_argument('--remove', action='store_true', help="Remove the folder which aren't on the server")
        self.parser.add_argument('--white_list', type=str, nargs='+', help='The files in white_list (__ to add space)')
        self.parser.add_argument('--black_list', type=str, nargs='+', help='The files in black list (__ to add space)')
