#!/bin/bash
read x
if [ -z "$x" ]
then
x=$(LC_ALL="pl_PL.utf8" date +"%d %B")
fi
z=":"
y="$(grep "$z$x" /home/z1172691/imieniny)"
u=","
while read -r line
do
    line=${line%%$z*}
    d="$(getent passwd | grep "$line ")"
    while read -r line1
        do
            line1=${line1%%$u*}
            line2=${line1%%$z*}
            line3=${line1##*$z}
            if ! [ -z "$line1" ]
            then
                echo "$line2 $line3"
            fi
        done <<< "$d"
done <<< "$y"

