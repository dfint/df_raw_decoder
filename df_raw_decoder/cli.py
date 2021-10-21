#!/usr/bin/python3

import sys
from os.path import isfile, isdir, exists, realpath

from df_raw_decoder import decode_directory, encode_directory, decode_datafile, encode_datafile

usage = """Dwarf Fortress RAW decoder/encoder
Usage:
df_enc.py [options] <inputDir>  <outputDir>
df_enc.py [options] <inputFile> <outputFile>

Options:
-d  --decode - decode files from the source directory
-e  --encode - encode files from the source directory
-y  --yes    - force overwrite of the existing files/directories
"""

func = {"directory":{"--decode":decode_directory,"--encode":encode_directory,
                           "-d":decode_directory,      "-e":encode_directory},
        "file"     :{"--decode":decode_datafile, "--encode":encode_datafile,
                           "-d":decode_datafile,       "-e":encode_datafile}}


def main():
    if len(sys.argv) < 4:
        print(usage)
        exit()

    action = ""
    overwrite = False
    frompath = sys.argv[-2]
    topath = sys.argv[-1]

    for option in sys.argv[1:-2]:
        if option in ["--decode", "--encode", "-d", "-e"]:
            action = option
        elif option in ["--yes", "-y"]:
            overwrite = True

    frompath = realpath(frompath)
    topath = realpath(topath)

    print("action:", action)
    print("overWrite:", overwrite)
    print("frompath:", frompath)
    print("topath:", topath)

    if action:
        if exists(frompath):
            if isdir(frompath):
                # Если цель - каталог
                if exists(topath):
                    if not overwrite:
                        answer = input("Directory %s already exists, overwrite? [y/N] " % topath)
                        if not (answer in ["y", "Y"]):
                            print("Interrupted by the user")
                            exit()

                # Обработка каталога, в зависимости от выбранного действия
                func["directory"][action](frompath, topath)

            elif isfile(frompath):
                # Если цель - один файл
                if exists(topath):
                    if not overwrite:
                        answer = input("File %s already exists, overwrite? [y/N] " % topath)
                        if not (answer in ["y", "Y"]):
                            print("Interrupted by the user")
                            exit()

                # Обработка файла, в зависимости от выбранного действия
                func["file"][action](frompath, topath)
            else:
                print("File type not recognized")
        else:
            print("Given path of the source directory doesn't exist")

    else:
        print(usage)
        exit()


if __name__ == '__main__':
    main()
