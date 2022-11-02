
"""
**********************************************

    @title: cyfly Network Protocol
    @module: Client communication method
    @author:nitrodegen
    (C) Gavrilo Palalic 2022

**********************************************
"""

import os,io,sys
from socket import * 
import struct
from ctypes import *
import crypto_aes
from requests import get
import json 
NOT_FOUND = 2
OK = 3 
SERVER_PORT = 3284
CYFLY_HEADER=b"\x42\x44\x69\x32\x52\x33\x69"
CHUNK_SIZE = 2048
#debugging messages
INFO = "[ INFO ]"
ERROR = "[ ERROR ]"
WARN = "[ WARNING ]"
SUCC = "[ OK ]"
#basically, had to rewrite everyting in python, cause it is easier for this non-perfomant stuff.
if(len(sys.argv) < 4):
  print("******************~ cyfly network protocol ~********************\n\ncommand list:\n\tupload {folder dir} - uploading a website online to peers.\n\tconnect {server ip} - connect to network.\n\tdelete {domain} - remove website from our network.\n\trender {domain} - connect to website and render it\n\n")
  exit(1)

class cyflyComm(object):
  def __init__(self,cmd,arg,ip):
    #render syntax: render {domain} : render test.com 
    if(cmd == "render"):
        res = self.send_data_to_server(cmd,arg,ip,SERVER_PORT)
        if(res == NOT_FOUND):
          print(ERROR+" server declined specified request.")
        else:
          print(SUCC+" done")

    if(cmd == "upload"):
        data =self.load_and_encrypt(arg)
       # ip =str(get("https://api64.ipify.org/?format=json").json()['ip'])
      #data
        res = self.send_data_to_server(cmd,data,ip,SERVER_PORT)
        if(res == NOT_FOUND):
          print("[Error]: server declined specified request.")
    if(cmd == "close"):
        s = socket(AF_INET,SOCK_STREAM,0)
        s.connect((ip,SERVER_PORT))
        s.send(CYFLY_HEADER+b":::close:::")
      #pass
  def send_data_to_server(self,cmd,data,ip,port):
    key = open(".cyfly_net_cache/mb_machine_key.key","rb").read() 
    aes = crypto_aes.AESOBJ(key)
    #data = aes.encrypt(data,"0")
    
    
    data= cmd.encode("utf-8")+b"/D/"+data
    
    s = socket(AF_INET,SOCK_STREAM,0)
    s.connect((ip,port))
    dt =0 
    chunks =[ ]
    while True:
      if(dt >=len(data)):
        break

      d = data[dt:dt+CHUNK_SIZE]
      dt+=CHUNK_SIZE
      chunks.append(d)

    lenreq = CYFLY_HEADER+b":::"+cmd.encode("utf-8")+b":::"+str( len(chunks)).encode("utf-8")
   # print(lenreq)
    #print(lenreq)
    s.send(lenreq)
    dat = s.recv(2)
    if(dat == "ER"):
      return NOT_FOUND
    else:
      print("[ OK ] request replied with OK.")
      for c in chunks:
        s.send(c)
      s.send(b"DONE")
    d = s.recv(2)
    if(d == b"CS"):
      print("[ERROR] no peers were connected on the network.")
    if(d == b"OK"):
      print("[ OK ] valid request.")

    s.close()
    return OK
  def load_and_encrypt(self,dir):

    fd = os.listdir(dir)
    found_tools = False
    domain_access=[]
    for d in fd:
      if(d == "rules"):
        found_tools=True
        ruleing= open(dir+"/rules","r")
        ruleing=ruleing.read().split("\n")
        
        for rule in ruleing:
          if("domain" in rule):
            domain_access.append(rule.split(":")[1]+"=")
         #print(rule)
          if("RULE" in rule):
            rule = rule.split(":")
            #print(rule)
            path=[]
            path.append(rule[1].encode("utf-8"))
            fd = open(dir+"/"+rule[2],"r")
            fd =fd.read()
            key = open(".cyfly_net_cache/mb_machine_key.key","rb").read()
          
            aes = crypto_aes.AESOBJ(key)
            data = aes.encrypt(fd,"1")
            path.append(data)
            domain_access.append(path)


    if(found_tools==False):
      return NOT_FOUND
    
    res=b""
    res+=domain_access[0].encode("utf-8")+b"mmm"
    for i in range(1,len(domain_access)):
      bb=domain_access[i][0]+b"::/"+domain_access[i][1]
      res+=bb+b"mmm"
    #print(res)
    #exit(1)
    return res

so = CDLL("./client.so")
if(so.check_valid_machine_key() == 1):
  print("*** machine key was not generated. generating...")
  so.cyfly_generate_machine_key()
  exit(1)
cmd = sys.argv[1]
arg = sys.argv[2]
ip = sys.argv[3]
comm = cyflyComm(cmd,arg,ip)

