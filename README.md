# iperfScanner

# TITLE: iPerf Discovery
# Author: Kris Armstrong
# Date: June 14, 2017
# Version 1.0.11

# Revision History

# Known Defects: June 7, 2017
# options file parser incomplete

# FUTURE FEATURES: June 6, 2017
# Adding Threading would speed scan time

# Change Log
# ----------------------------------------------------------------------------
# Kris Armstrong | June 14 2017| Removed Threading                           |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 12 2017| Changed function name to tcp_port_ping      |
#                |             | Setup separate timers for tcp_ping and query|
#                |             | First pass at adding docstrings             |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 8 2017 | Moved iPerf query to its own function       |
#                |             | Attempt 1 - Threading                       |
#                |             | Added Argparse -v Version                   |
#                |             | Added Argparse -o Option File               |
#                |             | Added Argparse -t default timeout over ride |
#                |             | Added Argparse -th Threaded mode            |
#                |             | Removed aircheck_sqlLITE function as it     |
#                |             | will not be used                            |
#                |             | Created option_file parser                  |
# ----------------------------------------------------------------------------
# Kevin Loftin   | June 7 2017 | Skip custom parsing and write raw results   |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 7 2017 | Removed Custom logging                      |
#                |             | Implemented the Python Logging Library      |
#                |             | Attempting to implement variable timeout    |
#                |             | Improved VarName Read ability               |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 6 2017 | Added command line arguments                |
#                |             | Moved onscreen output to log file           |
#                |             | Method Cleanup                              |
#                |             | Variable name cleanup                       |
#                |             | Removed unused imports                      |
#                |             | FIXED: Invalid counts (not counting)        |
#                |             | FIXED: Output not seperating strings        |
#                |             | FIXED: iPerf Accessory file was not purged  |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 5 2017 | Added Output to file for iPerf Remotes      |
#                |             | Started Output formatting changes           |
# ----------------------------------------------------------------------------
# Kris Armstrong | June 1 2017 | Added Logging Method                        |
#                |             | Cleaned up Exception Handling               |
#                |             | Remove b' in favor of .encode and .decode   |
#                |             | Added aircheck_sqllite method               |
#                |             | Added Min/Max Time Outs                     |
# ----------------------------------------------------------------------------
# Kris Armstrong | May 31 2017 | Added FileI/O for exception                 |
# ----------------------------------------------------------------------------
# Kris Armstrong | May 30 2017 | Moved Vars to Global                        |
# ----------------------------------------------------------------------------
# Kris Armstrong | May 25 2017 | Added Parser Function                       |
# ----------------------------------------------------------------------------
# Kris Armstrong | May 1 2017  | iPerf Discovery was Born                    |
# ----------------------------------------------------------------------------
#
