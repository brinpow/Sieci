#!/bin/bash

function a () {
    echo "Function a with ${#} parameters"
}

function b () {
    echo "Function b with ${#} parameters: ${1} ${2}"
}

a
b
a 1
b 1
a 1 2
b 1 3

function pretty () {
    printf "%10s : %5d\n" "${1}" "${2}"
}

function stats () {
    pretty "First" "14"
    pretty "Second" "430"
    pretty "Third" "1024"
}

stats
