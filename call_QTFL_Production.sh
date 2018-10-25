#!/bin/bash
PATH=$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
echo $PATH
cd /home/solopticon/github/AIA_VideoGen/  
/usr/bin/python QTFL_Production.py
 