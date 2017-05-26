#!/bin/bash

# Layouts to switch between
layouts=(no us)
currentLayout="$(setxkbmap -query | grep layout | cut -c 13-14)"


len=${#layouts[@]}
i=0
for l in "${layouts[@]}"
do
	if [ "$l" = "$currentLayout" ] 
	then
		if (( i == len-1 ))
		then
			i=-1
		fi
		newLayout="${layouts[i+1]}"
	fi
	((i++))
done

setxkbmap -layout $newLayout