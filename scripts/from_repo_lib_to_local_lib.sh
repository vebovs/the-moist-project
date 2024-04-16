#!/bin/bash

handle_all() {
    cp -r ./libraries/moist ~/Documents/Arduino/libraries
}

handle_specific() {
    cp -r ./libraries/$1 ~/Documents/Arduino/libraries
}

while getopts "ad:" option; do
  case $option in
    a)
      handle_all
      ;;
    d)
      handle_specific "$OPTARG"
      ;;
    *)
      exit 1
      ;;
  esac
done