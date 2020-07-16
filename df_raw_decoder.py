#!/usr/bin/python3

import zlib
from io import BytesIO
import os
from os.path import isfile, isdir, exists, realpath, join as joinPath

from_bytes = lambda x: int.from_bytes(x, byteorder="little")
from_int16 = lambda x: x.to_bytes(2, byteorder="little")
from_int32 = lambda x: x.to_bytes(4, byteorder="little")

"""Функция декодирования текстового raw-файла"""
def decode_datafile(zipfile, txtfile):
    with open(zipfile, 'rb') as _zip:
        zip_length = from_bytes(_zip.read(4)) #Первые 4 байта - длина последующего архива
        deflate = _zip.read()

    if zip_length == len(deflate):
        #Обработка файла
        unpacked = zlib.decompress(deflate)
        buf = BytesIO()
        buf.write(unpacked)
        buf.seek(0)
        lines_count = from_bytes(buf.read(4)) #Первые 4 байта - кол-во строк
        result = []
        
        file_path, fn = os.path.split(zipfile)
        
        # Файл index имеет туже структуру, но немного "зашифрован"
        indexFile = fn == 'index'

        for line in range(lines_count):
            _len = from_bytes(buf.read(4)) #Длина строки
            _len2 = from_bytes(buf.read(2)) #Она же еще раз?
            if _len != _len2:
                print("Incorrect length of the line:", line)
            _str = buf.read(_len)

            if indexFile:
                _str = bytes([(255-(i%5)-c) % 256 for i,c in enumerate(_str)])

            result.append(_str)

        _dir = os.path.dirname(txtfile)
        if not exists(_dir):
            os.mkdir(_dir)
            
        with open(txtfile, 'wb') as out_file:
            for line in result:
                out_file.write(line + b'\n')
         
    else:
        print('Incorrect length of the file:', zipfile)

"""Функция кодирования текстового raw-файла"""
def encode_datafile(txtfile, zipfile):
    with open(txtfile, 'rb') as txt:
        lines = [line.rstrip(b'\n\r') for line in txt.readlines()]
    
    buf = BytesIO()

    buf.write(from_int32(len(lines))) #Записываем количество строк

    file_path, fn = os.path.split(zipfile)
    
    # Файл index имеет туже структуру, но немного "зашифрован"
    indexFile = fn == 'index'

    for line in lines:
        _len = len(line)
        buf.write(from_int32(_len))
        buf.write(from_int16(_len))
        if indexFile:
            encoded = bytes([(255-(i%5)-c) % 256 for i,c in enumerate(line)])
            buf.write(encoded)
        else:
            buf.write(line)

    deflate = zlib.compress(buf.getvalue())
    buf.close()

    _dir = os.path.dirname(zipfile)
    if not exists(_dir):
        os.mkdir(_dir)

    with open(zipfile, 'wb') as _zip:
        _zip.write(from_int32(len(deflate)))
        _zip.write(deflate)


"""Функция рекурсивного обхода и декодирования файлов
Ищет файлы в каталоге data/ и сохраняет в data_src/"""
def decode_directory(directory, outdir):

    #Пробуем обрабатывать все файлы, у которых нет расширения
    for root, directories, files in os.walk(frompath):
        for file in files:
            fn, ext = os.path.splitext(file)
            if ext == "":
                new_path = root.replace(frompath, topath)
                decode_datafile(joinPath(root, file), joinPath(new_path, file) + ".txt")
            


def encode_directory(inputdir, outputdir):

    #Пробуем обрабатывать все файлы с расширением .txt
    for root, directories, files in os.walk(inputdir):
        for file in files:
            fn, ext = os.path.splitext(file) #Получаем имя файла без .txt
            if ext == ".txt":
                new_path = root.replace(inputdir, outputdir)
                encode_datafile(joinPath(root, file), joinPath(new_path, fn))


usage="""Dwarf Fortress RAW decoder/encoder
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

import sys

if __name__ == '__main__':
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
    topath   = realpath(topath)

    print("action:", action)
    print("overWrite:",overwrite)
    print("frompath:", frompath)
    print("topath:", topath)


    if action:
        if exists(frompath):
            if isdir(frompath):
                #Если цель - каталог
                if exists(topath):
                    if not overwrite:
                        answer = input("Directory %s already exists, overwrite? [y/N] " % topath)
                        if not (answer in ["y","Y"]):
                            print("Interrupted by the user")
                            exit()
                
                #Обработка каталога, в зависимости от выбранного действия
                func["directory"][action](frompath, topath)
                    
            elif isfile(frompath):
                #Если цель - один файл
                if exists(topath):
                    if not overwrite:
                        answer = input("File %s already exists, overwrite? [y/N] " % topath)
                        if not (answer in ["y","Y"]):
                            print("Interrupted by the user")
                            exit()
                        
                #Обработка файла, в зависимости от выбранного действия
                func["file"][action](frompath, topath)
            else:
                print("File type not recognized")
        else:
            print("Given path of the source directory doesn't exist")
        
    else:
        print(usage)
        exit()
