from os.path import join, dirname, abspath, isdir, isfile, exists
from os import mkdir


class Logger:
    def __init__(self, *path):
        self.columns = []
        executed_file_path = dirname(abspath(__file__))
        log_directory = join(executed_file_path, *path, 'logs')
        tracker_file_path = join(log_directory, 'last_log.txt')

        new_log_number = 1

        if isfile(log_directory):
            raise FileExistsError(log_directory)
        elif not exists(log_directory):
            print("Creating log directory under `{}`".format(log_directory))
            mkdir(log_directory)
        else:
            print("Directory `{}` exists. Using it as log directory.".format(log_directory))

        if isdir(tracker_file_path):
            raise FileExistsError(tracker_file_path)
        elif not exists(tracker_file_path):
            with open(tracker_file_path, 'w') as f:
                f.write("1\n")
        else:
            with open(tracker_file_path, 'r') as f:
                new_log_number = int(f.read())+1
            with open(tracker_file_path, 'w') as f:
                f.write("{}\n".format(new_log_number))

        self.log_path = join(log_directory, '{}log.csv'.format(new_log_number))
        self.log_fd = open(self.log_path, 'wt', encoding='utf-8')
        self.header_written = False

        print("Logger initialized. Writing to `{}`".format(self.log_path))

    def write_dict(self, robot_info: dict):
        if self.header_written:
            print("Cannot write dict to log as header is already written. This will create unusable csv file")
            return
        for key in robot_info.keys():
            self.log_fd.write('{}: {}, '.format(key, robot_info[key]))
        self.log_fd.write('\n')

    def set_columns(self, columns) -> None:
        self.columns = columns
        header = ','.join(columns)+'\n'
        self.log_fd.write(header)
        print("Log header is `{}`".format(header[:-1]))
        self.header_written = True

    def log(self, values) -> None:
        if not self.header_written:
            self.set_columns(list(values.keys()))

        row = dict.fromkeys(self.columns, 0)
        row_string = ""
        for key in self.columns:
            row[key] = values.setdefault(key, 0)
            row_string += "{:f},".format(row[key])
        row_string = row_string[:-1]
        self.log_fd.write(row_string+'\n')

    def close(self):
        self.log_fd.close()
