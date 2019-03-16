from lgit_branch import LgitBranch
from datetime import datetime
from rsync import sync_file
import hashlib
import os


class LgitStash:
    def __init__(self, apply=False):
        self.branch = self.find_branch()
        self.checked_dict = self.checkFiles()
        if apply is False:
            self.save_to_stash(self.checked_dict)
            LgitBranch('checkout', self.branch, True)
        if apply is True:
            self.apply_stash()

    def turnHash(self, content):
        hsh = hashlib.sha1(content).hexdigest()
        return hsh

    def updateContent(self, file):
        fd = os.open(file, os.O_RDONLY)
        current = os.read(fd, os.stat(fd).st_size)
        hsh = self.turnHash(current)
        return hsh

    def all_file_list(self, dir):
        file_list = []
        for root, dir, file in os.walk(dir):
            for x in file:
                result = []
                if 'git' not in root:
                    result.append(root[2:])
                    result.append(x)
                    file_list.append(os.path.join(result[0], result[1]))
        return file_list

    def checkFiles(self):
        checked_dict = {'ready': [], 'notstaged': []}
        dirs = self.all_file_list('.')
        with open('.lgit/index', 'r') as f:
            start = 0
            for line in f:
                list_line = line[:-1].split(' ')
                if (len(list_line) != 5 or (len(list_line) == 5
                   and list_line[2] != list_line[3])):
                    checked_dict['ready'].append(list_line[-1])
                hash = self.updateContent(list_line[-1])
                if hash != list_line[2]:
                    checked_dict['notstaged'].append(list_line[-1])
                start += len(line)
        return checked_dict

    def save_to_stash(self, checked_dict):
        list = []
        for key in checked_dict:
            for item in checked_dict[key]:
                list.append(item)
        for filename in list:
            source = os.path.abspath(filename)
            dest = os.path.abspath('.lgit/stash/' + filename)
            sync_file(source, dest)

    def update_index(self, fname, hsh):
        index = os.open('.lgit/index', os.O_RDWR)
        filetime = os.path.getmtime(fname)
        timestamp = datetime.fromtimestamp(filetime).strftime("%Y%m%d%H%M%S")
        with open('.lgit/index', 'r') as f:
            start = 0
            for line in f:
                list_line = line[:-1].split(' ')
                if fname in list_line:
                    os.lseek(index, start, 0)
                    os.write(index, str.encode('{} {} {} {}'.format(
                            timestamp, hsh, hsh, hsh)))
                    os.close(index)
                    return fname
                start += len(line)
        os.lseek(index, start, 0)
        os.write(index, str.encode('{} {} {} {} {}\n'.format(
                timestamp, hsh, hsh, hsh, fname)))
        os.close(index)
        return fname

    def find_branch(self):
        with open('.lgit/HEAD', 'r') as f:
            content = f.read()
        head = content.strip().split('/')[-1]
        return head

    def apply_stash(self):
        list = os.listdir('.lgit/stash')
        for filename in list:
            dest = os.path.abspath(os.getcwd()) + '/' + filename
            source = os.path.abspath('.lgit/stash/' + filename)
            sync_file(source, dest)
            with open(source) as file:
                content = file.read()
                self.update_index(filename, self.turnHash(str.encode(content)))
