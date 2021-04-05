from OpenCv import OpenCv

cv = OpenCv()
# cv = OpenCv("https://s16.picofile.com/file/8429117892/99.jpg")
key, value = cv.process("images/img-1617467691.0312476.jpeg")
print({
    "keys" : key,
    "value" : value
})