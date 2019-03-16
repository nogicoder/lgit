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
            self.parents_commit = self.get_parents_commit()
            self.current_branch = self.get_current_branch()
            self.last_commit = self.update_file(self.author, self.time,
                                                self.parents_commit,
                                                self.message,
                                                self.current_branch)

    def check_config(self):
        if os.path.exists('.lgit/config'):
            with open('.lgit/config') as f:
                author = f.readlines()
            if author:
                return True
            else:
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
                print(line)
                file.write(line)

    def get_name(self):
        with open('.lgit/config', 'r') as file:
            return file.read().strip()

    def get_time(self):
        return datetime.now().strftime('%Y%m%d%H%M%S.%f')

    def get_current_branch(self):
        with open('.lgit/HEAD') as file:
            return file.read().strip().split('/')[-1]

    def get_parents_commit(self):
        commits_list = os.listdir('.lgit/commits')
        if commits_list:
            return sorted(commits_list, reverse=True)[0]
        return ''

    def update_file(self, author, time,
                    parents_commit, message, current_branch):
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
                        with open('.lgit/snapshots/' + time,
                                  'a+') as file2:
                            file2.write(line[2] + ' ' + line[-1] + '\n')
                if commited is False:
                    print('On branch master\nnothing to commit, working ' +
                          'directory clean')
                    exit(1)
                else:
                    with open('.lgit/commits/' + time, 'w') as file:
                        file.write(author + "\n" + shorten_time + "\n" +
                                   parents_commit + "\n\n" + message)
                    file = open('.lgit/refs/heads/' + current_branch, 'a')
                    file.write(time + '\n')
                    file.close()
