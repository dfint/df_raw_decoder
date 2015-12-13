
import zlib
from io import BytesIO

little4bytes = lambda x: int.from_bytes(x, byteorder="little")

#def decode_datafile(zipfile, txtfile):
zipfile = '/home/user/Games/df_linux/data/help/a_first'

filename = zipfile.split("/")[-1]

_zip = open(zipfile, 'rb')
zip_length = little4bytes(_zip.read(4))
deflate = _zip.read()

if zip_length == len(deflate):
    #Обработка файла
    unpacked = zlib.decompress(deflate)
    buf = BytesIO()
    buf.write(unpacked)
    buf.seek(0)
    lines_count = little4bytes(buf.read(4))

    for line in range(lines_count):
        _len = little4bytes(buf.read(4))
        _len2 = little4bytes(buf.read(2))
        if _len != _len2:
            print("Incorrect line length in line:", line)
        _str = buf.read(_len)
        print(_str)
     







    
else:
    print('Некорректная длина файла', filename)
    exit()



