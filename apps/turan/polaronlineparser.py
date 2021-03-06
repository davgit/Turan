from xml.etree import ElementTree as ET
import datetime
#import pyproj
#from math import hypot
#geod = pyproj.Geod(ellps='WGS84')


class Entry(object):

    def __init__(self, time, hr, speed, cadence, altitude, lon, lat):
        self.time = time
        self.hr = hr
        self.speed = speed
        self.cadence = cadence
        self.altitude = altitude
        self.lat = lat
        self.lon = lon

class POLParser(object):

    def __init__(self, filename=None):
        self.start_lon = 0.0
        self.start_lat = 0.0

        self.end_lon = 0.0
        self.end_lat = 0.0

        self.entries = []
        self.laps = []
        self.distance = 0.0
        self.ascent = 0.0
        self.descent = 0.0
        self.max_speed = 0
        self.avg_speed = 0
        self.max_hr = 0
        self.avg_hr = 0
        self.avg_cadence = 0
        self.max_cadence = 0
        self.kcal_sum = 0
        # self.comment = '' Fixme
        if filename:
            self.parse_uploaded_file(filename)

    def parse_uploaded_file(self, filename):

        if self.entries: # Do not parse again if sent filename in constructor
            return

        try:
            doc = ET.parse(filename)
        except:
            # mongofil
            return
        root = doc.getroot()
        ns = '{http://www.polarpersonaltrainer.com}'
        self.ns = ns

        exercise = root[0][0]

        # http://en.wikipedia.org/wiki/Dilution_of_precision_(GPS)
        vdop_cutoff = 30
        hdop_cutoff = 90

        self.start = datetime.datetime.strptime(exercise.find(ns + "time").text,"%Y-%m-%d %H:%M:%S.0")
        self.start_time = self.start.time()
        self.date = self.start.date()

        result = exercise.find(ns+'result')
        self.kcal_sum = int(result.find(ns + 'calories').text)
        self.distance_sum = 0
        try:
            self.distance_sum = float(result.find(ns + 'distance').text)
        except: pass # element missing in many files
        self.comment = ''
        try:
            self.comment = result.find(ns + 'note').text.strip()
        except: pass # element missing in many files
        duration = result.find(ns+'duration').text
        hour, minute, second = int(duration[0:2]), int(duration[3:5]), int(duration[6:8])
        self.seconds = hour*3600 + minute*60 + second
        self.duration = '%ss' %(self.seconds)

        self.interval = 5 # default

        for sample in result.find(ns+'samples').getchildren():
            sampletype = sample.find(ns+'type').text
            values = sample.find(ns+'values').text.strip().split(',')
            if sampletype == 'HEARTRATE':
                # Try to determine interval based on number of samples and duration
                self.interval = int(round(1. / (float(len(values)) / self.seconds)))
                for i, value in enumerate(values):
                    time = self.start + datetime.timedelta(0, self.interval*i)
                    hr = int(value)
                    self.avg_hr += int(hr)
                    if hr > self.max_hr:
                        self.max_hr = hr
                    self.entries.append(Entry(time, hr, 0, 0, 0, 0, 0))
            elif sampletype == 'SPEED':
                for i, value in enumerate(values):
                    if not value: continue # protect against empty samples
                    speed = float(value)
                    if speed > self.max_speed:
                        self.max_speed = speed
                    self.avg_speed += speed
                    self.entries[i].speed = speed
            elif sampletype == 'ALTITUDE':
                for i, value in enumerate(values):
                    if not value: continue # protect against empty samples
                    altitude = float(value)
                    self.entries[i].altitude = int(round(altitude)) # somehow these are floats?? round to int 
            elif sampletype == 'RUN_CADENCE':
                for i, value in enumerate(values):
                    if not value: continue # protect against empty samples
                    cadence = float(value)
                    self.avg_cadence += cadence
                    self.entries[i].cadence = cadence

        if self.entries:
            if self.avg_speed:
                self.avg_speed = self.avg_speed/len(self.entries)
            if self.avg_hr:
                self.avg_hr = self.avg_hr/len(self.entries)
            if self.avg_cadence:
                self.avg_cadence = self.avg_cadence/len(self.entries)




if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    g = POLParser(filename)
    print g.start_lon, g.start_lat, g.end_lon, g.end_lat

    for e in g.entries:
        #if 'speed' in e and 'altitude' in e:
        print e.time, e.hr, e.speed, e.altitude, e.lon, e.lat
        #else:
        #    print e['time'], e['lon'], e['lat']
    print 'distance: ', g.distance_sum
    print 'avg_hr: ', g.avg_hr
    print 'avg_cadence: ', g.avg_cadence
    print 'avg_speed: ', g.avg_speed
    print 'calories: ', g.kcal_sum
    print 'comment: ', g.comment


