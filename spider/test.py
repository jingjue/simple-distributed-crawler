import sys

import chardet

htmlCharsetGuess = chardet.detect()
htmlCharsetEncoding = htmlCharsetGuess["encoding"]
htmlCode_decode = pageCode.decode(htmlCharsetEncoding)
type = sys.getfilesystemencoding()
htmlCode_encode = htmlCode_decode.encode(type)
