
import os,io,sys
import struct
from Crypto.Cipher import AES
class AESOBJ(object):
    def __init__(self,key) -> None:
        self.cipher = AES.new(key, AES.MODE_ECB)

    def e_word(self,wrd):
        test = self.cipher.encrypt(wrd)
        return test

    def encrypt(self,wrd,flag):
        res = [] 
        if(flag == "1"):
            wrd =wrd.encode("utf-8")
        
        final_wrd=b""
        if(len(wrd) > 16):
                k = 0 
                while True:
                    if(k > len(wrd)):
                        break
                    msg= wrd[k:16+k]
                    #print(len(msg))
                    print(len(msg),":",msg)
                    if(len(msg) < 16):
                    	for i in range(16-len(msg)):
                    		msg+=b" "
                    if(len(msg) <=6):
                        #print(len(msg))
                        for i in range(0,7-len(msg)):
                            msg+=b" "
                    
                    res.append(msg)
                    k+=16
        else:
            res.append(wrd) 
        
        result=[]
        for i in range(len(res)):
            wrd = res[i]
            test = self.e_word(wrd)
            final_wrd+=b"BLK"+test    
        return final_wrd   
        
    def d_decr(self,wrd):
        test = self.cipher.decrypt(wrd)
        return test
    def decrypt(self,wrd):
        final_wrd=b""
        if(len(wrd) > 16):
            wrd = wrd.split(b"BLK")
            print("LEN:",len(wrd))
            for wr in wrd:
#:                  print("len:",len(wr))
                 if(len(wr) >1 ):
                    for i in range(16-len(wr)):
                        wr+= b" "
                    #os.system("clear")
                    #print(len(wr))
                    
                    
                    final_wrd+=self.d_decr(wr)
        else:
            return self.decrypt(wrd)
        return final_wrd



