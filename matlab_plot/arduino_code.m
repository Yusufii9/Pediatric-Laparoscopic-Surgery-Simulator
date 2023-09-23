clear all
clc
myarduino = arduino('COM4','Mega2560','Libraries','I2C');
%scanI2CBus(myarduino,0);
sensor1 = device(myarduino,'I2CAddress','0x68','bitrate',100000);
sensor2 = device(myarduino,'I2CAddress','0x69','bitrate',100000);
data1 = read(sensor1, 16,'uint16');
data2 = read(sensor2, 16,'uint16');
disp(data1);
disp(data2);