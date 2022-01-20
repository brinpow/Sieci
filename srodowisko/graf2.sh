#!/bin/bash
x=$(apt list)
y="$( while IFS= read -r line ; do line=${line%%/*} ; echo "$line" ; done <<< "$x" )"
echo "$y"
echo "$y"
