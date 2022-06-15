# battery-monitoring.py

A simple script, running in a loop, checking the current battery charge level. Optionally it will warn the user
when a given threshold is reached by sending a desktop notification. Optionally it will either alert the user
again, suspend or shutdown the computer when a given critical threshold is reached.

## Requirements

1. [dbus-python](https://pypi.org/project/dbus-python/)

## Usage

    usage: battery-monitoring.py [-h] [-w WARN] [-c CRIT] [-s SLEEP]
                                 [-a {notify,suspend,poweroff}]
                                 path
    
    positional arguments:
      path                  the absolute path to a battery device in Linux power
                            supply class e.g. /sys/class/power_supply/BAT1
    
    options:
      -h, --help            show this help message and exit
      -w WARN, --warn WARN  (optional) limit value, of the battery in percent,
                            below which an alarm/notification is triggered
      -c CRIT, --crit CRIT  (optional) limit value, of the battery in percent,
                            below which the action is triggered
      -s SLEEP, --sleep SLEEP
                            (optional) set the time to sleep between status checks
                            in seconds
      -a {notify,suspend,poweroff}, --action {notify,suspend,poweroff}
                            (optional) action to execute when crit threshold is
                        undercut