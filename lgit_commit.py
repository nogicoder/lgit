import os
from datetime import datetime


class LgitCommit:
    def __init__(self, message):
        self.author = self.get_name()
        self.time = self.get_time()
        self.message = message
        if self.check_config() is False:
            print('You must define an author first. Use lgit config --author')
            exit(1)
        else:
            self.check_deleted_file()
            self.update_file(self.author, self.time, self.message)

    def get_name(self):
        with open('.lgit/config', 'r') as file:
            return file.read().strip()

    def get_time(self):
        return datetime.now().strftime('%Y%m%d%H%M%S.%f')

    def check_config(self):
        with open('.lgit/config', 'r') as file:
            content = file.read()
            if content:
                return True
            return False

    def check_deleted_file(self):
        index = os.open('.lgit/.deleted', os.O_RDWR)
        with open('.lgit/.deleted') as f:
            start = 0
            flag = False
            for deleted in f:
                delete = deleted.strip().split(' ')
                blank = " "*len(delete[0])
                if '[deletedbyLGIT]' in delete[0]:
                    os.pwrite(index, str.encode(blank), start)
                start += len(deleted)
        del_content = []
        content = []
        with open('.lgit/.deleted') as f:
            for deleted in f:
                delete = deleted.strip()
                content.append(delete)
        for item in content:
            if item:
                item += '\n'
                del_content.append(item)
        os.unlink('.lgit/.deleted')
        with open('.lgit/.deleted', 'a+') as file:
            for line in del_content:
                file.write(line)

    def update_file(self, author, time, message):
        shorten_time = time.split('.')[0]
        index = os.open('.lgit/index', os.O_RDWR)
        with open('.lgit/index', 'r+') as file1:
            content = file1.readlines()
            if not content:
                print('On branch master\nnothing to commit, working ' +
                      'directory clean')
                exit(1)
            else:
                position = 0
                commited = False
                for line in content:
                    length = len(line)
                    line = line.strip().split(' ')
                    if line[2] == line[3]:
                        position += length
                    elif line[2] != line[3]:
                        commited = True
                        position += len(line[0]) + len(line[1]) + \
                            len(line[2]) + 3
                        os.pwrite(index, str.encode(line[2]), position)
                        position += len(line[2]) + len(line[-1]) + 2
                        with open('.lgit/snapshots/' + self.time,
                                  'a+') as file2:
                            file2.write(line[2] + ' ' + line[-1] + '\n')
                if commited is False:
                    print('On branch master\nnothing to commit, working ' +
                          'directory clean')
                    exit(1)
                else:
                    with open('.lgit/commits/' + self.time, 'w') as file:
                        file.write(author + "\n" + shorten_time + "\n\n" +
                                   message)
