import os
import random
import time

import machine
import neopixel
from machine import Timer, Pin

import BG77
import config


def is_full():
    if get_car_num() <= config.CAPACITY:
        return False
    else:
        return True


def reset_timer():
    print("Timer reset")
    timer.init(mode=Timer.PERIODIC, period=config.RADIO_INFO_PERIOD * 1000, callback=send_radio_information)


def spz_gen():
    kraje = "ABCDEHJKLMPSTUZ"
    pismena = "0123456789ABCDEFHJKLMNPRSTUVXYZ"

    znak1 = str(random.randint(1, 9))
    znak2 = random.choice(kraje)
    znak3 = random.choice(pismena)
    znak4 = "%04d" % random.randint(1, 9999)

    return f"{znak1}{znak2}{znak3}{znak4}"


def vjezd():
    global last_msg
    reset_timer()
    RGB_LEDS[0] = (50, 50, 0, 0)
    RGB_LEDS.write()
    spz = spz_gen()
    save_to_local(spz)
    time.sleep(3)
    last_msg = "o" + spz
    send_away("i", spz)


def vyjezd():
    global last_msg
    reset_timer()
    RGB_LEDS[1] = (0, 0, 50, 0)
    RGB_LEDS.write()
    spz = read_from_local()
    time.sleep(3)
    if spz is None:
        return
    last_msg = "o" + spz
    send_away("o", spz)


def get_car_num():
    with open("spz.txt", "r") as file:
        return len(file.readlines())+1
    return None

def send_radio_information(timer):
    data = module.sendCommand("AT+QCSQ\r\n")
    if "+QCSQ:" in data:
        try:
            parts = data.split(',')

            sysmode = str(parts[0].split('"')[1])
            rssi = int(parts[1])
            rsrp = int(parts[2])
            sinr = round(float((int(parts[3]) / 5) - 20))
            rsrq = str(parts[4].split("\r")[0])

            print("Radio information", (sysmode, rssi, rsrp, sinr, rsrq))

            send_away("s", f"{rsrp},{sinr},{get_car_num()}")

        except Exception as e:
            print("Parse error:", e)
    else:
        print("Bad response to QCSQ")


def save_to_local(spz):
    with open("spz.txt", "a") as dst:
        dst.write(spz + "\n")
    print("Saving SPZ to spz.txt")


def read_from_local():
    with open("spz.txt", "r") as src:
        lines = src.readlines()
    if not lines:
        return None
    spz = random.choice(lines)
    lines.remove(spz)
    os.remove("spz.txt")
    with open("spz.txt", "a") as dst:
        for line in lines:
            dst.write(line)
    print("Reading SPZ from spz.txt")
    return spz.strip()


def send_away(flag, value):
    print("Sending message:", flag + value)
    if socket.send(flag + value, 2):
        print("Send successful")
    else:
        print("Send failed")


previous_ticks = 0

timer = Timer(-1)

VJEZD_BTN = Pin(28, Pin.IN)
VYJEZD_BTN = Pin(6, Pin.IN)

last_msg = ""

RGB_LEDS = neopixel.NeoPixel(Pin(16), 3, bpp=4)

RGB_LEDS[0] = (0, 0, 0, 0)
RGB_LEDS[1] = (0, 0, 0, 0)
RGB_LEDS[2] = (0, 0, 0, 0)

RGB_LEDS.write()

pon_trig = Pin(9, Pin.OUT)
pon_trig.value(1)
time.sleep(0.3)
pon_trig.value(0)

bg_uart = machine.UART(0, baudrate=115200, tx=Pin(0), rxbuf=256, rx=Pin(1), timeout=0, timeout_char=1)

while True:
    try:
        module = BG77.BG77(bg_uart, verbose=True, radio=False)
        break
    except OSError:
        print("Module is not ready yet")
        time.sleep(0.5)

time.sleep(0.3)
module.sendCommand("AT+QURCCFG=\"urcport\",\"uart1\"\r\n")
time.sleep(0.1)
module.sendCommand("AT+CPSMS=0\r\n")
time.sleep(2)
module.sendCommand("AT+CEDRXS=0\r\n")
time.sleep(3)

# Automatic NB-IoT/LTE CAT-M selection, LTE CAT-M preferred
# module.setRATType(2)  # does not work
auto_handover = module.sendCommand("AT+QCFG=\"iotopmode\",2,1\r\n")
if "OK" in auto_handover:
    print("RAT type set successfully")
else:
    print("RAT type setting failed")

# module.sendCommand("AT+QCFG=\"band\",0x0,0x80084,0x80084,1\r\n")
module.setRadio(1)
module.setAPN(config.APN)

module.setOperator(BG77.COPS_MANUAL, config.OPERATOR)

while not module.isRegistered():
    print("Not registered yet")
    time.sleep(0.5)

module.sendCommand("AT+QCSCON=1\r\n")

print("Device Ready")

reset_timer()

socket_open, socket = module.socket(BG77.AF_INET, BG77.SOCK_DGRAM)
if socket_open:
    socket.settimeout(1)
    socket.connect(config.IPV4, config.PORT)
    print("Socket Open")
else:
    print("Error occurred while opening socket")

while True:
    if previous_ticks <= time.ticks_ms() - config.CHECK_INTERVAL:
        if not VYJEZD_BTN.value():
            vyjezd()
        elif not VJEZD_BTN.value() and not is_full():
            vjezd()
        elif not is_full():
            RGB_LEDS[0] = (0, 50, 0, 0)
        else:
            RGB_LEDS[0] = (50, 0, 0, 0)
        # vyjezd vzdy povolen
        RGB_LEDS[1] = (0, 50, 0, 0)
        RGB_LEDS.write()
        previous_ticks = time.ticks_ms()

    try:
        if bg_uart.any():
            time.sleep(.01)
            data = bg_uart.read()
            # print(data)
            if data != None:
                # data = data.decode()
                # print(data)
                if 0xff in data:
                    m = bytearray(data)
                    for i in range(len(m)):
                        if m[i] == 0xff:
                            m[i] = 0
                    data = bytes(m)
                data = str(data, 'ascii')
                data = data.strip('\r\n')
                data_split = data.split("\n")
                for line in data_split:
                    if line == "\r\n":
                        continue
                    print(f"{time.ticks_ms()}: <- {line.strip('\r\n')}")
        time.sleep(.1)
    except KeyboardInterrupt:
        socket.close()
        break
    except:
        pass
