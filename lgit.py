#!/usr/bin/env python3
import argparse
import os
import sys
import hashlib
from lgit_take_args import ArgParser
from lgit_init import Initialize
from lgit_add import LgitAdd
from lgit_status import LgitStatus
from lgit_commit import LgitCommit
from lgit_log import LgitLog


"""---------------------CHECK LGIT FOLDER----------------------"""


def check_lgit_file():
    dirs = os.listdir('.lgit')
    if ('config' not in dirs or 'index' not in dirs or 'commits' not in dirs or
       'objects' not in dirs or 'snapshots' not in dirs):
        return False
    return True


"""---------------------LGIT CONFIG----------------------------"""


def write_config(author):
    config = open('.lgit/config', 'w+')
    config.write(author + '\n')
    config.close()


"""---------------------LGIT REMOVE----------------------------"""


def rIndex(file, added_files):
    for x in added_files:
        if file == x:
            del added_files[x]
            break
    with open('.lgit/index', 'w') as f1:
        f1.write(''.join(added_files.values()))


def remove(fname):
    added_files = dictIndex()
    if fname in added_files:
        if os.path.exists(fname):
            os.unlink(fname)
        rIndex(fname, added_files)
        with open('.lgit/.deleted', 'a') as file:
            file.write(fname + '\n')
    else:
        print("fatal: pathspec '%s' did not match any files" % fname)


"""---------------------LGIT LS-FILES-------------------"""


def dictIndex():
    added_files = {}
    with open('.lgit/index', 'r') as f:
        for line in f:
            fn = line[:-1].split(' ')
            added_files[fn[-1]] = line
    return added_files


def lsFiles(current_dir):
    new = current_dir.replace(os.getcwd() + '/', '') + '/'
    current_dir2 = os.getcwd()
    for tracked_file in sorted(dictIndex().keys()):
        if new in tracked_file:
            print(tracked_file.replace(new, ''))
        elif current_dir == current_dir2:
            print(tracked_file)


def all_file_list(dir):
    file_list = []
    for root, dir, file in os.walk(dir):
        for x in file:
            result = ''
            result += root + '/'
            result += x
            file_list.append(result)
    return file_list


"""---------------------MAIN----------------------------"""


def main():
    args = ArgParser()
    command = args.arg
    current_dir = Initialize.get_current_dir()
    if not Initialize.checkParents() and command != 'init':
        print('fatal: not a git repository (or any of the parent directories)')
    elif command != 'init' and check_lgit_file() is False:
        print('fatal: Not a git repository (or any of the parent ' +
              'directories): .lgit')
    else:
        if command == 'init':
            Initialize()
        elif command == 'add':
            filename = args.add()
            for fname in filename:
                if not os.path.exists(fname):
                    LgitAdd(fname, 'None')
                else:
                    if os.path.isdir(fname):
                        file_list = all_file_list(fname)
                        for f in file_list:
                            try:
                                name = os.open(f, os.O_RDONLY)
                                content = os.read(name,
                                                  os.stat(name).st_size)
                                LgitAdd(f, content)
                            except PermissionError:
                                print('error: open("dir/file"): ' +
                                      'Permission denied')
                                print('error: unable to index file ' +
                                      'dir/file')
                                print('fatal: adding files failed')
                    else:
                        try:
                            name = os.open(fname, os.O_RDONLY)
                            content = os.read(name, os.stat(name).st_size)
                            LgitAdd(fname, content)
                        except PermissionError:
                            print('error: open("dir/file"): Permission denied')
                            print('error: unable to index file dir/file')
                            print('fatal: adding files failed')
        elif command == 'status':
            LgitStatus()
        elif command == 'commit':
            message = args.commit()
            LgitCommit(message)
        elif command == 'rm':
            filename = args.rm()
            remove(filename)
        elif command == 'ls-files':
            lsFiles(current_dir)
        elif command == 'log':
            LgitLog()
        elif command == 'config':
            author = args.config()
            write_config(author)


if __name__ == '__main__':
    main()
