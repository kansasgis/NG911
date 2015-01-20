'''!Conversion of coordinates from decimal LatLong, UTM and MGRS zone.
   Limitation: doesn't do UPS so do not venture above lat +84 and below Lat -80.
   Contact:
   Python reimplementation including the MGRS conversion by Christian Blouin <cblouin @ cs dal ca>
   Credits:
   C code written by Chuck Gantz- chuck.gantz@globalstar.com
   Original python port for all but MGRS stuff Converted to Python by Russ Nelson <nelson@crynwr.com>
   Reference ellipsoids derived from Peter H. Dana's website-
   http://www.utexas.edu/depts/grg/gcraft/notes/datum/elist.html
   Department of Geography, University of Texas at Austin
   Internet: pdana@mail.utexas.edu
   3/22/95
   Source
   Defense Mapping Agency. 1987b. DMA Technical Report: Supplement to Department of Defense World Geodetic System
   1984 Technical Report. Part I and II. Washington, DC: Defense Mapping Agency
   Interfacing with the Translator
   LonLat
         1 - as a list of decimal longitude, latitude
         2 - Degrees[d], Minute['] [seconds]["] Degrees[d], Minute['] [seconds]["]
   UTM
         1 - 18T 1111111.0 1111111.0
   MGRS
         1 - 18T UF 23232323
         2 - 18TUF23232323
   License and notes:
         This code is distributed under a GPL license (http://www.gnu.org/licenses/gpl.txt for modalities). It was written as
         an utility for a game/simulator project. It is NOT intended for real world navigation, although it probably is good
         enough for as long as you stay firm within the UTM region (Lat -80 to Lat +84). Anyone want to implment the UPS coordinate
         system?
         Please let me know if you use this code, and whether you have found bugs into it!
         CoordConverter/FlatLand -- Interconversion between four geographic coordinate systems: LonLat (decimal),
         LonLat (DMS), UTM and MGRS as well as FlatLand Projection (based on False Eastings).
         Copyright (C) 2007  Christian Blouin
         This program is free software; you can redistribute it and/or modify
         it under the terms of the GNU General Public License as published by
         the Free Software Foundation; either version 2 of the License, or
         (at your option) any later version.
         This program is distributed in the hope that it will be useful,
         but WITHOUT ANY WARRANTY; without even the implied warranty of
         MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
         GNU General Public License for more details.
         You should have received a copy of the GNU General Public License along
         with this program; if not, write to the Free Software Foundation, Inc.,
         51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
         Christian Blouin -- cblouin @ cs dal ca
'''
from math import pi, sin, cos, tan, sqrt, radians, degrees, atan2
import re
from copy import copy
class CoordTranslator:
    def AsMGRS(self, coord, precision = 5, internal = False):
        '''! \brief Returns a MGRS string
             \param precision Number of digits for easting or northing.
        '''
        coord, format = self.ParseCoord(coord)
        if format == 'LL':
            coord = self.LLtoUTM(coord)
            format = 'UTM'
        if format == 'UTM':
            coord = self.UTMtoMGRS(coord)
        if internal:
            return coord
        # string format
        c = coord
        return '%d%s%s%s%s'%( int(c[0]), c[1], c[2], str(c[3])[:precision], str(c[4])[:precision] )
    def AsUTM(self, coord, internal = False):
        '''! \brief Returns a UTM string
        '''
        coord, format = self.ParseCoord(coord)
        if format == 'LL':
            coord = self.LLtoUTM(coord)
            format = 'UTM'
        if format == 'MGRS':
            coord = self.MGRStoUTM(coord)
            format = 'UTM'
        if internal:
            return coord
        # string format
        c = coord
        return '%s %s %d %d'%( c[0], c[1], int(c[2]), int(c[3]))
    def AsLatLong(self, coord, dms = False, internal = False):
        '''! \brief Returns a decimal Lat long pair as a list.
             \param dms forces the output ot be in Deg Min sec
        '''
        coord, format = self.ParseCoord(coord)
        if format == 'MGRS':
            coord = self.MGRStoUTM(coord)
            format = 'UTM'
        if format == 'UTM':
            coord = self.UTMtoLL(coord)
            format = 'LL'
        if internal:
            return coord
        # string format
        c = copy(coord)
        if dms:
            lond = int(c[0])/1
            c[0] -= lond
            c[0] = abs(c[0])
            lonmin = int( c[0]/(60**-1) )
            c[0] -= lonmin * (60**-1)
            lonsec = int(c[0]/(60**-2))
            c[0] -= lonsec * (60**-2)
            if c[0] > 1E-10:
                lonsec += 1
            latd = int(c[1])/1
            c[1] -= latd
            c[1] = abs(c[1])
            latmin = abs(int( c[1]/(60**-1) ))
            c[1] -= latmin * (60**-1)
            latsec = int(c[1]/(60**-2))
            c[1] -= latsec * (60**-2)
            if c[1] > 1E-10:
                latsec += 1
            return '%dd %d\' %d\" %dd %d\' %d\"'%( lond, lonmin, lonsec, latd, latmin, latsec )
        return coord
    def HaversineDistance(self, LL, ll):
        '''! \brief Compute the Haversine distance as per:
              http://en.wikipedia.org/wiki/Haversine_formula
              \param LL, ll Coordinates in any of LL, UTM, MGRS
              Uses the radius as per self.datum (stored in self.a)
        '''
        LL  = self.AsLatLong(LL, internal = True)
        ll = self.AsLatLong(ll, internal = True)
        R = self.a
        dlon = radians(ll[1] - LL[1])
        dlat = radians(ll[0] - LL[0])
        a = (sin(dlat/2))**2 + cos(dlat) * cos(dlat) * (sin(dlon/2)**2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    #
    # Semi-Private Methods, used only to manipulate internal data.
    def ParseCoord(self, coord):
        '''! \brief Turn coord into internal list of tokens, whatever the format. Also return the format.
        '''
        if type(coord) == type([]):
            if len(coord) == 2:
                return coord, 'LL'
            elif len(coord) == 4:
                return coord, 'UTM'
            elif len(coord) == 5:
                return coord, 'MGRS'
        elif type(coord) == type(''):
            # Its a string
            out = []
            if self.re_mgrs.match(coord):
                span = self.re_mgrs.search(coord).span()
                coord = coord[span[0]:span[1]]
                # Zone
                span = re.compile('[0-9]{1,2}').search(coord).span()
                out.append(int(coord[span[0]:span[1]]))
                # Sub-zone
                span = re.compile('[A-X]').search(coord,span[1]).span()
                out.append(coord[span[0]])
                #digraph
                span = re.compile('[A-Z][A-V]').search(coord,span[1]).span()
                out.append(coord[span[0]:span[1]])
                # Easting / Northing forced into the center of lower res squares
                cd = coord[span[1]:].strip()
                E = (cd[:len(cd)/2] + '5555')[:5]
                N = (cd[len(cd)/2:] + '5555')[:5]
                out.append(int(E))
                out.append(int(N))
                return out, 'MGRS'
            elif self.re_utm.match(coord):
                span = self.re_utm.search(coord).span()
                coord = coord[span[0]:span[1]]
                # Zone
                span = re.compile('[0-9]{1,2}').search(coord).span()
                out.append(int(coord[span[0]:span[1]]))
                # Sub-zone
                span = re.compile('[A-X]').search(coord,span[1]).span()
                out.append(coord[span[0]])
                #easting
                span = re.compile('[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?').search(coord,span[1]).span()
                out.append(float(coord[span[0]:span[1]]))
                #northing
                span = re.compile('[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?').search(coord,span[1]).span()
                out.append(float(coord[span[0]:span[1]]))
                return out, 'UTM'
            elif self.re_degdecimal.match(coord):
                x = self.re_degdecimal.match(coord)
                lat = float(x.groups()[0])
                lon = float(x.groups()[2])
                return [lon, lat], 'LL'
            elif self.re_degminosecpair.match(coord):
                # Longitude
                span = self.re_degminosec.search(coord).span()
                lon = self._DegMinSec(coord[span[0]:span[1]])
                if lon[0] < 0.0:
                    mod = -1
                else:
                    mod = 1
                lon = mod * (abs(lon[0]) + lon[1] * 60**-1 + lon[2] * 60**-2)
                # Latitude
                span = self.re_degminosec.search(coord, span[1]).span()
                lat = self._DegMinSec(coord[span[0]:span[1]])
                if lat[0] < 0.0:
                    mod = -1
                else:
                    mod = 1
                lat = mod * (abs(lat[0]) + lat[1] * 60**-1 + lat[2] * 60**-2)
                return [lon, lat], 'LL'
            else:
                return None, 'Invalid'
        else:
            return None, 'Invalid'
    def __init__(self, ellipsoid = 23):
        '''! \brief Create a Translator according to a certain reference Datum. By default, the global datum WGS-84.
        '''
        # Datum
        self.datum = ellipsoid
        # Trivial constants
        self._deg2rad = pi / 180.0
        self._rad2deg = 180.0 / pi
        self._EquatorialRadius = 2
        self._eccentricitySquared = 3
        # Associate latitude and UTM sub-sectors
        self._NSminbound = {}
        self._NSzones = 'CDEFGHJKLMNPQRSTUVWX'
        for i in range(len(self._NSzones)):
            self._NSminbound[self._NSzones[i]] = -80 + (8*i)
        #  id, Ellipsoid name, Equatorial Radius, square of eccentricity
        # first once is a placeholder only, To allow array indices to match id numbers
        self._ellipsoid = [
        [ -1, 'Placeholder', 0, 0],
        [ 1, 'Airy', 6377563, 0.00667054],
        [ 2, 'Australian National', 6378160, 0.006694542],
        [ 3, 'Bessel 1841', 6377397, 0.006674372],
        [ 4, 'Bessel 1841 (Nambia] ', 6377484, 0.006674372],
        [ 5, 'Clarke 1866', 6378206, 0.006768658],
        [ 6, 'Clarke 1880', 6378249, 0.006803511],
        [ 7, 'Everest', 6377276, 0.006637847],
        [ 8, 'Fischer 1960 (Mercury] ', 6378166, 0.006693422],
        [ 9, 'Fischer 1968', 6378150, 0.006693422],
        [ 10, 'GRS 1967', 6378160, 0.006694605],
        [ 11, 'GRS 1980', 6378137, 0.00669438],
        [ 12, 'Helmert 1906', 6378200, 0.006693422],
        [ 13, 'Hough', 6378270, 0.00672267],
        [ 14, 'International', 6378388, 0.00672267],
        [ 15, 'Krassovsky', 6378245, 0.006693422],
        [ 16, 'Modified Airy', 6377340, 0.00667054],
        [ 17, 'Modified Everest', 6377304, 0.006637847],
        [ 18, 'Modified Fischer 1960', 6378155, 0.006693422],
        [ 19, 'South American 1969', 6378160, 0.006694542],
        [ 20, 'WGS 60', 6378165, 0.006693422],
        [ 21, 'WGS 66', 6378145, 0.006694542],
        [ 22, 'WGS-72', 6378135, 0.006694318],
        [ 23, 'WGS-84', 6378137, 0.00669438]]
        # Obscure constant that need to be computed only once
        self.a = self._ellipsoid[self.datum][self._EquatorialRadius]
        self.eccSquared = self._ellipsoid[self.datum][self._eccentricitySquared]
        self.k0 = 0.9996
        self.eccPrimeSquared = (self.eccSquared)/(1-self.eccSquared)
        # Regular expressions to identify coordinates as strings.
        self.re_mgrs = re.compile('[0-9]{1,2}\s?[C-T]\s?[A-Z][A-V]\s?[0-9]{2,10}')
        self.re_utm = re.compile('[0-9]{1,2}\s?[C-T]\s?[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?\s?[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')
        self.re_degminosec = re.compile('[+-]?(\d+)[d]?\s?(\d+)[\']?(\s?\d+(\.\d*)?)?[\"]?') # Only One deg min sec group (secs are optional)
        self.re_degminosecpair = re.compile('^[+-]?(\d+)[d]?\s?(\d+)[\']?(\s?\d+(\.\d*)?)?[\"]?\s([NS]\s)?[+-]?(\d+)[d]?\s?(\d+)[\']?(\s?\d+(\.\d*)?)?[\"]?')
        self.re_degdecimal = re.compile('([+-]?\d+[\.]?\d*)\s([NS]\s)*([+-]?\d+[\.]?\d*)(\s[NS]\s)*')
    def LLtoUTM(self, latlong):
        '''! \brief Conversion from decimal lat and long into a UTM list.
              converts lat/long to UTM coords.  Equations from USGS Bulletin 1532
              East Longitudes are positive, West longitudes are negative.
              North latitudes are positive, South latitudes are negative
              Lat and Long are in decimal degrees
              Written by Chuck Gantz- chuck.gantz@globalstar.com
        '''
        Lat = latlong[0]
        Long = latlong[1]
        #Make sure the longitude is between -180.00 .. 179.9
        LongTemp = (Long+180)-int((Long+180)/360)*360-180 # -180.00 .. 179.9
        # Radians
        LatRad = radians(Lat)
        LongRad = radians(LongTemp)
        # Add half a turn to rescale to 360
        ZoneNumber = int((LongTemp + 180)/6) + 1
        if Lat >= 56.0 and Lat < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0:
            ZoneNumber = 32
        # Special zones for Svalbard
        if Lat >= 72.0 and Lat < 84.0:
            if  LongTemp >= 0.0  and LongTemp <  9.0:ZoneNumber = 31
            elif LongTemp >= 9.0  and LongTemp < 21.0: ZoneNumber = 33
            elif LongTemp >= 21.0 and LongTemp < 33.0: ZoneNumber = 35
            elif LongTemp >= 33.0 and LongTemp < 42.0: ZoneNumber = 37
        LongOrigin = (ZoneNumber - 1)*6 - 180 + 3 #+3 puts origin in middle of zone
        LongOriginRad = radians(LongOrigin)
        #compute the UTM Zone from the latitude and longitude
        #UTMZone = "%d%c" % (ZoneNumber, self._UTMLetterDesignator(Lat))
        N = self.a/sqrt(1-self.eccSquared*sin(LatRad)*sin(LatRad))
        T = tan(LatRad)*tan(LatRad)
        C = self.eccPrimeSquared*cos(LatRad)*cos(LatRad)
        A = cos(LatRad)*(LongRad-LongOriginRad)
        # Huh... I'm not going to touch that...
        M = self.a*((1 -self.eccSquared/4
                - 3* self.eccSquared* self.eccSquared/64
                - 5* self.eccSquared* self.eccSquared* self.eccSquared/256)*LatRad
               - (3* self.eccSquared/8
                  + 3* self.eccSquared* self.eccSquared/32
                  + 45* self.eccSquared* self.eccSquared* self.eccSquared/1024)*sin(2*LatRad)
               + (15* self.eccSquared* self.eccSquared/256 + 45* self.eccSquared* self.eccSquared* self.eccSquared/1024)*sin(4*LatRad)
               - (35* self.eccSquared* self.eccSquared* self.eccSquared/3072)*sin(6*LatRad))
        UTMEasting = (self.k0*N*(A+(1-T+C)*(A**3)/6 + (5-18*T+T*T+72*C-58*self.eccPrimeSquared)*(A**5)/120)+ 500000.0)
        UTMNorthing = (self.k0*(M+N*tan(LatRad)*(A*A/2+(5-T+9*C+4*C*C)*(A**4)/24
                                            + (61
                                               -58*T
                                               +T*T
                                               +600*C
                                               -330*self.eccPrimeSquared)*(A**6)/720)))
        if Lat < 0:
            UTMNorthing = UTMNorthing + 10000000.0; #10000000 meter offset for southern hemisphere
        # Returns as list
        return [ZoneNumber, self._UTMLetterDesignator(Lat), round(UTMEasting), round(UTMNorthing)]
    def UTMtoLL(self, utm):
        '''! \brief Conversion from utm list to LL as list of decimals.
              converts UTM coords to lat/long.  Equations from USGS Bulletin 1532
              East Longitudes are positive, West longitudes are negative.
              North latitudes are positive, South latitudes are negative
              Lat and Long are in decimal degrees.
        '''
        # vars
        northing = utm[3]
        easting = utm[2]
        subzone = utm[1]
        zone = utm[0]
        e1 = (1-sqrt(1-self.eccSquared))/(1+sqrt(1-self.eccSquared))
        #NorthernHemisphere; //1 for northern hemispher, 0 for southern
        x = easting - 500000.0 #remove 500,000 meter offset for longitude
        y = northing
        ZoneLetter = subzone
        ZoneNumber = int(zone)
        if ZoneLetter >= 'N':
            NorthernHemisphere = 1  # point is in northern hemisphere
        else:
            NorthernHemisphere = 0  # point is in southern hemisphere
            y -= 10000000.0         # remove 10,000,000 meter offset used for southern hemisphere
        LongOrigin = (ZoneNumber - 1)*6 - 180 + 3  # +3 puts origin in middle of zone
        M = y / self.k0
        mu = M/(self.a*(1-self.eccSquared/4-3*self.eccSquared*self.eccSquared/64-5*(self.eccSquared**3)/256))
        phi1Rad = (mu + (3*e1/2-27*e1*e1*e1/32)*sin(2*mu)
                   + (21*e1*e1/16-55*e1*e1*e1*e1/32)*sin(4*mu)
                   +(151*e1*e1*e1/96)*sin(6*mu))
        phi1 = degrees(phi1Rad)
        N1 = self.a/sqrt(1-self.eccSquared*sin(phi1Rad)*sin(phi1Rad))
        T1 = tan(phi1Rad)*tan(phi1Rad)
        C1 = self.eccPrimeSquared*cos(phi1Rad)*cos(phi1Rad)
        R1 = self.a*(1-self.eccSquared)/pow(1-self.eccSquared*sin(phi1Rad)*sin(phi1Rad), 1.5)
        D = x/(N1*self.k0)
        Lat = phi1Rad - (N1*tan(phi1Rad)/R1)*(D*D/2-(5+3*T1+10*C1-4*C1*C1-9*self.eccPrimeSquared)*D*D*D*D/24
                                              +(61+90*T1+298*C1+45*T1*T1-252*self.eccPrimeSquared-3*C1*C1)*D*D*D*D*D*D/720)
        Lat = degrees(Lat)
        Long = (D-(1+2*T1+C1)*D*D*D/6+(5-2*C1+28*T1-3*C1*C1+8*self.eccPrimeSquared+24*T1*T1)
                *D*D*D*D*D/120)/cos(phi1Rad)
        Long = LongOrigin + degrees(Long)
        return [Lat, Long]
    def UTMtoMGRS(self, utm):
        '''! \brief Converts UTM into MGRS according to the source code from the xastir project.
         \param utmZone eg 12T
         \param Xthing in meters, assumed to be floats
        '''
        # vars
        utmZone = utm[0]
        utmSubZone = utm[1]
        utmEasting = int(utm[2])
        utmNorthing = int(utm[3])
        # Zone keys
        EW = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        NS = 'ABCDEFGHJKLMNPQRSTUV'
        # Get the Easting letter
        start = int(utmZone)
        start -= 1
        start %= 3
        start *= 8
        start %= 24 # Index of the starting letter for the current zone
        eastoffset = int( utmEasting / 100000. ) - 1
        eastindex = (start + eastoffset) % 24
        eastCode = EW[eastindex]
        # Get the northing
        start = int(utmZone)
        start %= 2
        if start:
            # Odd number zone start @ A
            start = 0
        else:
            # Even @ F
            start = 5
        northoffset = int( utmNorthing / 100000. )
        northindex = (northoffset + start) % 20
        northCode = NS[northindex]
        northing = utmNorthing % 100000
        easting = utmEasting % 100000
        return [utmZone, utmSubZone, eastCode + northCode, str(int(easting)).zfill(5), str(int(northing)).zfill(5)]
    def MGRStoUTM(self, mgrs):
        '''! \brief Conversion from MGRS component list to UTM list.
        '''
        # Zone keys
        EW = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        NS = 'ABCDEFGHJKLMNPQRSTUV'
        # Zone
        utmZone = str(mgrs[0]) + mgrs[1]
        # Easting
        S = int(mgrs[0]) - 1
        S %= 3
        S *= 8
        S %= 24  # Index of first box in this zone
        myindex = EW.find(mgrs[2][0]) - S
        eastoffset = 100000. + (100000. * myindex) + int(mgrs[3])
        # Northing
        # Get the northing
        S = int(mgrs[0])
        S %= 2
        if S:
            # Odd number zone start @ A
            ns = NS
        else:
            # Even @ F
            ns = NS[5:]+NS[:5]
        # Northing bounds
        NBd = self._AllowedNorthingFromZone(mgrs[1])
        # Offset from N (use EW for major zone seprators since there are letter beyond V in this scale)
        if EW.find(mgrs[1]) >= EW.find('N'):
            # Norther hemisphere
            offset = ns.find( mgrs[2][-1] )
            northing = offset * 100000. + float(mgrs[4])
            while northing < NBd[0]*0.95:
                # One spin around the alphabet
                northing += 2000000.
        else:
            northing = 10000000.
            # Determine how many boxes to move down from last box before equator
            offset = len(ns) - ns.find(mgrs[2][-1])
            # minus 100km box + northing residual
            offset = (-100000 * offset) + float(mgrs[4])
            northing += offset
            # the 1.05 factor is there to compensate for loos of precision.
            while northing > NBd[1]*1.05:
                # One Spin around the alphabet
                northing -= 2000000.
        return [mgrs[0], mgrs[1], eastoffset, northing]
    #
    # Private Methods
    def _UTMLetterDesignator(self, Lat):
        '''! \brief Returns the main letter designator for a latitude given in decimal Lat.
             Returns a Z if outside of the UTM area.
        '''
        for i in self._NSminbound.keys():
            x = self._NSminbound[i]
            if Lat >= x and Lat < x+8:
                return i
        return 'Z'
    def _AllowedNorthingFromZone(self, Z):
        '''! \brief Returns a list of min and max UTM Northing for a given Zone.
             This is a utility function for MGRStoUTM.
        '''
        mn = self._NSminbound[Z]
        mx = mn + 8
        Nmin = self.LLtoUTM([mn,0])[-1]
        Nmax = self.LLtoUTM([mx,0])[-1]
        if Z == 'M':
            Nmax = 10000000
        return [Nmin,Nmax]
    def _DegMinSec(self, s):
        '''! \brief Returns a list of deg, min and sec
        '''
        out = [0.0, 0.0, 0.0]
        # Degrees.
        span = re.compile('[+-]?\d+').search(s).span()
        out[0] = int(s[span[0]:span[1]])
        # Minutes.
        span = re.compile('\d+').search(s, span[1]).span()
        out[1] = int(s[span[0]:span[1]])
        # seconds
        try:
            span = re.compile('\d+').search(s, span[1]).span()
            out[2] = int(s[span[0]:span[1]])
        except:
            pass
        return out
if __name__ == '__main__':
    # Create an instance of the Translator
    a = CoordTranslator()
    print a.AsUTM('0 0 0 0 0 0')
    # Ten thousand two-way conversions
    from random import random
    i = 0
    miss = 0
    while i < 10000:
        lat = random()*160. - 80
        lon = random()*360. - 180
        #lat = -24.0040004515
        #lon = 69.8148278944
        utm = a.LLtoUTM([lat, lon])
        mgrs = a.UTMtoMGRS(utm)
        utm2 = a.MGRStoUTM(mgrs)
        if utm != utm2:
            print i
            print lat, lon
            print utm, mgrs
            print utm2
            miss += 1
        i += 1
    print 'Percent missed: ', 100*miss/float(i)