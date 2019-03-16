from argparse import ArgumentParser
from argparse import ArgumentError
import sys
import os


class ArgParser(object):
    def __init__(self):
        parser = ArgumentParser(description='A simplified Git')
        parser.add_argument('command', help="choose from ['init', 'add', \
                    'rm', 'config', 'commit', 'status', 'log', 'ls-files', \
                    'branch', 'stash', 'checkout', 'merge']")
        args = parser.parse_args(sys.argv[1:2])
        self.arg = args.command
        if args.command in ['ls-files', 'init', 'status', 'log', 'merge']:
            pass
        else:
            if not hasattr(self, args.command):
                print('Unrecognized command')
                parser.print_help()
                exit(1)
            getattr(self, args.command)()

    def add(self):
        parser = ArgumentParser()
        parser.add_argument('filename', type=str, nargs='+')
        if len(sys.argv) == 2:
            print("Nothing specified, nothing added.\
                       \nMaybe you wanted to say 'git add .'?")
            exit(1)
        else:
            args = parser.parse_args(sys.argv[2:])
            return args.filename

    def rm(self):
        parser = ArgumentParser()
        parser.add_argument('filename', type=str, default=None, nargs='?')
        args = parser.parse_args(sys.argv[2:])
        if args.filename is None:
            print("Nothing specified, nothing added.\
                       \nMaybe you wanted to say 'git rm .'?")
            exit(1)
        return args.filename

    def config(self):
        parser = ArgumentParser()
        parser.add_argument('--author', action='store_true')
        parser.add_argument('name', type=str)
        args = parser.parse_args(sys.argv[2:])
        return args.name

    def commit(self):
        parser = ArgumentParser()
        parser.add_argument('-m', action='store_true')
        parser.add_argument('message', type=str, default=None, nargs='?')
        args = parser.parse_args(sys.argv[2:])
        if args.message is None:
            print("Nothing specified, nothing added.\
                       \nMaybe you wanted to say 'git commit .'?")
            exit(1)
        return args.message

    def branch(self):
        parser = ArgumentParser()
        parser.add_argument('branchname', type=str, default=None, nargs='?')
        args = parser.parse_args(sys.argv[2:])
        if args.branchname is None:
            dirs = os.listdir('.lgit/refs/heads')
            with open('.lgit/HEAD') as f:
                head = f.read().strip().split('/')[-1]
            for x in dirs:
                if x == head:
                    print('*', end='')
                print(x)
            exit(1)
        elif args.branchname == 'master':
            print("fatal: A branch named 'master' already exists.")
            exit(1)
        return args.branchname

    def checkout(self):
        parser = ArgumentParser()
        parser.add_argument('branchname', type=str, default=None, nargs='?')
        args = parser.parse_args(sys.argv[2:])
        if args.branchname is None:
            print("Nothing specified, nothing added.\
                       \nMaybe you wanted to say 'git checkout .'?")
            exit(1)
        return args.branchname

    def merge(self):
        parser = ArgumentParser()
        parser.add_argument('branchname', type=str, default=None, nargs='?')
        args = parser.parse_args(sys.argv[2:])
        if args.branchname is None:
            print("Nothing specified, nothing added.\
                       \nMaybe you wanted to say 'git merge .'?")
            exit(1)
        return args.branchname

    def stash(self):
        parser = ArgumentParser()
        parser.add_argument('apply', nargs='?')
        args = parser.parse_args(sys.argv[2:])
        return args.apply
