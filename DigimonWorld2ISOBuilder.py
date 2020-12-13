from sys import argv
from pathlib import Path
from Utils import FileIO
# from Utils import Debugging
from Utils import UserFeedback

import confuse


class DigimonWorld2ISOBuilder(object):
    def __init__(self, args):
        config = confuse.Configuration('DigimonWorld2ISOBuilder')
        config.set_file("config.yaml")

        general_config = config["general"]
        file_config = config["files"]

        self.data_dir = general_config["data_path"].get(str)
        self.binary_file = general_config["binary_path"].get(str)
        self.output_file = general_config["output_path"].get(str)
        self.batch_factor = general_config["batch_factor"].get(int)

        self.supported_dirs = []

        self.chunk_size = 2048
        # Sector sizes on PSX discs seems to be 2352 and anything after
        # 2048 seems to be sector metadata.
        self.sector_size = 2352

        # For some reason (possibly header) the data sectors start
        # after 24 bytes.
        self.offset_adjustment = 24

        # calculate the difference between the sector and the chunk.
        self.sector_padding = self.sector_size - self.chunk_size

        # For each file in the supported directories (recursive),
        # add the file to a list.
        for supported_dir in file_config["supported_directories"].get(list):
            self.supported_dirs = [
                file_glob for file_glob in (
                    Path(self.data_dir) / supported_dir
                    ).rglob("*") if not file_glob.is_dir()
                ]

        # File containing offsets
        self.offsets = FileIO(
            Path(__file__).resolve().parent / "offsets.json").read_json(
        )

        # print header to console
        self.print_header()

        # allow for the option to generate offset file or create
        # a patched ISO.
        if args.lower() == "offsets":
            self.find_offsets()
        elif args.lower() == "patch":
            self.patch_file()
        else:
            print("Unrecognised action")

        print("ISO / Binary creation successful")

    def print_header(self):
        """Basic file header for info
        """
        seperator = "*"*50

        print(seperator)
        print("Digimon World 2 ISO Builder")
        print("Author: ChaosWargreymon")
        print("Version: 0.2b")
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
            source_path = self.supported_dirs.pop(0)
            print("Generating offset for: {}".format(source_path))
            relative_path = str(Path(source_path).relative_to(self.data_dir))

            self.offsets[relative_path] = "0"

            source_file = FileIO(source_path)

            source_chunk = source_file.read_chunk(chunk_size=self.chunk_size)
            source_chunk_len = len(source_chunk)

            # If the source file is below the required 1024 chunk, zero pad it.
            if source_chunk_len < self.chunk_size:
                source_chunk += bytes(
                    [0] * (self.chunk_size - source_chunk_len)
                )

            iterator = 0

            # Loop through each sector of the binary and if the data within
            # the sector matches that of the source file, add the offset
            # to the file.
            while self.get_sector(iterator) <= binary_file.file_size():
                current_offset = self.get_offset(iterator)
                binary_chunk = binary_file.read_chunk(
                    chunk_size=self.chunk_size, offset=current_offset
                )

                if source_chunk == binary_chunk:
                    self.offsets[relative_path] = hex(current_offset)
                    break

                iterator += 1

        offset_file.write_json(self.offsets)

    def patch_file(self):
        """Patch the source files into a workable ISO.
        """

        binary_file = FileIO(self.binary_file)
        binary_file_size = binary_file.file_size()
        patched_data = FileIO(self.output_file)

        iterator = 0

        print("Patching ISO")

        patched_data.write_chunk(
            binary_file.read_chunk(chunk_size=self.offset_adjustment)
        )

        batch = bytes()

        # Create objects for percentage and loading bar.
        percentage = UserFeedback.Percentage(binary_file_size)
        percentage.update(self.get_sector(iterator))

        loading_bar = UserFeedback.LoadingBar()

        while self.get_sector(iterator) < binary_file.file_size():
            # Write to file only when the batch has been filled
            # and then flush it.
            if len(batch) >= (self.sector_size * self.batch_factor):
                patched_data.write_chunk(batch)
                batch = bytes()

            current_offset = self.get_offset(iterator)
            binary_chunk = binary_file.read_chunk(
                chunk_size=self.chunk_size,
                offset=current_offset
            )
            sector_padding = binary_file.read_chunk(
                chunk_size=self.sector_padding,
                offset=current_offset + self.chunk_size
            )

            if current_offset in [
                self.hex_to_int(value)
                    for value in self.offsets.values()
                    ]:
                for key in list(self.offsets):
                    value = self.offsets[key]

                    source_file = FileIO(Path(self.data_dir) / key)

                    if not source_file.exists():
                        self.offsets.pop(key)
                        continue

                    if current_offset == self.hex_to_int(value):
                        for source_chunk in source_file.read_in_chunks(
                            chunk_size=self.chunk_size
                        ):
                            source_chunk_len = len(source_chunk)

                            # If the source file is below the required 1024
                            # chunk, zero pad it.
                            if source_chunk_len < self.chunk_size:
                                batch += source_chunk
                                batch += (
                                    bytes([0] * (
                                        self.chunk_size - source_chunk_len)
                                        )
                                    )
                            else:
                                batch += source_chunk

                            current_offset = self.get_offset(iterator)
                            batch += binary_file.read_chunk(
                                chunk_size=self.sector_padding,
                                offset=current_offset + self.chunk_size
                                )

                            iterator += 1

                        self.offsets.pop(key)

            else:
                batch += binary_chunk
                batch += sector_padding

                iterator += 1

            if iterator % 200 == 0:
                percentage.update(self.get_sector(iterator))
                loading_bar.update(
                    loading_bar.create_bar(percentage.calculate())
                )

                if loading_bar.changed or percentage.changed:
                    print("{} {}".format(
                        loading_bar.output(),
                        percentage.output()),
                        end="\r")

        # If there is still data in the batch, patch the last bit of data.
        # and flush the batch to be safe.
        if len(batch) != 0:
            patched_data.write_chunk(batch)
            batch = bytes()

        percentage.update(self.get_sector(iterator))
        loading_bar.update(loading_bar.create_bar(percentage.calculate()))
        print("{} {}".format(
            loading_bar.output(),
            percentage.output()),
            end="\r")

        print()

    def hex_to_int(self, hex_string):
        if hex_string.startswith("$"):
            hex_string = hex_string[1:]
        return int(hex_string, 16)

    def get_offset(self, iterator):
        return self.offset_adjustment + self.get_sector(iterator)

    def get_sector(self, iterator):
        return iterator * self.sector_size


if len(argv) > 1:
    DigimonWorld2ISOBuilder(argv[1])
else:
    DigimonWorld2ISOBuilder("patch")
