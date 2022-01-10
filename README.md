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
Third it checks if remote folders are present in local resource, if it not, it will download them. If they are all present it will start to download folder per folder in Temp directory.
Fourth script tries to update GENRE mp3 tag of all file where is possible, according to parent folder name.
Fifth it uploads to server a fixed amount of bytes (25000 for default) to synchronize genres. This is much faster then uploading entire file.
Sixth it checks the hashes (sha256) between local resources and server's ones, if there are some modification in a folder, script downloads it from server and copies it from temp directory (or on whatever it was working on) to local resource.
And at the end it cleans all environment.

If you find a tmp file in script folder, is because software uses it to fix the amount of data to store on server and then it deletes it, it's safe to remove.
You can use white and black lists (not both together) to select which folder synchronize.

## Authors

* **Marco Valle** - [Marco-Valle](https://github.com/Marco-Valle)

## License

This project is licensed under the GPL v3 License - see the [LICENSE](LICENSE) file for details
