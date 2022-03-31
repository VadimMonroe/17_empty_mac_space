import sys
import os
import shutil
import threading
import time
import warnings
from stat import *

import pandas as pd

if not sys.warnoptions:
    warnings.simplefilter("ignore")


class SearchingBigFiles:
    def __init__(self):
        self.hdd_size = shutil.disk_usage('/').total
        self.hdd_size_mg = self.hdd_size / (1024 * 1024)

        self.hdd_size_files_quantity = os.statvfs('/').f_files

        self.all_searching_file_size = 0
        self.all_searching_file_count = 0

        self.files_base_df = pd.DataFrame()
        # self.done_folders_path = []
        # self.list_of_sizes = []
        self.count_of_writed_files = 0
        self.period = self.hdd_size_files_quantity / 10

    def searching_files(self, top: str, callback) -> bool:
        """recursively descend the directory tree rooted at top,
           calling the callback function for each regular file"""
        try:
            for dir_file in os.listdir(top):
                pathname = os.path.join(top, dir_file)
                mode = os.stat(pathname).st_mode
                if S_ISREG(mode):
                    callback(pathname)
                elif S_ISDIR(mode):
                    # It's a directory, recurse into it
                    self.searching_files(pathname, callback)

                else:
                    # Unknown file type, print a message
                    # print('Skipping %s' % pathname)
                    pass
        except Exception as E1:
            # print('E1:', E1)
            pass
        end_of_search = True
        return end_of_search

    def base(self, file_size_inner, path):
        self.files_base_df = \
            self.files_base_df.append({'file_size': f"{file_size_inner / (1024 * 1024):.4f}", 'path': path},
                                      ignore_index=True)
        self.files_base_df = self.files_base_df.sort_values(by='file_size', ascending=False)

    def visitfile(self, file: str) -> None:
        file_size = os.stat(file).st_size
        self.all_searching_file_size += file_size
        self.all_searching_file_count += 1
        self.base(file_size, file)

    def thread_func_print(self) -> None:
        while True:
            print(
                f"files checked \033[034m{(self.all_searching_file_count * 100) / self.hdd_size_files_quantity:.3f}\033[0m \033[035m%\033[0m size checked: \033[034m{(self.all_searching_file_size / (1024 * 1024)) / (self.hdd_size / (1024 * 1024)):.3f}\033[0m \033[035m%\033[0m")
            print(f'{(self.all_searching_file_size / (1024 * 1024)):.0f} MG of {(self.hdd_size / (1024 * 1024)):.0f} MG')
            # print(f'Next save:\033[034m{len(self.list_of_sizes) / int(self.period):.2f} \033[035m%\033[0m')
            time.sleep(5)


if __name__ == '__main__':
    searching_for_delete = SearchingBigFiles()

    searching_for_delete.print_result_process = threading.Thread(target=searching_for_delete.thread_func_print)
    searching_for_delete.print_result_process.start()

    done_searching_bool = searching_for_delete.searching_files('/', searching_for_delete.visitfile)
    if done_searching_bool:
        searching_for_delete.files_base_df.to_pickle('b.pkl')
