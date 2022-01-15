 ## The Bingbadaboom System Stability Monitor

This project was created out of the need to measure system stability on Linux. There currently is no other measurement of how stable a system runs, how many crashes it has had, and in Linux, there was not even a way to tell if the system crashed at all, for example having a Kernel panic, it just restarts and does not let you know about this important fact. All you see is the restart message in the log.

The idea of Bingbadaboom (sound of system falling down, I always have to chose especially clever names for my projects) is also to make systems comparable. Years back, I noticed that my Android smartphone was crashing a little too often and I wanted to track this and compare it to my much more reliable Linux desktops, laptops and servers.

The system is composed of 3 parts: 
1. The deamon component that runs in the background: bingbadaboomd.py
2. The utility to query data from the deamon: bingbadaboom-util.py
3. The library module: bingbadaboomd.py (will be shared by all the super large enterprise grade framework, just kidding: it just has one function)

There are also config files in yaml format that are handled as an object in the tool, i.e. gets loaded directly into an object and saved.
Bingbadaboom creates a lockfile at startup and erases it again when shutting down gracefully. If the system should crash, the file is left over when the system comes up again. The time of the crash is noted in the log. 
Bingbadaboom-util calculates the Markus system stability index, which is right now calculated with a very long, super complex and proprietary secret formula.
Joke aside, it just calculates how many crashes per how many hours the system has suffered.



Todo: 
Package this into a .DEB package through github action, the directory structure of the install is provided in the Debian_packaging directory.

