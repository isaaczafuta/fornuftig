# fornuftig
Raspberry Pi Pico W Micropython Firmware for Ikea Fornuftig Air Purifier

Open up yout Fornuftig, and cut the 4 active legs on the rotary switch. Wire the rotary legs to gpio 2, 3, 4, and 5. Now wire gpios 9, 8, 7, and 6 to the respective leads where the legs used to be.

Update the config.json, and add it and main.py to your pi pico w.

The pico w will listen on mqtt messages, for a json 'level' field, 0 being off, 3 being fully on. Turning the dial will override the mqtt setting and set a new level.