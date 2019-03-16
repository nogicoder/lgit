import os
from rsync import sync_file
from datetime import datetime
import difflib


class LgitBranch:
    def __init__(self, command, branch_name, stash=False):
        self.branch_name = branch_name
        self.command = command
        self.current_branch = self.get_current_branch()
        if self.command == 'branch':
            self.initialize(branch_name, self.current_branch)
        elif self.command == 'checkout':
            if not stash:
                self.checkout(branch_name, self.current_branch)
            self.update_working_dir()
        elif self.command == 'merge':
            self.merge(branch_name, self.current_branch)

    def get_current_branch(self):
        with open('.lgit/HEAD') as file:
            return file.read().strip().split('/')[-1]

    def initialize(self, branch_name, current_branch):
        branches = os.listdir('.lgit/refs/heads')
        if branch_name in branches:
            print("fatal: A branch named '" + branch_name +
                  "' already exists.")
            exit(1)
        branch_path = '.lgit/refs/heads/' + branch_name
        current_branch_path = '.lgit/refs/heads/' + current_branch
        with open(current_branch_path) as file:
            file1 = open(branch_path, 'w+')
            file1.write(file.read())
            file1.close()

    def checkout(self, branch_name, current_branch):
        branches = os.listdir('.lgit/refs/heads')
        if branch_name not in branches:
            print("error: pathspec '" + branch_name +
                  "' did not match any file(s) known to lgit.")
            exit(1)
        elif branch_name == current_branch:
            print("Already on " + "'" + branch_name + "'")
            exit(1)
        else:
            with open('.lgit/HEAD', 'w+') as file:
                file.write("refs: refs/heads/" + branch_name)
                print("Switched to branch '" + branch_name + "'")

    def sync_content(self, commit_path):
        with open(commit_path) as file:
            for line in file:
                line = line.strip().split(' ')
                dest = os.path.abspath(line[1])
                content_path = '.lgit/objects/' + line[0][:2] + \
                               '/' + line[0][2:]
                sync_file(content_path, dest)

    def find_trash(self, commit_list):
        with open('.lgit/index', 'r') as f:
            for line in f:
                list_line = line[:-1].split(' ')
                file = list_line[-1]
                if file not in commit_list:
                    self.remove(file)

    def dictIndex(self):
        added_files = {}
        with open('.lgit/index', 'r') as f:
            for line in f:
                fn = line[:-1].split(' ')
                added_files[fn[-1]] = line
        return added_files

    def remove(self, fname):
        added_files = self.dictIndex()
        os.unlink(fname)
        for x in added_files:
            if fname == x:
                del added_files[x]
                break
        with open('.lgit/index', 'w') as f1:
            f1.write(''.join(added_files.values()))

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

    def update_working_dir(self):
        current_branch = self.get_current_branch()
        list = {}
        with open('.lgit/refs/heads/' + current_branch) as file:
            commit_list = file.readlines()
            for commit in commit_list:
                commit = commit.strip()
                commit_path = '.lgit/snapshots/' + commit
                self.sync_content(commit_path)
                with open(commit_path) as file:
                    for line in file:
                        line = line.strip().split(' ')
                        list[line[1]] = line[0]
        for x in list:
            self.update_index(x, list[x])
        self.find_trash(list)

    def create_temp_index(self, current, mergefile):
        temporary_index = {}
        for x in mergefile:
            with open('.lgit/snapshots/' + x[:-1], 'r') as f:
                for line in f:
                    line_list = line[:-1].split(' ')
                    temporary_index[line_list[-1]] = line_list[0]
        return temporary_index

    def get_current_index(self):
        current_index = {}
        with open('.lgit/index', 'r') as f1:
            index_content = f1.readlines()
        for line in index_content:
            line = line[:-1].split()
            if line[3] != '':
                current_index[line[-1]] = line[3]
        return current_index

    def update_file(self, filename, hash):
        with open('.lgit/objects/%s/%s' % (hash[:2], hash[2:])) as f:
            content = f.read()
        with open(filename, 'w+') as f1:
            f1.write(content)
        self.update_index(filename, hash)

    def read_objects(self, mergehash, curhash):
        with open('.lgit/objects/%s/%s' % (mergehash[:2], mergehash[2:])) as f:
            mergecontent = f.readlines()
        with open('.lgit/objects/%s/%s' % (curhash[:2], curhash[2:])) as f1:
            curcontent = f1.readlines()
        return mergecontent, curcontent

    def check_conflict(self, merge_content, cur_content):
        d = difflib.SequenceMatcher(None, cur_content, merge_content)
        diff = d.get_opcodes()
        return list(diff)

    def write_conflict(self, diff, cur_branch, mer_branch, mcontent, ccontent,
                       fname):
        head = '<<<<<<< %s\n' % 'HEAD'
        mid = '=======\n'
        tail = '>>>>>>> %s\n' % mer_branch
        flag = True
        final = []
        for direction, cur_x, cur_y, mer_x, mer_y in diff:
            if direction == 'replace':
                flag = False
                final.append(head)
                for x in range(cur_x, cur_y):
                    final.append(ccontent[x])
                final.append(mid)
                for x in range(mer_x, mer_y):
                    final.append(mcontent[x])
                final.append(tail)
            elif direction == 'equal':
                for x in range(cur_x, cur_y):
                    final.append(ccontent[x])
            elif direction == 'insert':
                for x in range(mer_x, mer_y):
                    final.append(mcontent[x])
            elif direction == 'delete':
                for x in range(cur_x, cur_y):
                    final.append(ccontent[x])
        with open(fname, 'w+') as f:
            content = ''.join(final)
            f.write(content)
        return flag

    def print_conflict(self, conflict, fname):
        if conflict:
            print('Auto-merging %s' % fname)
        else:
            print('Auto-merging %s' % fname)
            print('CONFLICT (content): Merge conflict in %s' % fname)

    def merge(self, branch_name, current_branch):
        if branch_name == current_branch:
            print('Already up-to-date.')
            exit(1)
        else:
            with open('.lgit/refs/heads/' + branch_name, 'r') as file1:
                content1 = file1.readlines()
            with open('.lgit/refs/heads/' + current_branch, 'r') as file2:
                content2 = file2.readlines()
            if content1 == content2:
                print('Already up-to-date.')
                exit(1)
            if content2[-1] not in content1:
                # check_conflict
                temporary_index = self.create_temp_index(content2, content1)
                current_index = self.get_current_index()
                for file in temporary_index:
                    if file not in current_index:
                        self.update_file(file, temporary_index[file])
                    else:
                        merg, cur = self.read_objects(temporary_index[file],
                                                      current_index[file])
                        difflist = self.check_conflict(merg, cur)
                        flag = self.write_conflict(difflist, current_branch,
                                                   branch_name, merg,
                                                   cur, file)
                        self.print_conflict(flag, file)
                        if not flag:
                            print('Automatic merge failed;\
 fix conflicts and then commit the result.')
            else:
                # fast_foward
                with open('.lgit/refs/heads/' + branch_name, 'r') as content:
                    content1 = content.read()
                with open('.lgit/refs/heads/' + current_branch, 'w') as cur:
                    cur.write(content1)
                self.update_working_dir()
                print('Fast-foward')
