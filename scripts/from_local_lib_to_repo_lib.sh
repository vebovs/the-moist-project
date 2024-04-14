#!/bin/bash

handle_all() {
cp -r ~/Documents/Arduino/libraries/moist ./libraries/moist
}

handle_specific() {
cp -r ~/Documents/Arduino/libraries/$1 ./libraries/$1
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
      echo "Usage: $0 [-f file_name] [-d directory_name]"
      exit 1
      ;;
  esac
done