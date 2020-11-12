# musicSMBsync
I've written this Python3 software, because I needed to synchronize a folder on samba server with one on a local resource. This is  not the most powerful and fast tool you can find, but it's really useful for my situation maybe also for yours. 

### Prerequisites

1) Python 3
2) Pip3 (see requirequirements.txt)

### Installing

You can compile by yourself for the standalone usage or you can simply install requirements and execute it as normal python script.
```
pip3 install -r requirements.txt 
```

## How it works

The software first authenticate user to server (using password provide, or using password stored in Windows Credential Manager).
Second it gets the list of all the folders in main remote resource and use it to determinate the music genres.
Important: if you have a subfolders structure, it saves only the final folder with music files, not the parent ones. For istance if you have something like Album/Pippo and Album/Topolino, the Album folder and all the songs inside it will be ignored and only files inside Album/Pippo and Album/Topolino will be considered.
Third it checks if remote folders are present in local resurce, if it not, it will download them. If they are all present it will start to download folder per folder in Temp directory.
Fourth script tries to update GENRE mp3 tag of all file where is possible, according to parent folder name; for istance if we have a song inside Album/Pippo, this song will have Album/Pippo as its genre tag. This is not the best way to label music, but it may be useful when you share music file over Daap server (like me) or with other OTA method.
Fift it upload to server a fixed ammount of bytes (25000 for default) to syncronize genres. This is much more fast then uploading entire file and it works greatly.
Sixth it check the hashes (sha256) between local resources and server's ones, if there are some modification in a folder, script downloads it from server and copies it from temp directory (or on whatever it was working on) to local resource.
Seventh software checks if there are some files on local resource that aren't on server and delete it (it's useful if you move a file from server folder to other, because without this feature you will have a double file.
And at the end it cleans all enviroment.

If you find a tmp file in script folder, is because software uses it to fix the amount of data to store on server and then it delete it, it's safe to remove.
You can use white and black lists (not both toghether) to select which folder synchronize.
Actually I haven't already create a simple UI, so you may modify a little bit the script in order to solve some of your needs. 

## Authors

* **Marco Valle** - [Marco-Valle](https://github.com/Marco-Valle)

## License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details
