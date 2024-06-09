#!/usr/bin/env bash
if [ -z ${IP+x} ]; 
    then 
        echo "var IP is unset";
    else 
    scp -r ./src robot@$(IP):/home/robot/lab5/src;
    scp -r ./logs/last_log.txt robot@$(IP):/home/robot/lab5/src/logs/last_log.txt;
    scp -r ./polar/logs/last_log.txt robot@$(IP):/home/robot/lab5/src/polar/logs/last_log.txt;
fi
