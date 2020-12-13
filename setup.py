from cx_Freeze import setup, Executable

base = None

executables = [Executable("DigimonWorld2ISOBuilder.py", base=base)]

packages = ["idna", "confuse", "Utils", "timeit", "sys", "pathlib"]
includefiles = ["config.yaml", "offsets.json"]
options = {
    "build_exe": {    
        "packages":packages,
        "include_files":includefiles,
        "build_exe": "..\\build"
    },
}

setup(
    name = "Digimon World 2 ISO Builder",
    options = options,
    version = "0.2b",
    description = "Digimon World 2 ISO Builder",
    executables = executables
)