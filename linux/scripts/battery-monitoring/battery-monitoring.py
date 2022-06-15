# This is a Python script that monitors the notebook's battery level, to alert the user when the battery runs low and to
# suspend or power down the notebook when a certain threshold is reached.

# import the recommended command-line parsing module in the Python standard library
import argparse
import os
import sys
# requires dbus-python package
import dbus
import time

# Parse the command line arguments
def evaluate_params():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="the absolute path to a battery device in Linux power supply class e.g. "
                        "/sys/class/power_supply/BAT1")
    parser.add_argument("-w", "--warn", help="(optional) limit value, of the battery in percent, below which an "
                        "alarm/notification is triggered", type=float)
    parser.add_argument("-c", "--crit", help="(optional) limit value, of the battery in percent, below which the action"
                        " is triggered", type=float)
    parser.add_argument("-s", "--sleep", help="(optional) set the time to sleep between status checks in seconds",
                        type=int)
    parser.add_argument("-a", "--action", choices=['notify', 'suspend', 'poweroff'], help="(optional) action to execute"
                        " when crit threshold is undercut")
    return parser.parse_args()


def send_notification(title, body, icon):
    bus_name = "org.freedesktop.Notifications"
    object_path = "/org/freedesktop/Notifications"
    interface = bus_name

    notify = dbus.Interface(dbus.SessionBus().get_object(bus_name, object_path), interface)
    notify.Notify("battery-monitoring.py", 0, icon, title, body, "", "", -1)


if __name__ == '__main__':
    args = evaluate_params()
    charge_full = 0.0
    charge_now = 0.0
    was_above_warn = True
    was_above_crit = True

    while True:
        # try to open the files providing the battery status
        try:
            charge_full_file = open(args.path + "/charge_full", "r", newline=None)
            charge_full = float(charge_full_file.readlines().pop())
            charge_now_file = open(args.path + "/charge_now", "r", newline=None)
            charge_now = float(charge_now_file.readlines().pop())
        except OSError:
            print("Failed to open files in \"" + args.path + "\".")
            sys.exit(1)

        # check is valid values were returned
        if charge_full <= 0.0 or charge_now <= 0.0 or charge_now > charge_full:
            print("The Linux kernel power supply subsystem reported impossible values for: " + args.path + ". The values"
                  " reported were: charge_full: " + str(charge_full) + ", charge_now: " + str(charge_now) + ".")
            sys.exit(1)

        # calculate how full the battery is
        charge_in_percent = charge_now / charge_full * 100

        print(charge_in_percent)

        # trigger effects of charge falling below thresholds
        if args.warn:
            if charge_in_percent < float(args.warn):
                if was_above_warn:
                    send_notification("Battery Warning", "Battery at: " + str("%.0f" % charge_in_percent) + "%!", "")
                    was_above_warn = False
            if charge_in_percent >= float(args.warn):
                was_above_warn = True
        if args.crit:
            if charge_in_percent < float(args.crit):
                if was_above_crit:
                    if args.action == 'notify':
                        send_notification("Battery Critical", "Battery at: " + str("%.0f" % charge_in_percent) + "%!",
                                          "")
                    if args.action == 'poweroff':
                        os.system('systemctl poweroff')
                    if args.action == 'suspend':
                        os.system('systemctl suspend')
                    was_above_crit = False
            if charge_in_percent >= float(args.crit):
                was_above_crit = True

        charge_full_file.close()
        charge_now_file.close()

        if args.sleep:
            time.sleep(args.sleep)
        else:
            time.sleep(15)
