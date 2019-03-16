import os
from datetime import datetime


class LgitLog:
    def __init__(self):
        self.list = self.listing_commits()
        self.print_out_content(self.list)

    def listing_commits(self):
        commits_list = os.listdir('.lgit/commits')
        return sorted(commits_list, reverse=True)

    def print_out_content(self, list):
        for filename in list:
            year = int(filename[0:4])
            month = int(filename[4:6])
            day = int(filename[6:8])
            hour = int(filename[8:10])
            minute = int(filename[10:12])
            second = int(filename[12:14])
            t = datetime(year, month, day, hour, minute, second)
            time = t.strftime('%a %b %d %H:%M:%S %Y')
            path = '.lgit/commits/' + filename
            with open(path, 'r') as file:
                content = file.read().split('\n')
                author = content[0]
                message = content[-1]
                if filename in list[:-1]:
                    print('commit ' + filename)
                    print('Author: ' + author + '\n'
                          + 'Date: ' + time + '\n\n\t' + message
                          + '\n\n')
                else:
                    print('commit ' + filename)
                    print('Author: ' + author + '\n'
                          + 'Date: ' + time + '\n\n\t' + message)
