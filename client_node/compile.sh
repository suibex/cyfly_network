#!/bin/bash

cc cyfly_client.c -o  client.so -I/opt/homebrew/Cellar/openssl@1.1/1.1.1q/include  -L/opt/homebrew/Cellar//openssl@1.1/1.1.1q/lib/  -lcrypto -lssl -fPIC -shared;
