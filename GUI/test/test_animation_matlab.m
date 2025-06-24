%% PicoVNA S-Parameter Example
%
% The file, |PicoVNA_S_Parameter_Example.m| must be on your MATLAB Path. For
% additional information on setting your MATLAB path, see
% <matlab:doc('addpath') addpath>.
%
% Additionally you must have the |.cal| file for your device in the current
% folder.
;


%% Clear workspace, command window and close figures

clear;
clc;
close all;

%% Connect to VNA
picoVNACOMObj = connectVNA;

%% Load Calibration
currentFile = mfilename( 'fullpath' );
[pathstr,~,~] = fileparts( currentFile );
picoVNACOMObj.LoadCal(fullfile( pathstr, '20230216_two_ports.cal')

%% Stop button for exiting loop
[stopFig.f, stopFig.h] = stopButtonVNA(0, 50, 1350,1000);   
flag = 1; % Use flag variable to indicate if stop button has been clicked (0)
setappdata(gcf, 'run', flag);

%% Capture and plot data

n = 0; % Number of Loops
go = 1; % While loop condition (1 = run, 0 = stop)

while go == 1
    tic
    for s = 1:10
        picoVNACOMObj.Measure('S21');
    end
    toc
    % Instruct VNA do make a sweep measurement
    
    % Get Log magnitude data for all S-Parameters 
    %[s11.freq, s11.logmagDataPoints] = getBlockDataVNA(picoVNACOMObj,'S11','logmag');
    %[s22.freq, s22.logmagDataPoints] = getBlockDataVNA(picoVNACOMObj,'S22','logmag'); 
    %[s12.freq, s12.logmagDataPoints] = getBlockDataVNA(picoVNACOMObj,'S12','logmag');
    [s21.freq, s21.logmagDataPoints] = getBlockDataVNA(picoVNACOMObj,'S21','logmag');
    
    % Get values for y-axes limits
  
    
    maxS21c = max(s21.logmagDataPoints);
    
    if n == 0
        maxS21 = maxS21c;
    end
    
    if maxS21c > maxS21
        maxS21 = maxS21c;
    end
    
    minS21c = min(s21.logmagDataPoints);
    
    if n == 0
        minS21 = minS21c;
    end
    
    if minS21c < minS21
        minS21 = minS21c;
    end
    
    
    % Plot Data for all S-parameters
 
    
    subplot(1,1,1);
    plot(s21.freq, s21.logmagDataPoints);
    xlabel('Frequency (Hz)');
    ylabel('Magnitude (dB)');
    ylim([minS21 maxS21]);
    title('S21');
    
    
    drawnow
    
    n = n+1; % Current Loop Number
       
    % Check if stop button has been pressed
    flag = getappdata(gcf, 'run');
    if flag == 0
        go = 0;
    end
    clear  maxS21c minS21c 
end
%% Disconnect VNA

disconnectVNA(picoVNACOMObj)

% Tidy workspace
clear ans flag go maxS21 minS21 picoVNACOMObj
