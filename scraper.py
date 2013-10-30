import BeautifulSoup as bs
import requests as r
from HTMLParser import HTMLParser
import time
import patrick_twilio as ptwilio

class MLStripper(HTMLParser):
  def __init__(self):
    self.reset()
    self.fed = []
  
  def handle_data(self, d):
    self.fed.append(d)

  def get_data(self):
    return ''.join(self.fed)

def strip_tags(html):
  s = MLStripper()
  s.feed(html)
  return s.get_data()

def get_seats_available(crn):
  try:
    resp = r.get('https://oscar.gatech.edu/pls/bprod/bwckschd.p_disp_detail_sched?term_in=201402&crn_in=%s' % crn, verify=False)
  except r.exceptions.SSLError:
    print( 'ssl error')
    quit()
    pass
  if resp and resp.ok:
    soup = bs.BeautifulSoup(resp.text)
    theTable = soup.findAll('table', attrs={"class" : "datadisplaytable", "summary":"This layout table is used to present the seating numbers."})[0]
    remainingTag = theTable.findAll('td', attrs={"class" : "dddefault"})[2]
    seatsLeft = int(strip_tags(str(remainingTag)))
  return seatsLeft

crns = ['21973', '22247', '28472']

class ConsoleNotifier:
  def alert(self, crn, seats, time):
    print( 'crn ', crn, ' has ', str(seats), ' available.')

class TwilioNotifier:

  def __init__(self, twilio_rest_client, to_number, from_number):
    self.client = twilio_rest_client
    self.crns_notified = {}
    self.from_number = from_number
    self.to_number = to_number

  def alert(self, crn, seats):
    if crn not in self.crns_notified:
      data = { 
          "time_millis" : time.time(),
          "time_struct" : time.localtime(),
          "seats" : seats
      };
      data["last_notified"] = 0
      self.crns_notified[crn] = data

    self.crns_notified[crn]["seats"] = seats
    if seats > 0 and data["last_notified"] < time.time() + 60*60*1000:
      self.crns_notified[crn]["time_millis"] = time.time()
      self.crns_notified[crn]["time_struct"] = time.localtime()
      time_now = time.strftime("%a, %d %b %Y %H:%M:%S", self.crns_notified[crn]["time_struct"])
      message = "Crn {crn} now has {seats} seats at time {time}".format(seats=seats, crn=crn, time=time_now)
      self.client.sms.messages.create(body=message, to=self.to_number, from_=self.from_number)

notifier = TwilioNotifier(ptwilio.client(), ptwilio.to_number, ptwilio.from_number)

while True:
  for crn in crns:
    seats = get_seats_available(crn)
    notifier.alert(crn=crn, seats=seats)
  time.sleep(30) #seconds
