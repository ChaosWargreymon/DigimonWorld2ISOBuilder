# DigimonWorld2BuildTool

Command line tool to inject edited source files into a working Digimon World 2 binary / ISO file.

## Pre-requisites

A number of pre-requisites are required for the tool to work successfully.

- The source files (the AAA folder) should be extracted from the Digimon World 2 binary using ISO Buster (or equivalent). Whilst editing the files is encouraged, the overall folder structure should not be changed.

- The `config.yaml` file will need to be edited to point to a few directories on your local machine. The values are as follows:

  - `data_path` - This will need to point to the folders extracted using ISO Buster. By default, the `AAA\4.AAA` folder names have been included so only the upper directories will need to replace the `****`.

  - `binary_path` - The folder location (and file) of the original Digimon World 2 binary / ISO. By default, the path will be looking for a file titled `DW2.bin` but this can be replaced with your file name.

  - `output_path` - The folder location and file name of the generated / injected file. By default, the path will generate a file titled `DW2_built.bin` but this can be replaced with a desired file name.

  - `batch_factor` - The multiplier to apply to the sector size when deciding how many files to patch in each loop. By default, this is set as `50` as this seemed to yield the best performance benefit but experimentation may be required to tailor it to your machine.

  - `supported_directories` - A list of all directories which are currently scanned and patched into the ISO. Currently, only the `DATAFILE` and `DUNG` directories are supported.

## Running

You will need to use `cmd` to run the tool. To do this, open a command line interface in the directory and run `DigimonWorld2ISOBuilder.exe`.

## Development Pre-requesites
If you wish to test and add to the code, you will need to pip install the pre-requisites from the `requirements.txt` file.