#/usr/bin/python3.4

import zlib
from io import BytesIO
import os
from os.path import join as joinPath
from os.path import exists

from_bytes = lambda x: int.from_bytes(x, byteorder="little")
from_int16 = lambda x: x.to_bytes(2, byteorder="little")
from_int32 = lambda x: x.to_bytes(4, byteorder="little")
DATA_SRC = 'data_src'

"""Функция декодирования текстового raw-файла"""
def decode_datafile(zipfile, txtfile):

    _zip = open(zipfile, 'rb')
    zip_length = from_bytes(_zip.read(4)) #Первые 4 байта - длина последующего архива
    deflate = _zip.read()
    _zip.close()

    if zip_length == len(deflate):
        #Обработка файла
        unpacked = zlib.decompress(deflate)
        buf = BytesIO()
        buf.write(unpacked)
        buf.seek(0)
        lines_count = from_bytes(buf.read(4)) #Первые 4 байта - кол-во строк
        result = []
        
        file_path, fn = os.path.split(zipfile)
        indexFile = False
        if fn == 'index': #Файл index имеет туже структуру, но немного "зашифрован"
            indexFile = True

        for line in range(lines_count):
            _len = from_bytes(buf.read(4)) #Длина строки
            _len2 = from_bytes(buf.read(2)) #Она же еще раз?
            if _len != _len2:
                print("Некорректная длина в строке:", line)
            _str = buf.read(_len)

            if indexFile:
                _str = bytes([255-(i%5)-c for i,c in enumerate(_str)])

            result.append(_str.decode() + "\n") #Лучше чтобы все было сохранено в UTF-8
   
        open(txtfile, 'wt').writelines(result)
         
    else:
        print('Некорректная длина файла', filename)
        
"""Функция кодирования текстового raw-файла"""
def encode_datafile(txtfile, zipfile, _encoding="cp1251"):

    lines = [line[:-1] for line in open(txtfile, 'rt').readlines()]
    buf = BytesIO()

    buf.write(from_int32(len(lines))) #Записываем количество строк

    file_path, fn = os.path.split(zipfile)
    indexFile = False
    if fn == 'index': #Файл index имеет туже структуру, но немного "зашифрован"
        indexFile = True

    for line in lines:
        _len = len(line)
        buf.write(from_int32(_len))
        buf.write(from_int16(_len))
        if indexFile:
            #print(bytes(line.encode()))
            encoded = bytes([255-(i%5)-c for i,c in enumerate(line.encode(_encoding))])
            buf.write(encoded)
        else:
            buf.write(line.encode(_encoding))

    deflate = zlib.compress(buf.getvalue())
    buf.close()

    _zip = open(zipfile, 'wb')
    _zip.write(from_int32(len(deflate)))
    _zip.write(deflate)
    _zip.close()


"""Функция рекурсивного обхода и декодирования файлов
Ищет файлы в каталоге data/ и сохраняет в data_src/"""
def decode_all_files(directory=""):
    dataPath = joinPath(directory, 'data') #Исходная директория
    if not exists(dataPath):
        print("Не найден каталог 'data'")
        return

    data_src_path = joinPath(directory, DATA_SRC)

    #Пробуем обрабатывать все файлы, у которых нет расширения
    for root, directories, files in os.walk(dataPath):
        for file in files:
            fn, ext = os.path.splitext(file)
            if ext == "":
                new_path = root.replace('data', data_src_path)
                if not exists(new_path):
                    os.mkdir(new_path)
                #print(joinPath(root,file), "... OK")
                decode_datafile(joinPath(root, file), joinPath(new_path, file) + ".txt")
            


def encode_all_files(new_directory = "data_new"):
    if not exists(DATA_SRC):
        print("Не найден каталог data_src")
        return

    for root, directories, files in os.walk(DATA_SRC):
        for file in files:
            fn, ext = os.path.splitext(file) #Получаем имя файла без .txt
            txtfile = joinPath(root, file)   #Полный путь исходного файла
            new_path = root.replace(DATA_SRC, new_directory)
            if not exists(new_path):
                    os.mkdir (new_path)
            zipfile = joinPath(new_path, fn)
            encode_datafile(txtfile, zipfile)


#decode_all_files()
encode_all_files("data")


#encode_datafile('data_src/index.txt', 'data/index')
