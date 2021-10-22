import zlib
from io import BytesIO

import pytest

from df_raw_decoder import (
    decode_data, DecodingException, encode_to_int32, encode_to_int16, encode_data,
    encode_decode_index_file_line
)


def test_invalid_file():
    file = BytesIO()
    file.write(100 .to_bytes(4, 'little'))
    file.write(b'\0')
    file.seek(0)

    with pytest.raises(DecodingException):
        next(decode_data(file))


def test_encode_decode():
    lines = [b'test']
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


def test_decode_encode_index_file_line():
    line = b'test'
    assert encode_decode_index_file_line(encode_decode_index_file_line(line)) == line
