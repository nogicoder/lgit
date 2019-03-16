#!/usr/bin/env python3
import argparse
import os
import sys
import hashlib


"""----------------------------SUB-FUNCTION---------------------------------"""


def is_hard_link(file):  # check if file has hardlink
    link_number = os.stat(file).st_nlink
    return link_number > 1


def check_size(source_path, dest_path):  # check if equal size
    source_size = os.lstat(source_path).st_size
    dest_size = os.lstat(dest_path).st_size
    return source_size == dest_size


def check_mtime(source_path, dest_path, u=False):  # check time condition
    source_time = os.lstat(source_path).st_mtime
    dest_time = os.lstat(dest_path).st_mtime
    if not u:
        return dest_time == source_time
    if u:
        return dest_time > source_time


def change_mode(source_path, dest_path):  # change file permission
    mode = os.lstat(source_path).st_mode
    os.chmod(dest_path, mode)


def change_time(source_path, dest_path):  # change file time
    stat = os.lstat(source_path)
    atime = stat.st_atime
    mtime = stat.st_mtime
    os.utime(dest_path, (atime, mtime), follow_symlinks=False)


def create_file(source_path, dest_path):  # create new file
    dest_file = open(dest_path, 'w')
    source_file = open(source_path, 'r')
    content = source_file.read()
    dest_file.write(content)
    dest_file.close()
    source_file.close()


def get_hash(path):  # get hash of two file
    md5 = hashlib.md5()
    file = open(path, 'rb')
    data = file.read()
    md5.update(data)
    return md5.digest()


def check_hash(source_path, dest_path):  # check if hashes equal
    return get_hash(source_path) == get_hash(dest_path)


def common_prefix(lst):  # get common prefix of two strings
    s1 = min(lst)
    s2 = max(lst)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


# update content from source to dest
def update_content(source_path, dest_path, source_size, dest_size):
    content_list = []
    fd_source = os.open(source_path, os.O_RDONLY)
    fd_dest = os.open(dest_path, os.O_RDWR)
    source_content = os.read(fd_source, source_size)
    dest_content = os.read(fd_dest, dest_size)
    content_list.append(source_content)
    content_list.append(dest_content)
    cp = common_prefix(content_list)
    os.lseek(fd_dest, len(cp), 0)
    os.write(fd_dest, source_content[len(cp):])
    os.close(fd_dest)
    os.close(fd_source)


# check the condition of two files
def sync_file(source_path, dest_path):
    if os.path.exists(dest_path):  # if dest file exists
        os.unlink(dest_path)
    create_file(source_path, dest_path)
    change_time(source_path, dest_path)


# copy the dirs and files recursively
def copy_tree(src, dst):
    names = os.listdir(src)
    if os.path.exists(dst):  # if dest exist
        pass
    elif not os.path.exists(dst):  # if dest not exist -> create new
        os.mkdir(dst)
    for item in names:
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        if os.path.isdir(src_path):
            copy_tree(src_path, dst_path)
        elif os.path.isfile(src_path):
            sync_file(src_path, dst_path)
