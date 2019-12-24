<!-- Sina Sehlaver, 2099729 -->
<!-- Beyazit Yalcinkaya, 2172138 -->


# CENG 435 - Data Communications and Networking Term Project - Part II

## Requirements

1. Python3
2. Python3 Module socket
3. Python3 Module threading
4. Python3 Module struct
5. Python3 Module sys
6. Python3 Module time
7. Python3 Module hashlib
8. Python3 Module statistics
9. Python3 Module math
10. Linux Command tc/netem

## Project Structure

Below, we first give the file structure of the project. `configurationScripts` folder contains all configuration scripts that applies all `tc/netem` commands. `discoveryScripts` folder contains all scripts for discoverying the RTTs of edges between nodes. `experimentScripts` folder contains all the scripts for experiments 1, 2, and 3.

```
TP_Part2_16
│   README.md
│   tr2_request_rspec.xml
│   report.tex
│   input.txt
│
└───d
│   │   config.sh
│   │   init.sh
│   │   main.py
│   │   reset.sh
│   │   start.sh
│   │
│   
└───r1
│   │   config.sh
│   │   init.sh
│   │   main.py
│   │   reset.sh
│   │   start.sh
│   │
│   
└───r2
│   │   config.sh
│   │   init.sh
│   │   main.py
│   │   reset.sh
│   │   start.sh
│   │
│   
└───r3
│   │   config.sh
│   │   init.sh
│   │   main.py
│   │   reset.sh
│   │   start.sh
│   │
│   
└───s
│   │   config.sh
│   │   init.sh
│   │   main.py
│   │   reset.sh
│   │   start.sh
│   │
│   
```

## How to Run

Below, we specify how to run scripts for single file transfer and an experimentation.

### Single File transfer


1. Copy TP\_Part2\_16 to each machine in `~/` directory, you can also copy only the corresponding folder, i.e., for s, you do not need to copy folders named r1, r2, r3, and d.
2. Run `cd ~/TP_Part1_16`
3. From r1, run `./r1/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
4. From r2, run `./r2/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
5. From r3, run `./r3/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
6. From d, run `./d/start.sh <loss> <output file name> 1` where `<loss>` is an interger from `[0, 100]` and `<output file name>` is name of the output file
7. From s, run `./s/start.sh <exp type> <loss> <input file name> -1` where `<exp type>` if either `exp1` or `exp2`, `<loss>` is an interger from `[0, 100]` and `<output file name>` is name of the output file
8. The order of steps 3, 4, 5, and 6 are not important but step 7 must be the last one

After following these steps, s node will print the file transfer time to stdout. Notice that the input file for node s must be in `~/TP_Part1_16/`, that is where the scripts are called.

In order to merge all results run the following command.


### Experimentation


1. Copy TP\_Part2\_16 to each machine in `~/` directory, you can also copy only the corresponding folder, i.e., for s, you do not need to copy folders named r1, r2, r3, and d.
2. Run `cd ~/TP_Part1_16`
3. From r1, run `./r1/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
4. From r2, run `./r2/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
5. From r3, run `./r3/start.sh <loss>` where `<loss>` is an interger from `[0, 100]` 
6. From d, run `./d/start.sh <loss> <output file name> -1` where `<loss>` is an interger from `[0, 100]` and `<output file name>` is name of the output file
7. From s, run `./s/start.sh <exp type> <loss> <input file name> <margin of error threshold>` where `<exp type>` if either `exp1` or `exp2`, `<loss>` is an interger from `[0, 100]`, `<output file name>` is name of the output file, and `<margin of error threshold>` is a float from `[0.0, 1.0]`
8. The order of steps 3, 4, 5, and 6 are not important but step 7 must be the last one

After following these steps, s node will do the experimentation until the desired margin of error is achieved with 95% confidence interval and output sample space size, margin of error, and the file transfer time for each sample. At the end it will also print statistical info regarding sample space. Notice that the input file for node s must be in `~/TP_Part1_16/`, that is where the scripts are called.
