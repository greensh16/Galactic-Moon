# Moon tracker for the Pimoroni Galactic Unicon with Pi Pico W

Code to track and display the movement of the Moon (and other Celestial bodies) on a Galactic Unicorn led matrix.

<img src="https://github.com/greensh16/Galactic-Moon/assets/20108650/97e9f2e9-ab1d-4d9c-9ad3-bd605cca9bcd" alt="Image" width="900">

The moon is represented by 4 white dots that vary in brightness based on the moon's phase. The user pointing north is represented by a green dot.

## How to use

- Copy all the python files to your Galactic Unicon using Thonny (or whatever you use).
- Add a secrets.py script to contain your Wifi SSID and password, also add your latitude and longitude.
- This code was created to track the moon in the Southern Hemsiphere, you my need to change; 1 - The azimuth extents near the top of main.py. 2 - The corrections for the azimuth near the end of moon_position() in moon.py

## TODO

- Track the Sun
- ~~Track the Moon's brightness and maybe phase~~ ✓ **COMPLETED** - Moon brightness now tracked and displayed
- Track some planets
- ~~Change the background colour of the display to match the time of day~~ ✓ **COMPLETED** - Background now changes: blue (day), black (night), orange (evening/twilight)

## Dependencies
- ```galactic```: Library for the Pimoroni Galactic Unicorn display.
- ```picographics```: Graphics library for displays.
- ```math```: For math calculations and functions.
- ```network```: For connecting to Wi-Fi.
- ```ntptime```: For syncing time.
- ```utime```: to set the Pico's clock
