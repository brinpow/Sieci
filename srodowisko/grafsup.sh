#!/bin/bash
x="$(apt list --installed)"
y="$( while IFS= read -r line ; do line=${line%%/*} ; echo "$line" ; done <<< "$x" | uniq )"
z="$(apt-cache depends $y | grep -w Depends )"
r="$(echo -n "$z" | grep -c '^')"
echo "$z"
echo "$r"
r=$(wc -l <<< "${z}")
echo "$r"
