import zlib
from io import BytesIO

import pytest

from df_raw_decoder import (
    decode_data, DecodingException, encode_to_int32, encode_to_int16, encode_data,
    encode_decode_index_file_line, pack_data, unpack_data
)


def test_invalid_file():
    file = BytesIO()
    file.write(100 .to_bytes(4, 'little'))
    file.write(b'\0')
    file.seek(0)

    with pytest.raises(DecodingException):
        next(decode_data(file))


def test_pack_unpack():
    lines = [b'Hello', b'World']
    assert list(unpack_data(BytesIO(pack_data(lines)))) == lines


def test_encode_decode():
    lines = [b'Hello', b'World']
    assert list(decode_data(BytesIO(encode_data(lines)))) == lines
    assert list(decode_data(BytesIO(encode_data(lines, True)), True)) == lines


def test_invalid_line_length():
    buf = BytesIO()

    buf.write(1 .to_bytes(4, 'little'))

    line = b'test'
    buf.write(encode_to_int32(len(line)))
    buf.write(encode_to_int16(len(line) + 1))

    deflate = zlib.compress(buf.getvalue())
    file = encode_to_int32(len(deflate)) + deflate

    with pytest.raises(DecodingException):
        next(decode_data(BytesIO(file)))


@pytest.mark.parametrize("encoded,decoded", [
    (b'\x96\x90\x99\x97\x83', b'index'),
    (
        b'\xcd\xce\x7f\xac\x89\x90\x97\x8b\x9b\x8e\x92\x99\x99\xdc\x99\x86\xde\xa9\x9b\x89\x91\xde\xbc\x98\x9a\x92\x8b',
        b'20~Programmed by Tarn Adams'
    ),
    (b'\xcd\xca\x7f\xb8\x84\x9e\x8c\x97\xdc\xb5\x90\x8c\x89\x8a\x96\x8c\x8b', b'24~Dwarf Fortress'),
])
def test_decode_encode_index_file_line(encoded, decoded):
    assert encode_decode_index_file_line(encoded) == decoded
    assert encode_decode_index_file_line(encode_decode_index_file_line(encoded)) == encoded
