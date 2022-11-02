
"""
**********************************************

    @title: cyfly Network Protocol
    @module: Forwarding server
    @author:nitrodegen
    (C) Gavrilo Palalic 2022

**********************************************
"""
from curses import ERR
import os,io,sys
from socket import * 
import struct
from ctypes import *
import crypto_aes
from multiprocessing import Process, Queue
NOT_FOUND = 2
OK = 3 
DAEMON = 3283
SERVER_PORT = 3284
CYFLY_HEADER=b"\x42\x44\x69\x32\x52\x33\x69"
CHUNK_SIZE = 2048 
#debugging messages
INFO = "[ INFO ]"
ERROR = "[ ERROR ]"
WARN = "[ WARNING ]"
SUCC= "[ OK ]"
#TODO : it is saying that there are no peers, cause data isn't shared between processes.fix that one bitch.
class cyflyServer(object):
    def __init__(self):
        self.q = Queue()

        self.peers=[]
        s= socket(AF_INET,SOCK_STREAM,0)
        s.bind(("127.0.0.1",SERVER_PORT))
        s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        s.listen(25536)
        print(INFO+" server started.")
        self.q.put(self.peers)
        while True:
            conn,addr = s.accept()
            d = Process(target = self.handle_requests,args=[self.q,conn,addr])
            d.start()

    def send_daemon_upload_request(self,ip,chunk):
        s =socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,DAEMON))
        req = CYFLY_HEADER+b":::"+b"save_file:::"+chunk
        s.send(req)
        resp = s.recv(2)
        s.close()
        if(resp == b"ER"):
            return NOT_FOUND
        else:
            return OK

    def ask_peer_for_file(self,ip,data):
        s = socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,DAEMON))
        s.send(CYFLY_HEADER+b":::fetch:::"+data)
        files=[]
        while True:
            d = s.recv(2048)
         #   print(d)
      
            if(len(d) <=0):
            #    print("A??")
                break
            if(b"NOT_FOUND" in d):
                return None
            if(b"DONE" in d):
             #   print("A????")
                d=d.replace(b"DONE",b"")
                files.append(d)
                break
            files.append(d)
        #print(files)
        if(b"NOT_FOUND" in files):
            return None
        if(len(files) ==0):
            return None
        s.close()
        return files

    def ask_uploader_to_decrypt_data(self,ip,data):
        req = CYFLY_HEADER+b":::decrypt:::"
       # print("ALOO")
        chunks=[]
        b = 0
        while True:
            if(b >=len(data)):
                break
           # print("ALOP",b)

            chunk = data[b:b+CHUNK_SIZE]
            chunks.append(chunk)
            b+=CHUNK_SIZE
            #chunks.append(chunk)
        #print("IM DONE")

        s = socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,DAEMON))
        s.send(req)

        resp = s.recv(2)
       # print("received:"resp)
        if(resp == b"OK"):
            for c in chunks:
                s.send(c)
            s.send(b"DONE")

            decrypted=b""
            while True:
                chunk = s.recv(CHUNK_SIZE)
                if(len(chunk) ==0 ):
                    break
                if(b"DONE" in chunk):
                    chunk = chunk.replace(b"DONE",b"")
                    decrypted+=chunk
                    break
                decrypted+=chunk
            return decrypted
        else:
            return NOT_FOUND


        
    def handle_requests(self,q,conn,addr):
        self.peers =q.get()
        #print(self.peers)
        data = conn.recv(CHUNK_SIZE)    
        print("Peers:",self.peers)
        checker = data[0:len(CYFLY_HEADER)]
        if(checker == CYFLY_HEADER):
            conn.send(b"OK")
        else:
            conn.send(b"ER")

        data = data.split(b":::")

#        exit(1)
        if(data[1] == b"connect"):
            
            self.peers.append(addr)
            print(INFO+" new peer connected ",addr)
            conn.send(b"CONNECTED")

       # print(data)
        if(data[1] == b"close"):
            
            for peer in self.peers:
                if(peer[0] == addr[0]):
                    self.peers.remove(peer)
                    break
            print(INFO+" peer ",addr," removed.")
        
        if(data[1] == b"render"):
            cont= True
            print(INFO+"  rendering...")
            #asking every peer for files
            filed=b""
            for i in range(len(self.peers)):
            
                addr  = self.peers[i][0]
                file = self.ask_peer_for_file(addr,data[2])
                if(file == None):
                    print(WARN +" peer ",i, " doesn't have the files for the website.")
                    conn.send(b"ERROR:NOT_FOUNDDONE")
                    cont=False

                else:
                    filed = file
                  #  print("GOT IT.")
                    break
            if(cont== True):
                #os.system("clear")
                filed = filed[1].split(b":::")
                uploader = filed[0]
                file_data= filed[1]
                resp = self.ask_uploader_to_decrypt_data(uploader,file_data)
                if(resp == NOT_FOUND):
                    conn.send(b"ER")
                else:
                    #print(INFO+" sending decrypted file back to client...")
                    
                    chunks =[] 
                    d = 0 
                    while True:
                       # print(d)
                        if(d >=len(resp)):
                            break
                        chunk = resp[d:d+CHUNK_SIZE]
                        chunks.append(chunk)
                        d+=CHUNK_SIZE


                    for c in chunks:
                        conn.send(c)
                    
                    conn.send(b"DONE")
                    print(INFO+" sending decrypted file back to client...")
                    
        if(data[1] ==b"upload"):
        
            number_of_chunks = data[2]
            number_of_chunks=int(number_of_chunks)
            #print(number_of_chunks)
            chunks =[]
            while True:
                data =conn.recv(CHUNK_SIZE)
                if(len(data) ==0):
                    break
                if(b"DONE" in data):
                    data=data.replace(b"DONE",b"")
                    chunks.append(data)
                    break
                chunks.append(data)
            data=b""
            for c in chunks:
                data+=c
            #print(data)
            data =data.split(b"//")
            #print(data)
            print(INFO+" connected peers : " ,len(self.peers))
            if(len(self.peers) == 0):
                print(WARN+" no peers are connected on the network. can't host.")
                conn.send(b"CS")
            else:
                conn.send(b"OK")
                if(len(self.peers) < number_of_chunks):
                    print(WARN+" not enough connected clients.")
                    conn.send(b"ER")
                else:
                    for i in range(len(self.peers)):
                        chunk = chunks[i].split(b"/D/")
                        #print(chunk)
                        #print(chunk)
                        if(len(chunk) == 1):
                            chunk =chunks[i]
                        #    print("ALO")
                        else:
                            chunk = chunk[len(chunk)-1]
                         #   print("hello")
                        #print("chunk:",chunk)
                        chunk = addr[0].encode()+b":::"+chunk
                        ip= self.peers[i][0]
                        resp = self.send_daemon_upload_request(ip,chunk)
                        if(resp == OK):
                            print(SUCC+" chunk ",i," successfully sent.")
                        else:
                            print(ERROR+" failed to send requested chunk. invalid response.")
                            conn.send(b"ER")
                            break
                    conn.send(b"OK")

        #add "remove" cmd to close peers.
        q.put(self.peers)

if __name__ == "__main__":
    server= cyflyServer()
