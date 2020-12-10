from sys import argv

from pathlib import Path

from Utils import Logging
from Utils import FileIO
from Utils import Config
from Utils import Debugging

import timeit

class ProcessFile(object):
    def __init__(self, args):
        self.print_header()
        self.data_dir = Config.settings.get("DataPath")
        self.binary_file = Config.settings.get("BinaryPath")
        self.output_file = Config.settings.get("OutputPath")
        self.supported_dirs = []

        self.chunk_size = 2048
        # Sector sizes on PSX discs seems to be 2352 and anything after
        # 2048 seems to be sector metadata.
        self.sector_size = 2352

        # For some reason (possibly header) the data sectors start
        # after 24 bytes.
        self.offset_adjustment = 24

        #calculate the difference between the sector and the chunk.
        self.sector_padding = self.sector_size - self.chunk_size

        # For each file in the supported directories (recursive),
        # add the file to a list.
        for supported_dir in Config.files.get("SupportedDirectories"):
            for file_path in [file_glob for file_glob in (Path(self.data_dir) / supported_dir).rglob("*") if not file_glob.is_dir()]:
                self.supported_dirs.append(file_path)

        # Basic logging info (currently unused)
        self.logging = Logging(
            Config.settings.get("LogLevel"),
            Config.settings.get("ConsolePrint")
        )

        # File containing offsets
        self.offsets = FileIO(
            Path(__file__).resolve().parent / "offsets.json").read_json(
        )

        # allow for the option to generate offset file or create
        # a patched ISO.
        if args[0].lower() == "offsets" or args == "offsets":
            self.find_offsets()
        elif args[0].lower() == "patch" or args == "patch":
            self.patch_file()
        else:
            print("Unrecognised action")

        print("Finished")

    def print_header(self):
        """Basic file header for info
        """
        seperator = "*"*50

        print(seperator)
        print("Digimon World 2 File Tool")
        print("Author: ChaosWargreymon")
        print("Version: 0.1a")
        print(seperator)

    def find_offsets(self):
        """Function to scan the source files from a directory
        and find the offset in the ISO that the data starts.

        Note: The offsets should be distributed as part of the
              release and this should never need to be called.
        """
        print("Begin generating offsets file")

        binary_file = FileIO(self.binary_file)

        offset_file = FileIO(Path(__file__).resolve().parent / "offsets.json")

        while len(self.supported_dirs) > 0:
            # Need to make this more efficient
            source_file_path = self.supported_dirs.pop(0)
            print("Generating offset for: {}".format(source_file_path))
            relative_path = str(Path(source_file_path).relative_to(self.data_dir))

            self.offsets[relative_path] = []

            source_file = FileIO(source_file_path)

            source_chunk = source_file.read_chunk(chunk_size=self.chunk_size)

            if len(source_chunk) < self.chunk_size:
                source_chunk += bytes([0] * (self.chunk_size - len(source_chunk)))

            iterator = 0

            while (iterator * self.sector_size) <= binary_file.file_size():
                current_offset = self.get_offset(iterator)
                binary_chunk = binary_file.read_chunk(chunk_size=self.chunk_size, offset=current_offset)

                if source_chunk == binary_chunk:
                    self.offsets[relative_path].append(hex(current_offset))
                    break

                iterator += 1

        offset_file.write_json(self.offsets)

    def patch_file(self):
        """Patch the source files into a workable ISO.
        """

        binary_file = FileIO(self.binary_file)
        patched_data = FileIO(self.output_file)

        iterator = 0

        print("Begin patching")

        patched_data.write_chunk(binary_file.read_chunk(chunk_size=self.offset_adjustment))

        while (iterator * self.sector_size) < binary_file.file_size():
            current_offset = self.offset_adjustment + (iterator * self.sector_size)
            binary_chunk = binary_file.read_chunk(chunk_size=self.chunk_size, offset=current_offset)
            sector_padding = binary_file.read_chunk(chunk_size=self.sector_padding, offset=current_offset + self.chunk_size)

            if current_offset in [ProcessFile.hex_to_int(value) for value in self.offsets.values() for value in value]:
                for key in list(self.offsets):
                    print("Patching file: {}".format(key))
                    value = self.offsets[key]

                    source_file = FileIO(Path(self.data_dir) / key)

                    if not source_file.exists():
                        print("File: {} does not exist".format(key))
                        self.offsets.pop(key)
                        continue

                    if current_offset in [ProcessFile.hex_to_int(offset) for offset in value]:
                        for source_chunk in source_file.read_in_chunks(chunk_size=self.chunk_size):
                            source_chunk_len = len(source_chunk)

                            if source_chunk_len < self.chunk_size:
                                patched_data.write_chunk(source_chunk)
                                patched_data.write_chunk(bytes([0] * (self.chunk_size - source_chunk_len)))
                            else:
                                patched_data.write_chunk(source_chunk)

                            
                            # This is what is wrong because it's not calculating the sector padding
                            # offset each time it hits this point. It is simply re-using the previous
                            # offset.

                            #TODO - make this work right by dynamically calculating the correct offset
                            current_offset = self.offset_adjustment + (iterator * self.sector_size)
                            patched_data.write_chunk(binary_file.read_chunk(chunk_size=self.sector_padding, offset=current_offset + self.chunk_size))

                            iterator += 1

                        self.offsets.pop(key)

            else:
                patched_data.write_chunk(binary_chunk)
                patched_data.write_chunk(sector_padding)

                iterator += 1

    @staticmethod
    def hex_to_int(hex_string):
        if hex_string.startswith("$"):
            hex_string = hex_string[1:]
        return int(hex_string, 16)

    def get_offset(self, iterator):
        return self.offset_adjustment + (iterator * self.sector_size)

if len(argv) > 1:
    ProcessFile(argv[1:])
else:
    ProcessFile("patch")
