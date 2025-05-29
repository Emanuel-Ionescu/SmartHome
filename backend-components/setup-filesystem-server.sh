#!/bin/sh
# v 2.0
# imx93 version

# setting up .profile file
echo 'alias ls="ls --color=auto"' >> ~/.profile
echo 'alias la="ls -a"'           >> ~/.profile
echo 'alias ll="ls -al"'	      >> ~/.profile
echo 'alias ld="ls -d */"'        >> ~/.profile
echo 'alias python=python3'       >> ~/.profile
echo 'alias pip="python3 -m pip"' >> ~/.profile

echo 'alias download-app="scp -r nxg05093@10.172.1.192:/home/nxg05093/SmartHome/imx93-components/*.py /SmartHome-Server"' >> ~/.profile

# creating file system

mkdir -p /SmartHome-Server/users_data/default_user

echo "0000+noadmin" | md5sum   > /SmartHome-Server/users_data/default_user/.pin
touch 			                 /SmartHome-Server/users_data/default_user/.identifier
echo "temperature:20,0,3,3,3"  > /SmartHome-Server/users_data/default_user/.config
echo "lights:255,255,255,100" >> /SmartHome-Server/users_data/default_user/.config

mkdir -p /SmartHome-Server/house/Bathroom/Lights
mkdir -p /SmartHome-Server/house/Bedroom1/Lights
mkdir -p /SmartHome-Server/house/Bedroom2/Lights
mkdir -p /SmartHome-Server/house/Garage/Lights
mkdir -p /SmartHome-Server/house/Kitchen/Lights
mkdir -p /SmartHome-Server/house/Livingroom/Lights

touch /SmartHome-Server/house/Bathroom/Lights/Bulb{0..2}
touch /SmartHome-Server/house/Bedroom1/Lights/Bulb{3..4}
touch /SmartHome-Server/house/Bedroom2/Lights/Bulb{5..7}
touch /SmartHome-Server/house/Garage/Lights/Bulb{8..9}
touch /SmartHome-Server/house/Kitchen/Lights/Bulb{10..12}
touch /SmartHome-Server/house/Livingroom/Lights/Bulb{13..16}

mkdir -p /SmartHome-Server/house/Livingroom/Outlets/
mkdir -p /SmartHome-Server/house/Garage/Outlets/

touch /SmartHome-Server/house/Livingroom/Outlets/Outlet1
touch /SmartHome-Server/house/Livingroom/Outlets/TV
touch /SmartHome-Server/house/Garage/Outlets/Car-Charger



echo "1:18:5:0:1" > /SmartHome-Server/house/Bathroom/temperature.config
echo "1:18:5:0:1" > /SmartHome-Server/house/Bedroom1/temperature.config
echo "1:18:5:0:1" > /SmartHome-Server/house/Bedroom2/temperature.config
echo "1:18:5:0:1" > /SmartHome-Server/house/Garage/temperature.config
echo "1:18:5:0:1" > /SmartHome-Server/house/Kitchen/temperature.config
echo "1:18:5:0:1" > /SmartHome-Server/house/Livingroom/temperature.config

python3 -m pip install "numpy<2.0" 
python3 -m pip install opencv-python
python3 -m pip install tflite-runtime
python3 -m pip install pillow
python3 -m pip install pytapo
python3 -m pip install flatbuffers
python3 -m pip install --upgrade lxml

scp -r nxg05093@10.172.1.192:~/SmartHome/ethos-dir.tar.gz


scp -r nxg05093@10.172.1.192:~/SmartHome/ethos-dir.tar.gz ~
tar -xvzf ~/ethos-dir.tar.gz
cp -r ~/ethos-dir/* /usr/local/lib/python3.11/site-packages/

scp -r nxg05093@10.172.1.192:~/SmartHome/shared_libs/* ~/shared_libs
cp ~/shared_libs/libethosu_delegate.so /usr/lib/libethosu_delegate.so
cp ~/shared_libs/libtensorflow-lite.so.2.12.1  /usr/lib64/libtensorflow-lite.so.2.12.1

#optional
cp /run/media/root-mmcblk0p2/usr/lib/libpython3.11.so.1.0 /usr/lib64/libpython3.11.so.1.0


