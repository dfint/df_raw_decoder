import zlib
from io import BytesIO
from typing import List

import pytest
from hypothesis import given, strategies as st

from df_raw_decoder import (
    decode_data,
    DecodingException,
    encode_to_int32,
    encode_to_int16,
    encode_data,
    encode_decode_index_file_line,
    pack_data,
    unpack_data,
)


def test_invalid_file():
    file = BytesIO()
    file.write((100).to_bytes(4, "little"))
    file.write(b"\0")
    file.seek(0)

    with pytest.raises(DecodingException):
        next(decode_data(file))


@st.composite
def encoded_strings(draw, *args, encoding="utf-8", **kwargs) -> bytes:
    return draw(st.text(*args, **kwargs)).encode(encoding)


@given(st.lists(encoded_strings()))
def test_pack_unpack(lines: List[bytes]):
    assert list(unpack_data(BytesIO(pack_data(lines)))) == lines


@given(st.lists(encoded_strings()))
def test_encode_decode(lines: List[bytes]):
    assert list(decode_data(BytesIO(encode_data(lines)))) == lines
    assert list(decode_data(BytesIO(encode_data(lines, True)), True)) == lines


@given(encoded_strings())
def test_invalid_line_length(byte_string: bytes):
    buf = BytesIO()

    buf.write((1).to_bytes(4, "little"))

    buf.write(encode_to_int32(len(byte_string)))
    buf.write(encode_to_int16(len(byte_string) + 1))

    deflate = zlib.compress(buf.getvalue())
    file = encode_to_int32(len(deflate)) + deflate

    with pytest.raises(DecodingException):
        next(decode_data(BytesIO(file)))


@pytest.mark.parametrize(
    "encoded, decoded",
    [
        (bytes.fromhex("96 90 99 97 83"), b"index"),
        (
            bytes.fromhex("cd ce 7f ac 89 90 97 8b 9b 8e 92 99 99 dc 99 86 de a9 9b 89 91 de bc 98 9a 92 8b"),
            b"20~Programmed by Tarn Adams",
        ),
        (bytes.fromhex("cd ca 7f b8 84 9e 8c 97 dc b5 90 8c 89 8a 96 8c 8b"), b"24~Dwarf Fortress"),
    ],
)
def test_decode_encode_index_file_line(encoded: bytes, decoded: bytes):
    assert encode_decode_index_file_line(encoded) == decoded
    assert encode_decode_index_file_line(encode_decode_index_file_line(encoded)) == encoded
