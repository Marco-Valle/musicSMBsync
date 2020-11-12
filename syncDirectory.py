from hashlib import sha256
from os import path as ospath
from os import makedirs, scandir, remove
from tqdm import tqdm
from shutil import copy2, rmtree
from songs_manager import Song
import tempfile


class Synchronizer:

    BLOCK_SIZE = 65536                                          # The size of each read from the file for hashing
    TMP_FOLDER = tempfile.gettempdir().replace('\\', '/')       # The tmp folder where software can download things
    TMP_FOLDER += "/musicSMBsync"

    def __init__(self, server, local_folder, server_folder):

        self.server = server
        self.local_dir = local_folder                               # Local folder to sync
        self.server_dir = self.server.get_folder(server_folder)     # Main server folder
        self.server_dir_name = server_folder                        # Its name
        self.folders_name = []                                      # List of all folders filename
        self.current_dir = False                                    # The open folder use open_dir()
        self.current_dir_path = False                               # Its path
        self.current_dir_name = False                               # Its name
        self.files = []                                             # Files of current opened folder
        self.hashes = []                                            # Hashes of the files in directory
        self.exist_locally = False                                  # If current folder exist in local path
        self.missing_files = []                                     # The files that are different between server and client

        self.get_folders_name()
        Synchronizer.check_tmp_folder()

    def __str__(self):
        string = "Synchronizer: SMB server {}, local folder: {}, remote folder: {}".format(
            self.server.ip, self.local_dir, self.server_dir_name)
        string += "\nOpen folder: {}".format(self.current_dir_path)
        for f in self.files:
            string += "\n{}".format(f)
        return string

    def get_folders_name(self):
        self.folders_name = []
        for d in self.server_dir:
            name = d.filename
            is_folder = d.isDirectory
            if name != '..' and name != '.' and is_folder:
                self.folders_name.append(name)
                self.open_dir(name, add_folder_to_list=True)
        for name in self.folders_name:
            if name != '..' and name != '.':
                self.open_dir(name, add_folder_to_list=True)
        return self.folders_name

    def open_dir(self, folder_name, add_folder_to_list=False):
        self.files = []
        self.current_dir_name = folder_name
        self.current_dir_path = '{}{}'.format(self.server_dir_name, folder_name)
        self.current_dir = self.server.get_folder(self.current_dir_path)
        parent_folders = []
        for f in self.current_dir:
            name = f.filename
            is_folder = f.isDirectory
            if name != '..' and name != '.':
                if is_folder and add_folder_to_list:
                    self.folders_name.append("{}/{}".format(folder_name, name))
                    parent_folders.append(folder_name)
                else:
                    self.files.append(name)
        # Remove duplicates from parent folders list
        parent_folders = list(dict.fromkeys(parent_folders))
        # If there is a parent folder remove it
        for f in parent_folders:
            self.folders_name.remove(f)
        self.exist_locally = ospath.isdir('{}{}'.format(self.local_dir, folder_name))

    def download_dir(self, work_on_tmp=False):
        if self.local_dir[-1] != '/':
            self.local_dir += '/'
        if self.current_dir is not False:
            if work_on_tmp:
                parent_path = '{}/'.format(Synchronizer.TMP_FOLDER)
            else:
                parent_path = self.local_dir
            parent_path += '{}/'.format(self.current_dir_name)
            if ospath.isdir(parent_path) is False:
                makedirs(parent_path, exist_ok=True)
            for file in tqdm(self.files):
                path = '{}/{}'.format(self.current_dir_path, file)  # Remote path
                with open('{}{}'.format(parent_path, file), 'wb') as f:
                    self.server.get_file(path, f)

    def update_genres(self, work_on_tmp=False):
        print("Update genres of {} songs".format(len(self.files)))
        for file in tqdm(self.files):
            if work_on_tmp:
                path = '{}/{}/{}'.format(Synchronizer.TMP_FOLDER, self.current_dir_name, file)
            else:
                path = '{}/{}/{}'.format(self.local_dir, self.current_dir_name, file)
            genre = self.current_dir_name
            song = Song(path)
            if song.status:
                song.update_genre(genre)

    def sync_genres(self, work_on_tmp=False):
        print("Sync genres of {} songs with server".format(len(self.files)))
        for file in tqdm(self.files):
            if work_on_tmp:
                local_path = '{}/{}/{}'.format(Synchronizer.TMP_FOLDER, self.current_dir_name, file)
            else:
                local_path = '{}/{}/{}'.format(self.local_dir, self.current_dir_name, file)
            remote_path = '{}/{}'.format(self.current_dir_path, file)
            if self.server.update_header(remote_path, local_path) is False:
                print("Error occurred synchronizing file {}".format(file))

    def compute_hashes(self, work_on_tmp=False, is_check=False):
        if is_check:
            hashes = []
        else:
            self.hashes = []
        if is_check or work_on_tmp is False:
            parent_path = self.local_dir
        else:
            parent_path = '{}/'.format(Synchronizer.TMP_FOLDER)
        parent_path += '{}/'.format(self.current_dir_name)
        for file in self.files:
            file_hash = sha256()
            try:
                with open('{}{}'.format(parent_path, file), 'rb') as f:
                    # Compute hash
                    fb = f.read(Synchronizer.BLOCK_SIZE)
                    while len(fb) > 0:
                        file_hash.update(fb)
                        fb = f.read(Synchronizer.BLOCK_SIZE)
                if is_check:
                    hashes.append(file_hash.hexdigest())
                else:
                    self.hashes.append(file_hash.hexdigest())
            except FileNotFoundError:
                if is_check:
                    hashes.append(None)
        if is_check:
            return hashes

    def check_hashes(self):
        assert len(self.hashes) != 0, "Call compute_hashes() before"
        self.missing_files = []
        hashes = self.compute_hashes(is_check=True)
        idx = 0
        while idx < len(self.hashes):
            if hashes[idx] != self.hashes[idx]:
                self.missing_files.append(self.files[idx])
            idx += 1

    def copy_missing(self):
        if len(self.missing_files) == 0:
            return True
        else:
            parent_path = '{}/'.format(Synchronizer.TMP_FOLDER)
            parent_path += '{}/'.format(self.current_dir_name)
            local_dir = self.local_dir + '{}/'.format(self.current_dir_name)
            for file in self.missing_files:
                copy2('{}/{}'.format(parent_path, file), '{}{}'.format(local_dir, file))
            self.missing_files = []
            return True

    def check_existence(self, delete=True):
        # Check if there are some files locally that are not stored in server folder
        # and if it is necessary delete them
        missing_file = []
        folder = '{}/{}'.format(self.local_dir, self.current_dir_name)
        for file in scandir(folder):
            if file.is_file():
                if (file.path.split('\\')[-1] in self.files) is False:
                    if delete:
                        remove(file)
                        print("File {} removed because it wasn't on server".format(file.path))
                    missing_file.append(file)
        return missing_file

    @staticmethod
    def clean_temp():
        if ospath.isdir(Synchronizer.TMP_FOLDER):
            # Clear it
            rmtree(Synchronizer.TMP_FOLDER)

    @staticmethod
    def check_tmp_folder():
        # Clear temp folder
        Synchronizer.clean_temp()
        # Create it
        makedirs(Synchronizer.TMP_FOLDER, exist_ok=True)
        print("Tmp folder created: {}".format(Synchronizer.TMP_FOLDER))
