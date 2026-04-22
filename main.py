import machine
import time
import neopixel
import uselect, sys
import BG77
import _thread
import os
import random
from machine import Timer, Pin

def reset_timer():
    print("Timer reset")
    timer.init(mode=Timer.PERIODIC, period=20000, callback=send_radio_information)

def spz_gen():
    kraje = "ABCDEHJKLMPSTUZ"
    pismena = "0123456789ABCDEFHJKLMNPRSTUVXYZ"
    
    znak1 = str(random.randint(1, 9))
    znak2 = random.choice(kraje)
    znak3 = random.choice(pismena)
    znak4 = "%04d" % random.randint(1, 9999)
    
    return f"{znak1}{znak2}{znak3}{znak4}"

def check_vjezd(timer):
    if RGB_LEDS[1] != (0, 50, 0, 0):
        check_timer.init(mode=Timer.ONE_SHOT, period=500, callback=check_vjezd)
    else:
        vjezd()

def check_vyjezd(timer):
    if RGB_LEDS[0] != (0, 50, 0, 0):
        check_timer.init(mode=Timer.ONE_SHOT, period=500, callback=check_vyjezd)
    else:
        vyjezd()

def vjezd():
    reset_timer()
    RGB_LEDS[0] = (50, 0, 0, 0)
    RGB_LEDS.write()
    spz = spz_gen()
    save_to_local(spz)
    time.sleep(3)
    print("i" + spz)

def vyjezd():
    reset_timer()
    RGB_LEDS[1] = (0, 0, 50, 0)
    RGB_LEDS.write()
    spz = read_from_local()
    time.sleep(3)
    print("o" + spz)

def send_radio_information(timer):
    print("sRADIOINF")
    
def save_to_local(spz):
    with open("spz.txt", "a") as dst:
        dst.write(spz+"\n")
    print("Saving SPZ to spz.txt")

def read_from_local():
    with open("spz.txt", "r") as src:
        lines = src.readlines()
    if lines == []:
        return "0A00000"
    spz = random.choice(lines)
    lines.remove(spz)
    os.remove("spz.txt")
    with open("spz.txt", "a") as dst:
        for line in lines:
            dst.write(line)
    print("Reading SPZ from spz.txt")
    return spz.strip()

def core2_task():
    sel0 = Pin(2, Pin.OUT)
    sel1 = Pin(3, Pin.OUT)

    sel0.value(0)
    sel1.value(1)

    adc = machine.ADC(0)

    uart = machine.UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
    VREF=3.3
    while True:
        read_adc = adc.read_u16()
        '''
        if read_adc > 65000:
            sel0.value(1)
        elif read_adc < 42000:
            sel0.value(0)
        '''
        #print(str(read_adc))
        uart.write(str(time.ticks_ms())+ "," + str(read_adc)+"\r")
        time.sleep(0.001)
    
    

spoll=uselect.poll()
spoll.register(sys.stdin,uselect.POLLIN)

timer = Timer(-1)
reset_timer()

check_timer = Timer(-1)

VJEZD_BTN = Pin(28,Pin.IN)
VYJEZD_BTN = Pin(6,Pin.IN)
VJEZD_BTN.irq(trigger=Pin.IRQ_FALLING, handler=check_vjezd)
VYJEZD_BTN.irq(trigger=Pin.IRQ_FALLING, handler=check_vyjezd)

RGB_LEDS = neopixel.NeoPixel(Pin(16), 3, bpp=4)

RGB_LEDS[0] = (0,0,0,0)
RGB_LEDS[1] = (0,0,0,0)
RGB_LEDS[2] = (0,0,0,0)

RGB_LEDS.write()

pon_trig = Pin(9,Pin.OUT)




# machine.UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5), timeout=200, timeout_char=5)
bg_uart = machine.UART(0, baudrate=115200, tx=Pin(0), rxbuf=256, rx=Pin(1), timeout = 0, timeout_char=1)

bg_uart.write(bytes("AT\r\n","ascii"))
print(bg_uart.read(10))


module = BG77.BG77(bg_uart, verbose=True, radio=False)

time.sleep(0.3)
module.sendCommand("AT+QURCCFG=\"urcport\",\"uart1\"\r\n")
time.sleep(0.1)
module.sendCommand("AT+CPSMS=0\r\n")
time.sleep(2)
module.sendCommand("AT+CEDRXS=0\r\n")
time.sleep(3)

module.sendCommand("AT+QCFG=\"band\",0x0,0x80084,0x80084,1\r\n")
module.setRadio(1)
module.setAPN("lpwa.vodafone.iot")

#module.setOperator(BG77.COPS_MANUAL, BG77.Operator.CZ_VODAFONE)




def read1():
    return(sys.stdin.read(1) if spoll.poll(0) else None)

def readline():
    c = read1()
    buffer = ""
    while c != None:
        buffer += c
        c = read1()
    return buffer


def waitForCEREG():
    data_out = ""
    while True:
        data_tmp = bg_uart.read(1)
        if data_tmp:
            data_out = data_out + str(data_tmp, 'ascii')
        if "+CEREG: 5" in data_out:
            time.sleep(.01)
            data_tmp = bg_uart.read()
            data_out = data_out + str(data_tmp, 'ascii')
            return

#waitForCEREG()
print("OUT")
'''
print(f"Init: {time.ticks_ms()}")
while True:
    data = bg_uart.read()
    print(f"{time.ticks_ms()} {data}")
    time.sleep(1)
'''


module.sendCommand("AT+QCSCON=1\r\n")

#second_thread = _thread.start_new_thread(core2_task, ())

print("Terminal Ready")


while True:
    RGB_LEDS[0] = (0, 50, 0, 0)
    RGB_LEDS[1] = (0, 50, 0, 0)
    RGB_LEDS.write()
    
    
    try:
        data = readline()
        
        

        
        if bg_uart.any():
            time.sleep(.01)
            data = bg_uart.read()
            print(data)
        time.sleep(.1)
    except KeyboardInterrupt:
        break
    except:
        pass






