import json
import machine
import rp2
import time
import uasyncio

from mqtt_as import MQTTClient, config

with open('config.json') as configfile:
    cfg = json.loads(configfile.read())

CLIENT_ID = cfg['client_id']
SSID = cfg['ssid']
PW = cfg['pw']
BROKER = cfg['broker']
TOPIC = cfg['topic']
COUNTRY = cfg['country']

# Input pins
p2 = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
p3 = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
p4 = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
p5 = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

# Output pins
p6 = machine.Pin(6, machine.Pin.OUT, value=0)
p7 = machine.Pin(7, machine.Pin.OUT, value=1)
p8 = machine.Pin(8, machine.Pin.OUT, value=1)
p9 = machine.Pin(9, machine.Pin.OUT, value=1)

led = machine.Pin("LED", machine.Pin.OUT)

if COUNTRY:
    rp2.country(COUNTRY)

current_level = 0

def got_message(topic, msg, retained):
    try:
        body = json.loads(msg)
        level = int(body['level'])
        if not 0 <= level <= 3:
            level = 0
        if level != current_level:
            set_level(level)
    except:
        pass
    
async def conn_han(client):
    await client.subscribe(TOPIC)

config['ssid'] = SSID
config['wifi_pw'] = PW
config['server'] = BROKER
config['subs_cb'] = got_message
config['connect_coro'] = conn_han

client = MQTTClient(config)

def get_dial_value():
    if p2.value() == 0:
        return 3
    elif p3.value() == 0:
        return 2
    elif p4.value() == 0:
        return 1
    else:
        return 0
    
async def publish_level(level):
    try:
        message = json.dumps({'level': level, 'sender': CLIENT_ID})
        await client.publish(TOPIC, message, retain=True)
    except Exception as e:
        pass

def set_level(level):
    global current_level
    current_level = level
    p6.value(level != 0)
    p7.value(level != 1)
    p8.value(level != 2)
    p9.value(level != 3)

async def check_dial():
    dial_value = get_dial_value()
    set_level(dial_value)
    
    while True:
        new_dial_value = get_dial_value()
        if new_dial_value != dial_value:
            dial_value = new_dial_value
            set_level(new_dial_value)
            await publish_level(new_dial_value)
        await uasyncio.sleep_ms(200)
        
async def connect():
    while True:
        try:
            await client.connect()
            while True:
                await uasyncio.sleep_ms(1000 * 1000)
        except OSError:
            await uasyncio.sleep_ms(10 * 1000)

async def blink_led():
    while True:
        led.off()
        await uasyncio.sleep_ms(3000)
        led.on()
        await uasyncio.sleep_ms(50)

async def main():
    await uasyncio.gather(check_dial(), connect(), blink_led())
    
uasyncio.run(main())

# Seems we broke out of our loop somehow, let's blink the LED angrily.
while True:
    led.off()
    time.sleep(100)
    led.on()
    time.sleep(100)
