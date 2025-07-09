# Created by Sam Green
# Date: 17-05-2024

# This code uses the users current time/latitude/longitude and calculates the moons altitude and 
# azimuth (moon.py). These 2 values are then used to plot the position of the moon on a Galactic Unicorn using
# the inbuilt Raspberry Pi Pico W.

# The graphics part of this code was built for Pimoroni's pirate-brand MicroPython.

# The ntptime library is used to set the Pico at the correct time. For this to work we need to connect to the internet
# You need to create a secrets.py script and place your SSID and its password in there. I've aslo added my 
# latitude and longitude in there too.


import machine, time, network, ntptime, utime, math
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

# Function to get background color based on time of day
def get_background_color(current_time, lat, lng):
    """
    Determines background color based on sun position (time of day).
    
    Parameters:
    current_time: current time in seconds since epoch
    lat: latitude in degrees
    lng: longitude in degrees
    
    Returns:
    tuple: (r, g, b) color values for background
    """
    # Calculate sun position using existing MoonPosition class
    moon_calc = MoonPosition()
    dt = moon_calc.to_days_J2000(current_time)
    
    # Get sun position - we need sun altitude to determine time of day
    sun_ra, sun_dec = moon_calc.sun_position(dt)
    
    # Calculate sun altitude using similar logic to moon calculation
    lng_ra = math.radians(-lng)
    lat_ra = math.radians(lat)
    
    # Calculate the hour angle of the sun
    H = moon_calc.sidereal_time(dt, lng_ra) - sun_ra
    
    # Normalize hour angle to [-π, π] range
    while H > math.pi:
        H -= 2 * math.pi
    while H < -math.pi:
        H += 2 * math.pi
    
    sun_alt_rad = math.asin(math.sin(lat_ra) * math.sin(sun_dec) + math.cos(lat_ra) * math.cos(sun_dec) * math.cos(H))
    sun_alt_deg = math.degrees(sun_alt_rad)
    
    # Determine time of day based on sun altitude
    if sun_alt_deg > 0:
        # Day - sun is above horizon (blue background)
        return (0, 0, 50)  # Dim blue
    elif sun_alt_deg < -18:
        # Night - astronomical twilight (black background)
        return (0, 0, 0)   # Black
    else:
        # Evening/twilight - sun is below horizon but not fully dark (yellow/orange background)
        return (50, 25, 0)  # Dim orange/yellow

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
    # get the current time
    current_time = utime.localtime()
    date = utime.mktime(current_time)

    # Get background color based on time of day
    bg_r, bg_g, bg_b = get_background_color(date, secrets.latitude, secrets.longitude)
    
    # Clear the display with time-based background color
    graphics.set_pen(graphics.create_pen(bg_r, bg_g, bg_b))
    graphics.clear()
    
    # Add a pixel for the observer at North
    graphics.set_pen(graphics.create_pen(0, 255, 0))
    graphics.pixel(26, 10)
    galactic.update(graphics)

    # Calculate the moon's position and brightness
    azimuth, altitude, distance, brightness = MoonPosition().moon_position(date, secrets.latitude, secrets.longitude)
    #print(f"Moon Altitude: {altitude:.2f} degrees, Azimuth: {azimuth:.2f} degrees, Brightness: {brightness:.2f}")

    # Draw the moon
    draw_moon(altitude, azimuth, brightness)

    # Wait for 10 minutes before updating again (600 seconds)
    utime.sleep(600)