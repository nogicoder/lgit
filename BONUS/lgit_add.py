import hashlib
import os
from datetime import datetime


class LgitAdd:
    def __init__(self, fname, ct='None'):
        self.ct = ct
        self.fname = fname
        if self.ct == 'None':
            self.remove(self.fname)
        else:
            self.hsh = self.turnHash(self.ct)
            self.createFile(self.hsh, self.ct)
            self.updateIndex(self.hsh, self.fname)

    def turnHash(self, content):
        hsh = hashlib.sha1(content).hexdigest()
        return hsh

    def createFile(self, hsh, ct):
        if not os.path.exists('.lgit/objects/' + hsh[:2]):
            os.mkdir('.lgit/objects/' + hsh[:2])
        fd = os.open('.lgit/objects/' + hsh[:2] + '/' + hsh[2:],
                     os.O_RDWR | os.O_CREAT)
        os.write(fd, ct)
        os.close(fd)

    def dictIndex(self):
        added_files = {}
        with open('.lgit/index', 'r') as f:
            for line in f:
                fn = line[:-1].split(' ')
                added_files[fn[-1]] = line
        return added_files

    def rIndex(self, file, added_files):
        for x in added_files:
            if file == x:
                del added_files[x]
                break
        with open('.lgit/index', 'w') as f1:
            f1.write(''.join(added_files.values()))

    def remove(self, fname):
        added_files = self.dictIndex()
        if fname in added_files:
            self.rIndex(fname, added_files)
            with open('.lgit/.deleted', 'a') as file:
                file.write('[deletedbyLGIT]' + fname + '\n')
        else:
            error = True
            index = os.open('.lgit/.deleted', os.O_RDWR)
            with open('.lgit/.deleted') as file:
                start = 0
                for line in file:
                    list_line = line[:-1].split(' ')
                    if fname in list_line:
                        error = False
                        added_fname = '[deletedbyLGIT]' + fname + '\n'
                        os.pwrite(index, str.encode(added_fname), start)
                        os.close(index)
                    start += len(line)
            if error is True:
                print("fatal: pathspec '%s' did not match any files" % fname)

    def updateIndex(self, hsh, fname):
        index = os.open('.lgit/index', os.O_RDWR)
        filetime = os.path.getmtime(fname)
        timestamp = datetime.fromtimestamp(filetime).strftime("%Y%m%d%H%M%S")
        with open('.lgit/index', 'r') as f:
            start = 0
            for line in f:
                list_line = line[:-1].split(' ')
                if fname in list_line:
                    os.lseek(index, start, 0)
                    os.write(index, str.encode('{} {} {}'.format(
                            timestamp, hsh, hsh)))
                    os.close(index)
                    return fname
                start += len(line)
        os.lseek(index, start, 0)
        os.write(index, str.encode('{} {} {} {} {}\n'.format(
                timestamp, hsh, hsh, ' '*len(hsh), fname)))
        os.close(index)
        return fname
