from shutil import rmtree
from secureAuth import Auth
from syncDirectory import Synchronizer
from myParser import Parser

DEFAULT_music_folder = "/MEDIA/Music/"
DEFAULT_local_folder = "D://Music/"
DEFAULT_GROUPNAME = "DEFAULT"
DEFAULT_FOLDER = "smb"
DEFAULT_SERVICE_NAME = "musicSMBsync"
DEFAULT_PORT = 139


def print_genders(genders):
    for gender in genders:
        print(gender)


def show_server(server):
    if server is False:
        print("Connection failed check for username and password")
        exit(0)
    else:
        print(server)


def remove_folder(name):
    rmtree('{}/{}'.format(Synchronizer.TMP_FOLDER, name))


def main():

    parser = Parser()
    args = parser()

    if args.port is None:
        port = DEFAULT_PORT
    else:
        port = args.port
    if args.local_folder is None:
        local_folder = DEFAULT_local_folder
    else:
        local_folder = args.local_folder
    if args.music_folder is None:
        music_folder = DEFAULT_music_folder
    else:
        music_folder = args.music_folder
    if args.group is None:
        group = DEFAULT_GROUPNAME
    else:
        group = args.group
    if args.service_name is None:
        service_name = DEFAULT_SERVICE_NAME
    else:
        service_name = args.service_name
    if args.white_list is None:
        white_list = []
    else:
        white_list = args.white_list
    if args.black_list is None:
        black_list = []
    else:
        black_list = args.black_list

    authenticator = Auth(args.host, args.user, args.folder,
                         name=group,
                         password=args.password,
                         store_credential=args.store_password,
                         service_name=service_name,
                         port=port,
                         )

    server = authenticator()
    show_server(server)
    synchronizer = Synchronizer(server, local_folder, music_folder, white_list, black_list,
                                verbosity=args.verbose, remove_not_present=args.remove)

    # Navigate to music folder
    if args.verbose:
        print("cd {}".format(music_folder))
        genres = synchronizer.get_folders_name()
        print_genders([genre['name'] for genre in genres])
    synchronizer()

    # Clear temp folder
    Synchronizer.clean_temp()


if __name__ == '__main__':
    main()
    exit(0)
