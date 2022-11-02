#!/bin/bash

cc daemon.c -o daemon -I/opt/homebrew/Cellar/openssl@1.1/1.1.1q/include  -L/opt/homebrew/Cellar//openssl@1.1/1.1.1q/lib/  -lcrypto -lssl && ./daemon;
