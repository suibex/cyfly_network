import os,io,sys

if(len(sys.argv) < 2):
    exit(1)


fd =open(sys.argv[1],"r")
fd = fd.read()
def cyfly_web_parse(a):
    d =[]
    a = a.split("\n")
    for line in a:
        if(line == "end"):
            break
        if("domain" in line):
            print('a')
cyfly_web_parse(fd)