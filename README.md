# Moon tracker for the Pimoroni Galactic Unicon with Pi Pico W

Code to track and display the movement of the Moon (and other Celestial bodies) on a Galactic Unicorn led matrix.

## How to use

- Copy all the python files to your Galactic Unicon using Thonny (or whatever you use).
- Add a secrets.py scritp to contain your Wifi SSID and password, also add your latitude and longitude.
- This code was created to track the moon in the Southern Hemsiphere, you my need to change; 1 - The azimuth extents near the top of main.py. 2 - The corrections for the azimuth near the end of moon_position() in moon.py

## TODO

- Track the Sun
- Track the Moon's brightness and maybe phase
- Track some planets
- Change the background colour of the display to match the time of day.

## Dependencies
- ```galactic```: Library for the Pimoroni Galactic Unicorn display.
- ```picographics```: Graphics library for displays.
- ```math```: For math calculations and functions.
- ```network```: For connecting to Wi-Fi.
- ```ntptime```: For syncing time.
- ```utime```: to set the Pico's clock
