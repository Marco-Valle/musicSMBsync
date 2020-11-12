from mutagen import MutagenError
from mutagen.easyid3 import EasyID3


class Song:

    def __init__(self, path):
        self.path = path
        self.name = path.split('/')[-1]
        self.ext = self.name.split('.')[-1]
        try:
            if self.ext == 'mp3':
                self.m = EasyID3(self.path)
                self.status = True
            else:
                self.status = False
        except MutagenError:
            self.status = False

    def __str__(self):
        assert self, "File {} not found".format(self.path)
        return "{} -> {}".format(self.name, self.m)

    def __bool__(self):
        return self.status

    def update_genre(self, genre, over_write=False):
        assert self, "File {} not found".format(self.path)
        stop = False
        if 'genre' in self.m:
            if over_write is False:
                stop = True
        if self.status and not stop:
            self.m['genre'] = genre
            self.m.save()
