import zlib

from io import BytesIO
from typing import BinaryIO, List, Iterator


def decode_int(x: bytes) -> int:
    return int.from_bytes(x, byteorder="little")


def encode_to_int16(x: int) -> bytes:
    return x.to_bytes(2, byteorder="little")


def encode_to_int32(x: int) -> bytes:
    return x.to_bytes(4, byteorder="little")


def encode_decode_index_file_line(line: bytes) -> bytes:
    return bytes([(255 - (i % 5) - c) % 256 for i, c in enumerate(line)])


class DecodingException(Exception):
    pass


def unpack_data(data: BinaryIO) -> Iterator[bytes]:
    zip_length = decode_int(data.read(4))  # Первые 4 байта - длина последующего архива
    deflate = data.read()

    if zip_length != len(deflate):
        raise DecodingException("Incorrect buffer size. Expected: {}, Actual: {}".format(zip_length, len(deflate)))

    # Обработка файла
    unpacked = zlib.decompress(deflate)
    buf = BytesIO(unpacked)
    lines_count = decode_int(buf.read(4))  # Первые 4 байта - кол-во строк

    for line in range(lines_count):
        len4 = decode_int(buf.read(4))  # Длина строки
        len2 = decode_int(buf.read(2))  # Она же еще раз?

        if len4 != len2:
            raise DecodingException("Incorrect length of the line: {!r}".format(line))

        yield buf.read(len4)


def decode_data(data: BinaryIO, decode=False) -> Iterator[bytes]:
    if decode:
        return map(encode_decode_index_file_line, unpack_data(data))
    else:
        return unpack_data(data)


def pack_data(lines: List[bytes]) -> bytes:
    buf = BytesIO()

    buf.write(encode_to_int32(len(lines)))  # Записываем количество строк

    for line in lines:
        buf.write(encode_to_int32(len(line)))
        buf.write(encode_to_int16(len(line)))

        buf.write(line)

    deflate = zlib.compress(buf.getvalue())

    return encode_to_int32(len(deflate)) + deflate


def encode_data(lines: List[bytes], encode=False) -> bytes:
    if encode:
        lines = [encode_decode_index_file_line(line) for line in lines]

    return pack_data(lines)
