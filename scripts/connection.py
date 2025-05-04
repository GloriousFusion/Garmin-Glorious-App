from scripts.settings import ENV_KDE, RETRY_TIME

import pymtp.main, pymtp.errors

import subprocess
import time

### KDE Patch (killing kiod5 daemon allows mtp functionality) ###
def kill_kiod5():
    try:
        subprocess.run(["pkill", "kiod5"], check=True)
    except subprocess.CalledProcessError:
        print(f"Device is not connected or wrong environment is activated (change in settings).")

def connect(status_callback=None):
    try:
        device = pymtp.main.MTP()

        if status_callback:
            status_callback("Connecting")
        print("Connecting...")
        device.connect()

        manufacturer = device.get_manufacturer()
        if manufacturer.decode() == "Garmin":
            if status_callback:
                status_callback("Connected (Press To Disconnect)")
            print("Connected!")
            return device
    except pymtp.errors.NoDeviceConnected:
        try:
            print(f"Device not connected or busy, retrying in {RETRY_TIME} seconds...")
            if ENV_KDE:
                kill_kiod5()
            time.sleep(RETRY_TIME)
            return connect()
        except KeyboardInterrupt:
            print("Quiting...")
            quit()
    except Exception as e:
        print(f"Error: {e}")