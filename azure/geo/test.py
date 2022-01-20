#!/usr/bin/env python3
import os
import subprocess

command = ['ping', "-c", '5', '149.156.75.21']
output = subprocess.check_output(command).decode().strip()
result = output.split("time=")
print(output)
print(result[1].split(' ')[0])