#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set  -e

# Enable the globstar shell option
shopt -s globstar

# Make sure we are inside the github workspace
cd $GITHUB_WORKSPACE

# Create directories
mkdir $HOME/Arduino
mkdir $HOME/Arduino/libraries

# Install Arduino IDE
export PATH=$PATH:$GITHUB_WORKSPACE/bin
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
arduino-cli config init --additional-urls https://www.pjrc.com/teensy/package_teensy_index.json
arduino-cli core update-index --additional-urls https://www.pjrc.com/teensy/package_teensy_index.json

# Install Teensy AVR core for Teensy 4.1
arduino-cli core install teensy:avr

# Link Arduino library
ln -s $GITHUB_WORKSPACE $HOME/Arduino/libraries/moist

# Install dependencies
arduino-cli lib install float16@0.2.0
arduino-cli lib install --zip-path ./dependencies/*.zip --config-file "./ci/config.yml"

# Compile ino files in the ground station subfolder
for file in ./ground_station/**/*.ino ; do
	arduino-cli compile -b teensy:avr:teensy41 $file
done

# Compile ino files in the cansat subfolder
for file in ./cansat/**/*.ino ; do
	arduino-cli compile -b teensy:avr:teensy41 $file
done