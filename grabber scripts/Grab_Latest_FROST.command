#!/usr/bin/env python

import subprocess
import glob
import os
import datetime
import sys

global_date = datetime.datetime.now()
global_date = str(global_date)
year = global_date.split("-")[0]
month = global_date.split("-")[1]
day = str(int(global_date.split("-")[2].split(" ")[0]) - 1).zfill(2)

latest_video = str(year) + "_" + str(month) + "_" + str(day) + "_FROST_VideoWall_Concatenated.mp4"

subprocess.call('scp solopticon@solopticon:~/github/AIA_VideoGen/daily_mov/' + str(latest_video) + " ~/Downloads", shell = True)