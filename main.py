from secureAuth import Auth
from syncDirectory import Synchronizer
from shutil import rmtree


def print_genders(genders):
    for gender in genders:
        if genders.index(gender) != len(genders)-1:
            print(gender, end=', ')
        else:
            print(gender, end='\n')


def remove_folder(name):
    rmtree('{}/{}'.format(Synchronizer.TMP_FOLDER, name))


if __name__ == '__main__':

    # To authenticate user and store password in Windows Credential Manager use:
    # authenticator = Auth('192.168.1.1', 'user', 'smb_folder', password='pass' name='DEFAULT', service_name='musicSMBsync', store_credential=True)
    # Instead if you have already store it you can use:
    authenticator = Auth('192.168.1.1', 'user', 'smb', name='DEFAULT')
    musicFolder = "/MEDIA/Music/"
    localFolder = "D://Music/"
    # Folders to ignore
    blackList = []
    # Folders to consider
    whiteList = []
    # Use only one between white or black list
    # if none is used then every folder will be in white list

    server = authenticator.server
    synchronizer = Synchronizer(server, localFolder, musicFolder)

    if server is False:
        print("Connection failed check for username and password")
        exit(0)
    else:
        print(server)

    # Navigate to music folder
    print("cd {}".format(musicFolder))
    genres = synchronizer.get_folders_name()

    # Print genders
    print_genders(genres)

    # Open each folder and exists locally
    for folder in genres:
        try:
            condition = ((folder not in blackList) and (len(whiteList) == 0)) or ((folder in whiteList) and (len(blackList) == 0))
            condition = condition or (len(whiteList) == 0 and len(blackList) == 0)
            if condition:
                synchronizer.open_dir(folder)
                if synchronizer.exist_locally:
                    print("\nDownload from server folder {} for comparison".format(folder))
                    synchronizer.download_dir(work_on_tmp=True)
                    print("Total files number: {}".format(len(synchronizer.files)))
                    # Update genres according folders name
                    synchronizer.update_genres(work_on_tmp=True)
                    # Sync genres to server
                    synchronizer.sync_genres(work_on_tmp=True)
                    # Compute hashes of files
                    synchronizer.compute_hashes(work_on_tmp=True)
                    # Check if server hashes and local hashes are the same
                    # if not notify the missing or with modification files
                    synchronizer.check_hashes()
                    # Copy the missing or with modification files to local resource
                    synchronizer.copy_missing()
                    # Check for files that aren't on server
                    synchronizer.check_existence()
                    # Remove folder
                    remove_folder(folder)
                else:
                    print("\nDownload from server folder {}".format(folder))
                    synchronizer.download_dir()
                    # Update genres according folders name
                    synchronizer.update_genres()
                    # Sync genres to server
                    synchronizer.sync_genres()

        except KeyboardInterrupt:
            print("KeyboardInterrupt - Stop")
            break

    # Clear temp folder
    Synchronizer.clean_temp()
