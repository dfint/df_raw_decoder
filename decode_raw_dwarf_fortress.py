
import zlib
from io import BytesIO

int_from_bytes = lambda x: int.from_bytes(x, byteorder="little")
from_int16 = lambda x: x.to_bytes(2, byteorder="little")
from_int32 = lambda x: x.to_bytes(4, byteorder="little")

"""Функция декодирования текстового raw-файла"""
def decode_datafile(zipfile, txtfile):

    _zip = open(zipfile, 'rb')
    zip_length = int_from_bytes(_zip.read(4)) #Первые 4 байта - длина последующего архива
    deflate = _zip.read()

    if zip_length == len(deflate):
        #Обработка файла
        unpacked = zlib.decompress(deflate)
        buf = BytesIO()
        buf.write(unpacked)
        buf.seek(0)
        lines_count = int_from_bytes(buf.read(4)) #Первые 4 байта - кол-во строк

        result = []

        for line in range(lines_count):
            _len = int_from_bytes(buf.read(4)) #Длина строки
            _len2 = int_from_bytes(buf.read(2)) #Она же еще раз?
            if _len != _len2:
                print("Некорректная длина в строке:", line)
            _str = buf.read(_len)
            
            result.append(_str)

        open(txtfile, 'wb').write(b"\n".join(result))
            
         
    else:
        print('Некорректная длина файла', filename)
        
"""Функция кодирования текстового raw-файла"""
def encode_datafile(txtfile, zipfile, encoding="cp1251"):

    lines = [line.strip() for line in open(txtfile, 'rt').readlines()]
    buf = BytesIO()

    buf.write(from_int32(len(lines)))

    for line in lines:
        _len = len(line)
        buf.write(from_int32(_len))
        buf.write(from_int16(_len))
        buf.write(line.encode(encoding))

    deflate = zlib.compress(buf.getvalue())
    buf.close()

    _zip = open(zipfile, 'wb')
    _zip.write(from_int32(len(deflate)))
    _zip.write(deflate)
    _zip.close()
    
    
if __name__ == "__main__":

    zipfile = '/home/user/Games/df_linux/data/help/a_first'

    decode_datafile(zipfile, "/tmp/a_first")
    encode_datafile("/tmp/a_first","/tmp/a_first_1")
    decode_datafile("/tmp/a_first_1", "/tmp/a_first_2")
    encode_datafile("/tmp/a_first_2","/tmp/a_first_3")
    decode_datafile("/tmp/a_first_3", "/tmp/a_first_4")


