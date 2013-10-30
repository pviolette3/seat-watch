import BeautifulSoup as bs
import requests as r
from HTMLParser import HTMLParser
import time

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
    print 'ssl error'
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
  def alert(self, crn, seats):
    print 'crn ', crn, ' has ', str(seats), ' available.'

notifier = ConsoleNotifier()

while True:
  for crn in crns:
    seats = get_seats_available(crn)
    notifier.alert(crn=crn, seats=seats)
  time.sleep(30)
