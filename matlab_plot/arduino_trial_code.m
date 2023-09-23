%This is a script that will plot Arduino analogRead values in real time
%Modified from http://billwaa.wordpress.com/2013/07/10/matlab-real-time-serial-data-logger/
%The code from that site takes data from Serial 
clear
clc
%User Defined Properties 
a = arduino('com4', 'Mega2560', 'Libraries', 'I2C')             % define the Arduino Communication port
plotTitle = 'Arduino Data Log';  % plot title
xLabel = 'Elapsed Time (s)';     % x-axis label
yLabel = 'Motion';      % y-axis label
legend1 = 'Sensor 1'
legend2 = 'Sensor 2'
legend3 = 'Sensor 3'
yMax  = 2                    %y Maximum Value
yMin  = 0                   %y minimum Value
plotGrid = 'on';                 % 'off' to turn off grid
min = 0;                         % set y-min
max = 2;                        % set y-max
delay = .01;                     % make sure sample faster than resolution 
%Define Function Variables
time = 0;
data = 0;
data1 = 0;
data2 = 0;
count = 0;
%Set up Plot
plotGraph = plot(time,data,'-r' )  % every AnalogRead needs to be on its own Plotgraph
hold on                            %hold on makes sure all of the channels are plotted
plotGraph1 = plot(time,data1,'-b')
plotGraph2 = plot(time, data2,'-g' )
title(plotTitle,'FontSize',15);
xlabel(xLabel,'FontSize',15);
ylabel(yLabel,'FontSize',15);
legend(legend1,legend2,legend3)
axis([yMin yMax min max]);
grid(plotGrid);
tic
%sensor1 = device(a,'SPIChipSelectPin','D53');
%sensor2 = device(a,'SPIChipSelectPin','D40');
sensor3 = device(a,'I2CAddress','0x68','bitrate',100000);
sensor4 = device(a,'I2CAddress','0x69','bitrate',100000);
while ishandle(plotGraph)         %Loop when Plot is Active will run until plot is closed
         dat = readVoltage(a, 'A0');   %Data from the arduino
         dat1 = read(sensor3, 16,'uint16')
         dat2 = read(sensor4, 16,'uint16')
         count = count + 1;    
         time(count) = toc;    
         data(count) = dat(1);         
         data1(count) = dat1(1)
         data2(count) = dat2(1)
         %This is the magic code 
         %Using plot will slow down the sampling time.. At times to over 20
         %seconds per sample!
         set(plotGraph,'XData',time,'YData',data);
         set(plotGraph1,'XData',time,'YData',data1);
         set(plotGraph2,'XData',time,'YData',data2);
          axis([0 time(count) min max]);
          %Update the graph
          pause(delay);
end
disp('Plot Closed and arduino object has been deleted');