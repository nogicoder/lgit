import os


class Initialize:
    def __init__(self):
        self.lgit_list = ['commits', 'objects', 'snapshots',
                          'refs', 'heads', 'index',
                          'stash', 'config', 'HEAD',
                          'master']
        self.lgitInit()

    def check_lgit_file(self, miss=False):
        missing_list = []
        dirs = os.listdir('.lgit')
        if os.path.exists('.lgit/refs'):
            dirs += os.listdir('.lgit/refs')
            if os.path.exists('.lgit/refs/heads'):
                dirs += os.listdir('.lgit/refs/heads')
        for item in self.lgit_list:
            if item not in dirs:
                missing_list.append(item)
        return missing_list

    def write_config(self):
        config = open('.lgit/config', 'w+')
        config.write(os.environ['LOGNAME'])
        config.close()

    def init_master(self):
        with open('.lgit/HEAD', 'w') as file:
            file.write('refs: refs/heads/master')

    def create_file(self, filename):
        index = open(filename, 'w+')
        index.close()

    def lgitInit(self):
        try:
            os.mkdir('.lgit')
            os.mkdir('.lgit/commits')
            os.mkdir('.lgit/objects')
            os.mkdir('.lgit/snapshots')
            os.mkdir('.lgit/refs')
            os.mkdir('.lgit/refs/heads')
            os.mkdir('.lgit/stash')
            self.create_file('.lgit/.deleted')
            self.write_config()
            self.create_file('.lgit/index')
            self.create_file('.lgit/HEAD')
            self.create_file('.lgit/refs/heads/master')
            self.init_master()
        except FileExistsError:
            missing_list = self.check_lgit_file()
            if not missing_list:
                print('Git repository already initialized.')
                exit(1)
            else:
                for item in missing_list:
                    if item == 'commits':
                        os.mkdir('.lgit/commits')
                    elif item == 'objects':
                        os.mkdir('.lgit/objects')
                    elif item == 'snapshots':
                        os.mkdir('.lgit/snapshots')
                    elif item == 'index':
                        self.create_file('.lgit/index')
                    elif item == 'config':
                        self.write_config()
                    elif item == 'refs':
                        os.mkdir('.lgit/refs')
                    elif item == 'heads':
                        os.mkdir('.lgit/refs/heads')
                    elif item == 'master':
                        self.create_file('.lgit/refs/heads/master')
                    elif item == 'stash':
                        os.mkdir('.lgit/stash')
                    elif item == 'HEAD':
                        self.create_file('.lgit/HEAD')

    def checkParents():
        current = os.getcwd()
        while current != '/':
            current_list = os.listdir(current)
            if '.lgit' in current_list:
                os.chdir(current)
                return True
            current = os.path.dirname(current)
        return False

    def get_current_dir():
        return os.getcwd()
