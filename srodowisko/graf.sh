#!/bin/bash
x=$(apt list --installed)
r=0
while IFS= read -r line
do
    line=${line%%/*}
    y="$(apt-cache depends $line | grep -w Depends)"
    z="$(echo -n "$y" | grep -c '^')"
    r=$(( $r + $z ))
done <<< "$x"
echo "$r"
