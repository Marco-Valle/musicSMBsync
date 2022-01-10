from hashlib import sha256
from os.path import isdir, isfile
from os import makedirs, walk, remove
from shutil import copy2, rmtree
from tqdm import tqdm
from songs_manager import Song
import tempfile


class Synchronizer:

    BLOCK_SIZE = 65536                                          # The size of each read from the file for hashing
    TMP_FOLDER = tempfile.gettempdir().replace('\\', '/')       # The tmp folder where software can download things
    TMP_FOLDER += "/musicSMBsync/"

    def __init__(self, server, local_folder, server_folder, white_list, black_list, verbosity=False, remove_not_present=False):

        self.server = server
        self.local_dir = local_folder                               # Local folder to sync
        self.server_dir = server.get_folder(server_folder)          # Main server folder
        self.server_dir_name = server_folder                        # Its name
        self.verbosity = verbosity
        self.remove = remove_not_present

        self.white_list = white_list
        self.black_list = black_list
        self.folders_name = []                                      # List of all folders filename
        self.files = []                                             # All the files

        self.recursive_search('', [])

        if self.local_dir[-1] != '/':
            self.local_dir += '/'

    def __str__(self):
        string = "Synchronizer: SMB server {}, local folder: {}, remote folder: {}".format(
            self.server.ip, self.local_dir, self.server_dir_name)
        return string

    def __call__(self, *args, **kwargs):
        try:
            Synchronizer.check_tmp_folder()
            self.create_folders_structure()
            self.handle_files()
            self.local_clean()
        except KeyboardInterrupt:
            print("KeyboardInterrupt - Stop")
            return

    def get_folders_name(self):
        return self.folders_name

    def get_server_path(self, relative_path):
        return "{}{}".format(self.server_dir_name, relative_path)

    def get_local_path(self, relative_path):
        return "{}{}".format(self.local_dir, relative_path)

    def check_folder(self, folder):
        folder = folder.strip('/').replace(self.local_dir, '').replace(' ', '__')
        if len(self.white_list) == len(self.black_list) == 0:
            return 1
        if len(self.white_list) == 0 and folder not in self.black_list:
            return 1
        return folder in self.white_list

    def recursive_search(self, folder_name, parents):
        if not Synchronizer.is_child_path(folder_name):
            return
        tmp_parents = parents[:-1]
        directory = self.server.get_folder(self.get_server_path("{}/{}".format('/'.join(tmp_parents), folder_name)))
        for item in directory:
            if not Synchronizer.is_child_path(item.filename):
                continue
            new_path = "{}/{}".format('/'.join(parents), item.filename).replace('//', '/')
            if item.isDirectory:
                if not self.check_folder(new_path):
                    continue
                local_path = "{}{}".format(self.local_dir, new_path[1:])
                new_folder = Synchronizer.get_my_dict(new_path, isdir(local_path))
                self.folders_name.append(new_folder)
                parents.append(item.filename)
                self.recursive_search(item.filename, parents)
                parents.pop()
            else:
                new_file = Synchronizer.get_my_dict(new_path.strip('/'), isfile(self.get_local_path(new_path)))
                self.files.append(new_file)

    def create_folders_structure(self):
        tmp_parent_path = '{}/'.format(Synchronizer.TMP_FOLDER)
        for folder in self.folders_name:
            folder_name, exists = folder.values()
            makedirs("{}/{}".format(tmp_parent_path, folder_name), exist_ok=True)
            makedirs("{}{}".format(self.local_dir, folder_name), exist_ok=True)

    def handle_files(self):
        self.log("Start sync")
        for file in tqdm(self.files, disable=self.verbosity):
            filename, exists = file.values()
            tmp_path = '{}{}'.format(Synchronizer.TMP_FOLDER, filename)
            local_path = '{}{}'.format(self.local_dir, filename)
            if exists:
                path = tmp_path
            else:
                path = local_path
            # Download the file
            self.log("Download {}".format(filename))
            with open(path, 'wb') as fp:
                self.server.get_file(self.get_server_path(filename), fp)
            # Update the genre
            song = Song(path)
            if not song.status:
                continue
            genre = Synchronizer.get_genre_from_path(filename)
            self.log("Update the genre of {} to {}".format(filename, genre))
            song.update_genre(genre)
            # Sync the genre with the server
            if not self.server.update_header(self.get_server_path(filename), path):
                print("Error occurred synchronizing file {}".format(filename))
            if not exists:
                continue
            # Compare the existing file with the now one
            tmp_hash = Synchronizer.hash_from_file(tmp_path)
            local_hash = Synchronizer.hash_from_file(local_path)
            if tmp_hash != local_hash:
                self.log("Server file is changed ({})".format(local_path))
                copy2(tmp_path, local_path)
            remove(tmp_path)
        self.log("End sync")

    def local_clean(self):
        self.log("Start cleaning")
        my_files = [file['name'] for file in self.files]
        for root, dirs, files in walk(self.local_dir, topdown=False):
            root = root.replace('\\', '/')
            if not self.check_folder(root):
                continue
            for file in files:
                path = '{}/{}'.format(root, file)
                short_path = path.replace(self.local_dir, '')
                if short_path in my_files:
                    continue
                if self.remove:
                    remove(path)
                    self.log("File {} removed because it wasn't on server".format(path))

    def log(self, string, flush=False):
        if self.verbosity:
            print(string, flush=flush)

    @staticmethod
    def hash_from_file(path):
        file_hash = sha256()
        try:
            with open(path, 'rb') as fp:
                fb = fp.read(Synchronizer.BLOCK_SIZE)
                while len(fb) > 0:
                    file_hash.update(fb)
                    fb = fp.read(Synchronizer.BLOCK_SIZE)
        except FileNotFoundError:
            print("Can't find the file {} during sync".format(path))
            return None
        return file_hash.hexdigest()

    @staticmethod
    def get_genre_from_path(path):
        return path.replace('/{}'.format(path.split('/')[-1]), '')

    @staticmethod
    def get_hash_dict(path, hex_hash):
        new_hash = {
            'name': path,
            'hash': hex_hash
        }
        return new_hash

    @staticmethod
    def get_my_dict(name, exists_locally):
        folder = {
            'name': name,
            'exists': exists_locally
        }
        return folder

    @staticmethod
    def clean_temp():
        if isdir(Synchronizer.TMP_FOLDER):
            # Clear it
            rmtree(Synchronizer.TMP_FOLDER)

    @staticmethod
    def check_tmp_folder():
        # Clear temp folder
        Synchronizer.clean_temp()
        # Create it
        makedirs(Synchronizer.TMP_FOLDER, exist_ok=True)
        print("Tmp folder created: {}".format(Synchronizer.TMP_FOLDER))

    @staticmethod
    def is_child_path(path):
        return not(path.startswith('..') or path.startswith('.'))
