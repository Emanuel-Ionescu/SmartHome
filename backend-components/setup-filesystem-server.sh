#!/bin/sh
# v 2.0
# server version

# creating file system

mkdir -p ./users_data/default_user

echo "0000+noadmin" | md5sum   > ./users_data/default_user/.pin
touch 			                 ./users_data/default_user/.identifier
echo "temperature:20,0,3,3,3"  > ./users_data/default_user/.config
echo "lights:255,255,255,100" >> ./users_data/default_user/.config

mkdir -p ./house/Bathroom/Lights
mkdir -p ./house/Bedroom1/Lights
mkdir -p ./house/Bedroom2/Lights
mkdir -p ./house/Garage/Lights
mkdir -p ./house/Kitchen/Lights
mkdir -p ./house/Livingroom/Lights

touch ./house/Bathroom/Lights/Bulb{0..2}
touch ./house/Bedroom1/Lights/Bulb{3..4}
touch ./house/Bedroom2/Lights/Bulb{5..7}
touch ./house/Garage/Lights/Bulb{8..9}
touch ./house/Kitchen/Lights/Bulb{10..12}
touch ./house/Livingroom/Lights/Bulb{13..16}

mkdir -p ./house/Livingroom/Outlets/
mkdir -p ./house/Garage/Outlets/

touch ./house/Livingroom/Outlets/Outlet1
touch ./house/Livingroom/Outlets/TV
touch ./house/Garage/Outlets/Car-Charger



echo "1:18:5:0:1" > ./house/Bathroom/temperature.config
echo "1:18:5:0:1" > ./house/Bedroom1/temperature.config
echo "1:18:5:0:1" > ./house/Bedroom2/temperature.config
echo "1:18:5:0:1" > ./house/Garage/temperature.config
echo "1:18:5:0:1" > ./house/Kitchen/temperature.config
echo "1:18:5:0:1" > ./house/Livingroom/temperature.config