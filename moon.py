# Created by Sam Green
# Date: 17-05-2024

# This code calculates the position of the moon in the sky at any given time, latitude, and longitude.
# The position of the observer is assumed to be in the Southern Hemisphere, if you are 
# in the Northern Hemisphere then you my need to tweek the end of moon_position().
# The various equations in this code are based on Vladimir Agafonkin's https://github.com/mourner/suncalc and 
# various astronomical sites.


import math

class MoonPosition:
    def __init__(self):
        """
        Initializes the MoonPosition class with necessary constants.
        """
        self.days_to_secs = 60 * 60 * 24 # Days to seconds
        self.obl_e = math.radians(23.4397) # obliquity of the Earth
    
    def to_days_J2000(self, date):
        """
        Converts the given date to the number of days since January 1, 2000.

        Parameters:
        date (float): The date in seconds since January 1, 1970.

        Returns:
        float: The number of days since January 1, 2000.
        """
        julian_date = date / self.days_to_secs - 0.5 + 2440588
        return julian_date - 2451545

    def sidereal_time(self, d, lw):
        """
        Calculates the sidereal time.

        Parameters:
        d (float): Number of days since January 1, 2000.
        lw (float): Longitude in radians.

        Returns:
        float: Sidereal time in radians.
        """
        sid_t = math.radians((280.16 + 360.9856235 * d)) - lw
        return sid_t

    def sun_position(self, d):
        """
        Calculates the sun's position for brightness calculations.

        Parameters:
        d (float): Number of days since January 1, 2000.

        Returns:
        tuple: (right_ascension, declination) in radians.
        """
        # Mean longitude of the sun
        l_sun = math.radians(280.460 + 0.9856474 * d)
        
        # Mean anomaly of the sun
        g_sun = math.radians(357.528 + 0.9856003 * d)
        
        # Ecliptic longitude of the sun with perturbation
        lambda_sun = l_sun + math.radians(1.915 * math.sin(g_sun) + 0.020 * math.sin(2 * g_sun))
        
        # Right ascension of the sun
        ra_sun = math.atan2(math.cos(self.obl_e) * math.sin(lambda_sun), math.cos(lambda_sun))
        
        # Declination of the sun
        dec_sun = math.asin(math.sin(self.obl_e) * math.sin(lambda_sun))
        
        return ra_sun, dec_sun

    def moon_brightness(self, moon_ra, moon_dec, sun_ra, sun_dec):
        """
        Calculates the moon's brightness (illuminated fraction).

        Parameters:
        moon_ra (float): Moon's right ascension in radians.
        moon_dec (float): Moon's declination in radians.
        sun_ra (float): Sun's right ascension in radians.
        sun_dec (float): Sun's declination in radians.

        Returns:
        float: Illuminated fraction of the moon (0.0 to 1.0).
        """
        # Calculate the phase angle between Moon and Sun as seen from Earth
        phase_angle = math.acos(
            math.sin(sun_dec) * math.sin(moon_dec) + 
            math.cos(sun_dec) * math.cos(moon_dec) * math.cos(sun_ra - moon_ra)
        )
        
        # Calculate illuminated fraction using standard formula
        # This gives the fraction of the moon that is illuminated (0 = new moon, 1 = full moon)
        illuminated_fraction = (1 + math.cos(phase_angle)) / 2
        
        return illuminated_fraction

    def moon_position(self, date, lat, lng):
        """
        Calculates the moon's position and brightness for a given date and location.

        Parameters:
        date (float): Date in seconds since January 1, 1970.
        lat (float): Latitude in degrees.
        lng (float): Longitude in degrees.

        Returns:
        tuple: azimuth (float) in degrees, altitude (float) in degrees, 
               distance to the moon in km (float), and brightness (float) 0.0-1.0.
        """
        lng_ra  = math.radians(-lng)
        lat_ra = math.radians(lat)
        dt   = self.to_days_J2000(date)

        l_moon = math.radians(218.316 + 13.176396 * dt) #  Mean longitude of the moon
        mean_an = math.radians(134.963 + 13.064993 * dt) # Mean anomaly of the moon
        dist_m = math.radians(93.272 + 13.229350 * dt)  # Mean distance of the moon from its ascending node
        
        long_pert  = l_moon + math.radians(6.289 * math.sin(mean_an))  # Longitude with perturbation
        lat_pert  = math.radians(5.128 * math.sin(dist_m)) # Latitude with perturbation
        moon_dist_pert = 385001 - 20905 * math.cos(mean_an) # Distance to the moon in km, with perturbation

        # Right ascension
        ra = math.atan2(math.sin(long_pert) * math.cos(self.obl_e) - math.tan(lat_pert) * math.sin(self.obl_e), math.cos(long_pert))
        # Declination
        dec = math.asin(math.sin(lat_pert) * math.cos(self.obl_e) + math.cos(lat_pert) * math.sin(self.obl_e) * math.sin(long_pert))

        # Calculate the altitude
        H = self.sidereal_time(dt, lng_ra) - ra
        alt_rad = math.asin(math.sin(lat_ra) * math.sin(dec) + math.cos(lat_ra) * math.cos(dec) * math.cos(H))
        alt_deg = math.degrees(alt_rad)

        # Calculate the azimuth
        az_rad = math.atan2(math.sin(H), math.cos(H) * math.sin(lat_ra) - math.tan(dec) * math.cos(lat_ra))
        az_deg = math.degrees(az_rad)
        az_deg += 180

        if az_deg < 0:
            az_deg += 360
        if az_deg > 360:
            az_deg -= 360

        # Calculate sun position for brightness calculation
        sun_ra, sun_dec = self.sun_position(dt)
        
        # Calculate moon brightness
        brightness = self.moon_brightness(ra, dec, sun_ra, sun_dec)

        return az_deg, alt_deg, moon_dist_pert, brightness

