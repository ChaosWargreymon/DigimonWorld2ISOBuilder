from cx_Freeze import setup, Executable

base = None

executables = [Executable("ProcessFile.py", base=base)]

packages = ["idna", "json", "Utils", "timeit", "sys", "pathlib"]
includefiles = ["config.json", "offsets.json"]
options = {
    "build_exe": {    
        "packages":packages,
        "include_files":includefiles,
        "build_exe": "..\\build"
    },
}

setup(
    name = "DW2 Tool",
    options = options,
    version = "0.1",
    description = "DW2 Tool",
    executables = executables
)