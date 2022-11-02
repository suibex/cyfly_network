
"""
**********************************************

    @title: cyfly Network Protocol
    @module: Daemon client server
    @author:nitrodegen
    (C) Gavrilo Palalic 2022

**********************************************
"""

import os,io,sys
from socket import * 
import struct
from ctypes import *
import crypto_aes
from multiprocessing import Process
NOT_FOUND = 2
OK = 3 
DAEMON = 3283
CYFLY_HEADER=b"\x42\x44\x69\x32\x52\x33\x69"
CHUNK_SIZE = 2048 
SERVER_PORT = 3284
peers=[]
#debugging messages
INFO = "[ INFO ]"
ERROR = "[ ERROR ]"
WARN = "[ WARNING ]"
selected_size= 0 
HTML_RESP_HEADER =b"HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length:"
SERVER_TAG = b"\r\nServer:cyfly_Daemon\r\n\r\n"
#TODO: add encryption to the actual server.

def split_data(data,chunk_size):
    chunks=[]
    d = 0 
    while True:
        if(d> len(data)):
            break
        chunk = data[d:d+chunk_size]
        chunks.append(chunk)
        d+=chunk_size
    return chunks

class cyflyDaemon(object):

    def __init__(self):
        
        rr = Process(target = self.connect_to_server,args=(sys.argv[1],))
        rr.start()
        self.sock = None
        print(INFO+" cyfly daemon started.")
        s= socket(AF_INET,SOCK_STREAM,0)
        self.sock = s
        s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        s.bind(("127.0.0.1",DAEMON))
       # s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        s.listen(25536)
        try:
            while True:
                conn,addr = s.accept()
                d = Process(target = self.handle_requests,args=[conn,addr])
                d.start()
        except KeyboardInterrupt:
            self.sock.close()
            s.close()
            print(WARN+" KeyboardInterrupt triggered.")
            s = socket(AF_INET,SOCK_STREAM,0)
            s.connect((sys.argv[1],SERVER_PORT))
            s.send(CYFLY_HEADER+b":::close:::")
            s.close()

    def send_to_server(self,req,ip):
        s = socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,SERVER_PORT))
        s.send(req)

        check = s.recv(2)

        if(check == NOT_FOUND):
            print(ERROR+" failed to request.")
            exit(1)
        
        file =b""
        while True:
            cd = s.recv(CHUNK_SIZE)
            if(len(cd) ==0 ):
                break
            if(b"DONE" in cd):
                cd = cd.replace(b'DONE',b"")
                file+=cd
                break
            file+=cd

        s.close()
        return file

    def cyfly_decrypt_file(self,file):
        key = open("./.cyfly_net_cache/mb_machine_key.key","rb").read()
        aes = crypto_aes.AESOBJ(key)
        return aes.decrypt(file)


    def save_file(self,uploader,fname,data):

        fname = fname+b"_"+data[0].replace(b"/",b";;")
        fd =open("./shared_data/"+fname.decode(),"wb")
        dat =uploader+b":::"+data[1]
        fd.write(dat)
        fd.close()

    def handle_requests(self,conn,addr):
        try:
            data = conn.recv(CHUNK_SIZE)    
        
            if(b"GET" in data):
                get = data.split(b"\r\n")[0].split(b" ")
                domain = get[1]+b";;"
                
                if(get[1] == b"/favicon.ico"):
                    print(INFO+" favicon requested, sending net image..")
                    ico = open("./static/favicon.ico","rb")
                    ico= ico.read()
                    header =b"HTTP/1.0 200 OK\r\nContent-Type: image/png;\r\nContent-Length:"+str(len(ico)).encode("utf-8")+SERVER_TAG
                    ico = header+ico
                    conn.send(ico)
                else:
                    req = CYFLY_HEADER+b":::render:::"+domain
                    
                    file = self.send_to_server(req,sys.argv[1])
                    #print(file)
                    if(file[:len("ERROR")] == b"ERROR"):
                        file = b"<h1>"+file+b"</h1>"
                    #os.system("clear")
                   # print(file)
                    selected_size= len(file)
                    header = HTML_RESP_HEADER+str(len(file)).encode()+SERVER_TAG
                    file = header+file
                    #print(header)
                    conn.send(file)
                    print(INFO+" website rendering.")


            else:
                checker = data[:len(CYFLY_HEADER)]
                if(checker == CYFLY_HEADER):
                    conn.send(b"OK")
                else:
                    conn.send(b"ER")
                
                data =data[len(CYFLY_HEADER)+3:].split(b":::")
                #print(data)
                found = False
                if(data[0] == b"decrypt"):
                    file=b""
                    #print("RECEIVING HERE...")
                    while True:
                        chunk = conn.recv(CHUNK_SIZE)
                        #print(chunk)
                        if(len(chunk) == 0):
                            break
                        if(b"DONE" in chunk):
                            chunk = chunk.replace(b"DONE",b"")
                            file+=chunk
                            break
                        file+=chunk
                    decrypted = self.cyfly_decrypt_file(file)
                    chunks =[] 
                    d = 0 
                    while True:
                        
                        if(d > len(decrypted)):
                            break
                        chunk = decrypted[d:d+CHUNK_SIZE]
                        chunks.append(chunk)

                        d+=CHUNK_SIZE
                    for c in chunks:
                        conn.send(c)
                    conn.send(b"DONE")
         
                
                if(data[0] == b"fetch"):
                  #  print("HELLO NIGGA")
                                   
                    look_for = data[1].decode().split("/")
                    #print("LOOK:",look_for)

                    files = os.listdir("./shared_data")

                    for file in files:
                        pth = file 
                        file = file.split("_")
                        if(file[0] == look_for[1]):
                            file[1] = file[1].replace(";;","")
                            look_for[2]= look_for[2].replace(";;","")


                            if(file[1] == look_for[2]):
                              #  print("alo")

                                d = open("./shared_data/"+pth,"rb").read()
                                chunked = split_data(d,CHUNK_SIZE)
                                found = True
                                for c in chunked:
                                    conn.send(c)
                                conn.send(b"DONE")
                                break
                           

                    if(found == False):
                        print(ERROR+" file not found.")
                        conn.send(b"NOT_FOUND")

                if(data[0] == b"save_file"):
                    uploader= data[1]
                    filename = data[2].split(b"=")[0]
                    chunks = data[2].split(b"mmm")
                  
                    print(INFO +" blob received, saved.")


                    for i in range(1,len(chunks)):
                        chunk = chunks[i]
                        #print(chunk)
                        chunk = chunk.split(b"::/")
                        #print(chunk)
                        
                        if(len(chunk) >1):
                            self.save_file(uploader,filename,chunk)
            conn.close()

        except KeyboardInterrupt:
            print(WARN+" KeyboardInterrupt triggered.")
            self.sock.close()
            s = socket(AF_INET,SOCK_STREAM,0)
            s.connect((sys.argv[1],SERVER_PORT))
            s.send(CYFLY_HEADER+b":::close:::")
            s.close()

                
            conn.close()


    def connect_to_server(self,ip):
        s = socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,SERVER_PORT))
        s.send(CYFLY_HEADER+b":::connect:::")
        s.close()



if __name__ == "__main__":

    if(len(sys.argv) <2):
        print("provide server ip address.")
        exit(1)    
    daemon = cyflyDaemon()

