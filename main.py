# Created by Sam Green
# Date: 17-05-2024

# This code uses the users current time/latitude/longitude and calculates the moons altitude and 
# azimuth (moon.py). These 2 values are then used to plot the position of the moon on a Galactic Unicorn using
# the inbuilt Raspberry Pi Pico W.

# The graphics part of this code was built for Pimoroni's pirate-brand MicroPython.

# The ntptime library is used to set the Pico at the correct time. For this to work we need to connect to the internet
# You need to create a secrets.py script and place your SSID and its password in there. I've aslo added my 
# latitude and longitude in there too.


import machine, time, network, ntptime, utime
from galactic import GalacticUnicorn
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN as DISPLAY
from moon import MoonPosition
import secrets

# overclock to 200Mhz
machine.freq(200000000)

# The calculations in map_moon_position() are assuming the user is in the southern hemisphere, you'll need
# to modify the azimuth extents for your region.
# azimuth extents for my location in southern hemisphere:
az_east = 125.0
az_west = 235.0

# Initialize the Galactic Unicorn and graphics surface
galactic = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY)

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.ssid, secrets.password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

try:
    ip = connect()
except KeyboardInterrupt:
    machine.reset()

# Set the pico to the right time using an ntp server.
ntptime.settime()

# Function to map altitude and azimuth to display coordinates
def map_moon_position(altitude, azimuth):
    # Ensure altitude is within the valid range
    if 0 < altitude < 90:
        # Normalize altitude (0° to 90°) to y-axis (10 to 0 pixels)
        y = int(10 - (altitude / 90.0 * 10))
    else:
        # Invalid altitude value
        return None, None
    
    # Normalize azimuth
    if 0 <= azimuth <= az_east:
        # Map az_east (max East) to 0 (leftmost), 0° (North) to 26 (center)
        x = int((az_east - azimuth) / az_east * 26)
    elif az_west <= azimuth <= 359:
        # Map 359° (slightly west) to 27, az_west (max West) to 52 (rightmost)
        x = int((azimuth - az_west) / (359 - az_west) * 26) + 26
    else:
        # Invalid azimuth value
        return None, None
    
    return x, y

# Function to draw the moon on the display
def draw_moon(altitude, azimuth, brightness):
    # Get the moon's position in display coordinates
    x, y = map_moon_position(altitude, azimuth)
    
    # Check if the position is valid (i.e., not None)
    if x is not None and y is not None:
        # Calculate brightness-based color intensity (brightness ranges from 0.0 to 1.0)
        # Scale brightness to a useful range for visibility (minimum 20% to ensure moon is always visible)
        intensity = int(max(20, brightness * 255))
        
        # Set the pen color based on brightness
        moon_pen = graphics.create_pen(intensity, intensity, intensity)
        graphics.set_pen(moon_pen)
        
        # Draw the moon as 4 adjacent pixels
        graphics.pixel(x, y)
        graphics.pixel(x+1, y)
        graphics.pixel(x, y-1)
        graphics.pixel(x+1, y-1)
        
        # Update the display
        galactic.update(graphics)

# Loop to update the moon's position every 10 minutes
while True:

    # Clear the display
    graphics.set_pen(graphics.create_pen(0, 0, 0))
    graphics.clear()
    # Add a pixel for the observer at North
    graphics.set_pen(graphics.create_pen(0, 255, 0))
    graphics.pixel(26, 10)
    galactic.update(graphics)

    # get the current time
    current_time = utime.localtime()
    date = utime.mktime(current_time)

    # Calculate the moon's position and brightness
    azimuth, altitude, distance, brightness = MoonPosition().moon_position(date, secrets.latitude, secrets.longitude)
    #print(f"Moon Altitude: {altitude:.2f} degrees, Azimuth: {azimuth:.2f} degrees, Brightness: {brightness:.2f}")

    # Draw the moon
    draw_moon(altitude, azimuth, brightness)

    # Wait for 10 minutes before updating again (600 seconds)
    utime.sleep(600)