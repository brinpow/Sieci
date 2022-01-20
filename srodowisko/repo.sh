#!/bin/bash
x="$(apt list --installed)"
y="$( while IFS= read -r line ; do line=${line%%/*} ; echo "$line" ; done <<< "$x" | uniq )"
z="$( apt show $y )"
v="$( echo "$z" | grep 'Package:\|APT-Sources:' )"
w="$( echo "$z" | grep APT-Sources: | sort | uniq )"
r=$( wc -l <<< "${w}" )
a=""
u=""
while IFS= read -r line1
	do
		while IFS= read -r line2
		do
		if ! [ -z "$line2" ]
			then
				if [ "$line2" = "$line1" ]
					then
						a="${a}\n${u}"
					fi
			fi
	u="$line2"
	done <<< "$v"
echo "$line1"
echo -e "$a"
a=""
done <<< "$w"
echo "$r"
