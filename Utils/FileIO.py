import json
from pathlib import Path


class FileIO(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def read_file(self, mode="rb", seek_offset=0, read_amount=-1):
        try:
            with open(self.file_name, mode) as f:
                if seek_offset != 0:
                    f.seek(seek_offset)

                if read_amount != -1:
                    file_data = f.read(read_amount)
                else:
                    file_data = f.read()
            return bytearray(file_data)
        except OSError:
            print("File {} Not Found".format(self.file_name))
            return None

    def write_file(self, data, mode="wb"):
        with open(self.file_name, mode) as f:
            f.write(data)

    def read_json(self):
        file_data = {}

        try:
            with open(self.file_name) as f:
                file_data = json.loads(f.read())
        except OSError:
            print("File {} Not Found".format(self.file_name))

        return file_data

    def write_json(self, data, mode="w"):
        with open(self.file_name, mode) as f:
            f.write(json.dumps(data))

    def read_in_chunks(self, mode="rb", chunk_size=1024):
        with open(self.file_name, mode) as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

    def read_chunk(self, mode="rb", chunk_size=1024, offset=0):
        with open(self.file_name, mode) as f:
            f.seek(offset)
            data = f.read(chunk_size)
        return data

    def file_size(self):
        return Path(self.file_name).stat().st_size

    def write_chunk(self, data, mode="ab"):
        with open(self.file_name, mode) as f:
            f.write(data)

    def exists(self):
        return Path(self.file_name).exists()


    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def chunk_index(chunk, n):
        for index, value in enumerate(chunk):
            if value == n:
                return index
