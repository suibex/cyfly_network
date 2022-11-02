/*
    ** cyfly Network Protocol **
      @module: client sender package
        @author:nitrodegen
          @year: 2022
          (C) Gavrilo Palalic        
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <openssl/aes.h>
#include <dirent.h> 
#include <time.h>
#include "helpers.h"

//make creator of website first, make my own key from my bios signature.
//then read all website data, encrypt it. wait to be sent.

int check_valid_machine_key(){
  int res=0;
  DIR *d;
  struct dirent *dir;
  d = opendir("./.cyfly_net_cache");
  if(d){
      while((dir = readdir(d))!= NULL){
        if(strcmp(dir->d_name,"mb_machine_key.key")==0){
          res++;
        }
      }
        closedir(d);
  }  
  else{
    return 1;
  }
  if(res > 0){
    return 0;
  }
  else{
    return 1;
  }
}
void cyfly_generate_machine_key(){

  char *serial_num= (char*)malloc(128);
  memset(serial_num,'\0',128);
  #ifdef __APPLE__  
    printf("\n*** detected OS: macOS");
    FILE *p = popen("ioreg -l | grep IOPlatformSerialNumber","r");
    char buff[256];
    while((fgets(buff,256,p))!= NULL){
    //  printf("\nbuff:%s",buff);
    }
    int go =0;
    char serial[128];
    memset(serial,'\0',128);
    int b =0; 
    for(int i =0;i< strlen(buff);i++){
      if(buff[i] =='='){
        go++;
      }
      if(go >0){
        if(buff[i] != '"' && buff[i] !='=' && buff[i] != ' '){
            serial[b] = buff[i];
            b++;
        }
      }
      memcpy(serial_num,serial,strlen(serial));
  }

  

  #else __linux__ || __ANDROID__
    printf("\n*** detected OS: Linux");
    //TODO: do this for linux 
    if(getuid() > 0  ){
      printf("\n*** cyfly protocol needs to be running as root to generate keys.");
      exit(1);
    }   
    // /sys/devices/virtual/dmi/id/board_serial
    FILE *a = fopen("/sys/devices/virtual/dmi/id/board_serial","r");
    fseek(a,0,SEEK_END);
    long size = ftell(a);
    fseek(a,0,SEEK_SET);
    char *sr = (char*)malloc(size);
    fread(sr,sizeof(char),size,a);
    fclose(a);
    memcpy(serial_num,sr,strlen(sr));


  #endif
  srand(time(NULL));
  int bb= strlen(serial_num)-1;
  while(1){
    if(bb >= 32){
      break;
    }
    char c = rand()%(105-50+1)+50;
    if(c != '\n'){
      serial_num[bb]= c;
      bb++;
    }
  }
  FILE *a = fopen("./.cyfly_net_cache/mb_machine_key.key","w");
  fwrite(serial_num,sizeof(char),strlen(serial_num),a);
  fclose(a);
  printf("\n*** private key generated.");

}
