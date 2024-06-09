#!/usr/bin/env bash
if [ -z ${IP+x} ]; 
    then 
        echo "var IP is unset"; 
    else 
    scp -r robot@$(IP):/home/robot/lab5/src/logs/ ./logs;
    scp -r robot@$(IP):/home/robot/lab5/src/polar/logs/ ./polar/logs;
fi
