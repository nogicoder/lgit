import os


class Initialize:
    def __init__(self):
        self.lgit_list = ['commits', 'objects', 'snapshots',
                          'index', 'config']
        self.lgitInit()

    def check_lgit_file(self):
        missing_list = []
        dirs = os.listdir('.lgit')
        for item in self.lgit_list:
            if item not in dirs:
                missing_list.append(item)
        return missing_list

    def write_config(self):
        config = open('.lgit/config', 'w+')
        config.write(os.environ['LOGNAME'])
        config.close()

    def create_file(self, filename):
        index = open(filename, 'w+')
        index.close()

    def lgitInit(self):
        try:
            os.mkdir('.lgit')
            os.mkdir('.lgit/commits')
            os.mkdir('.lgit/objects')
            os.mkdir('.lgit/snapshots')
            self.write_config()
            self.create_file('.lgit/index')
            self.create_file('.lgit/.deleted')
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
