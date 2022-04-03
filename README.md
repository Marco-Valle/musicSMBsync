# musicSMBsync
I've written this Python3 software, because I needed to synchronize a folder on samba server with one on a local resource.
This is  not the most powerful solutions, but it works sufficently great.

### Prerequisites

1) Python 3
2) Pip3 (see requirequirements.txt)

### Installing

```
pip3 install -r requirements.txt 
```

### Usage
```
python3 sync.py --help

Examples:
python3 sync.py 127.0.0.1 user smb --password my_pass --store_passord --local_folder D://Music --white-list My__Test__Folder
python3 sync.py 127.0.0.1 user smb --verbose --music_folder Music --black-list My__Test__Folder
```

## How it works

This script is able to authenticate on samba server, with a given credentials or the ones in the keyring (eg. Windows Credential Manager); then it checks for all the files and the subfolders in the directory smb-folder/Music-folder/ and compares them with the folders in the white or in the black list.
Then it determinates the Genre of the mp3 file using the folders' structure (this is not the best, but it is a simple way to label the music) and it uses hashes to check if there are some modifications between the files, if there are, it copies the files to the local resourse (eg. USB drive).
Eventually it cleans everything.
You can use white or black list (not both together) to select which folder you want to synchronize (remember that if you want to include House/Deep you have to write both --white_list House House/Deep).

## Authors

* **Marco Valle** - [Marco-Valle](https://github.com/Marco-Valle)

## License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details
