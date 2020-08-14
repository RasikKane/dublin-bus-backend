#!/bin/bash
fileIn="$1"
fileOut="$2"
cat $fileIn | cut -d ';' -f1- | sed 's/;/,/g' >> $fileOut
