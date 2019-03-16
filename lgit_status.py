import os
import hashlib
from datetime import datetime


class LgitStatus:
    def __init__(self):
        self.check_deleted_file()
        self.checked_dict = self.checkFiles()
        self.print_it()
        self.ready(self.checked_dict['ready'], self.checked_dict['notstaged'],
                   self.checked_dict['deleted'])
        self.notStaged(self.checked_dict['notstaged'],
                       self.checked_dict['deleted'])
        self.unTracked(self.checked_dict['untracked'])

    def print_it(self):
        print('On branch master')
        if not self.checked_dict['commited']:
            print('\nNo commits yet\n')
        temp_dict = self.checked_dict.copy()
        del temp_dict['commited']
        temp_list = [value for key, value in temp_dict.items() if value != []]
        if not temp_list:
            print('nothing to commit, working directory clean')

    def turnHash(self, content):
        hsh = hashlib.sha1(content).hexdigest()
        return hsh

    def updateIndex(self, new_hash, pos, fname):
        index = os.open('.lgit/index', os.O_RDWR)
        mtime = os.path.getmtime(fname)
        timestamp = datetime.fromtimestamp(mtime).strftime("%Y%m%d%H%M%S")
        return os.pwrite(index,
                         str.encode('{} {}'.format(timestamp, new_hash)), pos)

    def updateContent(self, file):
        fd = os.open(file, os.O_RDONLY)
        current = os.read(fd, os.stat(fd).st_size)
        hsh = self.turnHash(current)
        return hsh

    def check_deleted_file(self):
        index = os.open('.lgit/.deleted', os.O_RDWR)
        with open('.lgit/index') as file:
            for line in file:
                line = line[:-1].split(' ')
                if not os.path.exists(line[-1]):
                    with open('.lgit/.deleted') as f:
                        start = 0
                        flag = False
                        for deleted in f:
                            delete = deleted.strip().split(' ')
                            added = '[deletedbyLGIT]' + line[-1]
                            if added in delete or line[-1] in delete:
                                flag = True
                            start += len(deleted)
                        if flag is False:
                            del_name = line[-1] + '\n'
                            os.pwrite(index, str.encode(del_name), start)

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
        checked_dict = {'ready': [], 'notstaged': [],
                        'untracked': [], 'commited': [], 'deleted': []}
        dirs = self.all_file_list('.')
        with open('.lgit/.deleted') as file:
            for line in file:
                if '[deletedbyLGIT]' in line:
                    checked_dict['ready'].append(line[15:-1])
                    checked_dict['deleted'].append(line[15:-1])
                else:
                    checked_dict['notstaged'].append(line[:-1])
                    checked_dict['deleted'].append(line[:-1])
        with open('.lgit/index', 'r') as f:
            start = 0
            for line in f:
                list_line = line[:-1].split(' ')
                if os.path.exists(list_line[-1]):
                    if (len(list_line) != 5 or (len(list_line) == 5
                       and list_line[2] != list_line[3])):
                        checked_dict['ready'].append(list_line[-1])
                    elif len(list_line) == 5:
                        checked_dict['commited'].append(list_line[-1])
                    hash = self.updateContent(list_line[-1])
                    if hash != list_line[2]:
                        checked_dict['notstaged'].append(list_line[-1])
                        self.updateIndex(hash, start, list_line[-1])
                    start += len(line)
        for file in dirs:
            if file not in checked_dict['ready']:
                if file not in checked_dict['commited']:
                    checked_dict['untracked'].append(file)
        return checked_dict

    def ready(self, ready_list, notstaged, deleted):
        if ready_list:
            print('Changes to be committed:\n\
      (use "./lgit.py reset HEAD ..." to unstage)\n\
    \
    ')  # Check print message (enters) and when git status inside sub-dir
            for i in ready_list:
                if i in deleted:
                    print('\t' + 'deleted: ' + i)
                elif i not in notstaged:
                    print('\t' + 'new file: ' + i)
                else:
                    print('\t' + 'modified: ' + i)
            print('')

    def notStaged(self, notstaged_list, deleted):
        if notstaged_list:
            print('Changes not staged for commit:\n      \
(use "./lgit.py add ..." to update what will be committed)\n      \
(use "./lgit.py checkout -- ..." to discard changes in working directory)\n\
     \
     ')
            for i in notstaged_list:
                if i in deleted:
                    print('\t' + 'deleted: ' + i)
                else:
                    print('\t' + 'modified: ' + i)
            print('')
            if (not self.checked_dict['ready'] and
               not self.checked_dict['untracked']):
                print('no changes added to commit\
 (use "./lgit.py add and/or "./lgit.py commit -a")')

    def unTracked(self, untracked_list):
        if untracked_list:
            print('Untracked files:\n      \
(use "./lgit.py add <file>..." to include in what will be committed)\n\
     \
     ')
            for i in untracked_list:
                if os.path.isfile(i):
                    print('\t' + i)
                else:
                    print('\t' + i + '/')
            print('')
            if (not self.checked_dict['ready'] and
               not self.checked_dict['notstaged']):
                print('nothing added to commit but untracked\
 files present (use "./lgit.py add" to track)')
