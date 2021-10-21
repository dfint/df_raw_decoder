import zlib
import os

from io import BytesIO
from os.path import exists, join as join_path
from typing import Iterable, BinaryIO, List


def decode_int(x: bytes) -> int:
    return int.from_bytes(x, byteorder="little")


def encode_to_int16(x: int) -> bytes:
    return x.to_bytes(2, byteorder="little")


def encode_to_int32(x: int) -> bytes:
    return x.to_bytes(4, byteorder="little")


def encode_decode_index_file_line(line: bytes) -> bytes:
    return bytes([(255 - (i % 5) - c) % 256 for i, c in enumerate(line)])


def decode_data(_zip: BinaryIO, decode=False) -> Iterable[bytes]:
    zip_length = decode_int(_zip.read(4))  # Первые 4 байта - длина последующего архива
    deflate = _zip.read()
    assert zip_length == len(deflate), 'Incorrect buffer size'

    # Обработка файла
    unpacked = zlib.decompress(deflate)
    buf = BytesIO(unpacked)
    lines_count = decode_int(buf.read(4))  # Первые 4 байта - кол-во строк

    for line in range(lines_count):
        len4 = decode_int(buf.read(4))  # Длина строки
        len2 = decode_int(buf.read(2))  # Она же еще раз?
        assert len4 == len2, "Incorrect length of the line: {}".format(line)

        line = buf.read(len4)

        if decode:
            line = encode_decode_index_file_line(line)

        yield line


def decode_datafile(zipfile, txtfile):
    """Функция декодирования текстового raw-файла"""
    _, fn = os.path.split(zipfile)

    # Файл index имеет ту же структуру, но немного "зашифрован"
    is_index_file = fn == 'index'

    _dir = os.path.dirname(txtfile)
    if not exists(_dir):
        os.mkdir(_dir)

    with open(zipfile, 'rb') as _zip:
        result = list(decode_data(_zip, is_index_file))

    with open(txtfile, 'wb') as out_file:
        for line in result:
            out_file.write(line + b'\n')


def encode_data(lines: List[bytes], encode=False) -> bytes:
    buf = BytesIO()

    buf.write(encode_to_int32(len(lines)))  # Записываем количество строк

    for line in lines:
        buf.write(encode_to_int32(len(line)))
        buf.write(encode_to_int16(len(line)))

        if encode:
            line = encode_decode_index_file_line(line)

        buf.write(line)

    deflate = zlib.compress(buf.getvalue())
    buf.close()

    return encode_to_int32(len(deflate)) + deflate


def encode_datafile(txtfile, zipfile):
    """Функция кодирования текстового raw-файла"""
    with open(txtfile, 'rb') as txt:
        lines = [line.rstrip(b'\n\r') for line in txt.readlines()]

    _, fn = os.path.split(zipfile)

    # Файл index имеет ту же структуру, но немного "зашифрован"
    is_index_file = fn == 'index'

    data = encode_data(lines, is_index_file)

    _dir = os.path.dirname(zipfile)
    if not exists(_dir):
        os.mkdir(_dir)

    with open(zipfile, 'wb') as _zip:
        _zip.write(data)


def decode_directory(directory, outdir):
    """Функция рекурсивного обхода и декодирования файлов
    Ищет файлы в каталоге data/ и сохраняет в data_src/"""
    # Пробуем обрабатывать все файлы, у которых нет расширения
    for root, directories, files in os.walk(directory):
        for file in files:
            fn, ext = os.path.splitext(file)
            if ext == "":
                new_path = root.replace(directory, outdir)
                decode_datafile(join_path(root, file), join_path(new_path, file) + ".txt")


def encode_directory(inputdir, outputdir):
    # Пробуем обрабатывать все файлы с расширением .txt
    for root, directories, files in os.walk(inputdir):
        for file in files:
            fn, ext = os.path.splitext(file)  # Получаем имя файла без .txt
            if ext == ".txt":
                new_path = root.replace(inputdir, outputdir)
                encode_datafile(join_path(root, file), join_path(new_path, fn))
