#!/bin/bash

handle_all() {
cp -r ~/Documents/Arduino/libraries/moist ./libraries
}

handle_specific() {
cp -r ~/Documents/Arduino/libraries/$1 ./libraries
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