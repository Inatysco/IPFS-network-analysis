#!/usr/bin/python3
import sys
import os
import re
import concurrent.futures
import base64
import base58check
import threading
import json
import requests
import ipaddress
import geoip2.database
import dns.resolver
import dns.reversename
import magic
import socket
import time

LOG_PATTERN = re.compile('handling message([^{]+){"from": "([^"]+)", "type": ([0-9]+), "key": "([^"]+)"}')
IPFS_URLS = os.environ['IPFS_URLS'].split(',')
NB_WORKERS=len(IPFS_URLS)
REQUEST_TIMEOUT=1

def dhtquery(ipfs_url, arg):
 # get the closest peers from arg in the dht
 peers = []
 r = requests.post('%s/api/v0/dht/query?arg=%s&verbose=0' % (ipfs_url, arg))
 for line in r.iter_lines():
  json_line = json.loads(line.decode())
  if json_line['Type'] != 2:
   continue;
  if 'ID' in json_line and json_line['ID']:
   peers.append(json_line['ID'])
  if 'Responses' in json_line and json_line['Responses']!=None:
   for response in json_line['Responses']:
    if 'ID' in response and response['ID']:
     peers.append(response['ID'])
 return peers

def findprovs(ipfs_url, cid, num_provs=5, timeout=REQUEST_TIMEOUT):
 providers = []
 r = requests.post('%s/api/v0/dht/findprovs?arg=%s&verbose=0&num-providers=%d' % (ipfs_url, cid, num_provs), timeout=(timeout, timeout))
 for line in r.iter_lines():
  json_line = json.loads(line.decode())
  if json_line['Type'] != 4:
   continue;
  if 'ID' in json_line and json_line['ID']:
   providers.append(json_line['ID'])
  if 'Responses' in json_line and json_line['Responses']!=None:
   for response in json_line['Responses']:
    if 'ID' in response and response['ID']:
     providers.append(response['ID'])
 return providers

def findpeer(ipfs_url, peerid, timeout=REQUEST_TIMEOUT):
 ips = []
 try:
  r = requests.post('%s/api/v0/dht/findpeer?arg=%s&verbose=0' % (ipfs_url, peerid), timeout=(timeout, timeout))
  for line in r.iter_lines():
   json_line = json.loads(line.decode())
   if json_line['Type'] != 2:
    continue
   if 'Responses' in json_line and json_line['Responses']:
    for response in json_line['Responses']:
     if 'Addrs' in response and response['Addrs']:
      ips = ips + response['Addrs']
 except Exception as e:
  pass
 return ips

def filter(addrs):
 res = []
 for addr in addrs:
  a = addr.split('/')
  if a[1] not in ['ip4', 'ip6']:
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('::1/128'):
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('127.0.0.0/8'):
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('10.0.0.0/8'):
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('172.16.0.0/12'):
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('192.168.0.0/16'):
   continue
  if ipaddress.ip_address(a[2]) in ipaddress.ip_network('fe80::/10'):
   continue
  res.append((a[2], '%s/%s' % (a[3], a[4])))
 return list(set(res))

def ip_info(ip):
 info = {}
 info['addr'] = ip
 try:
  with geoip2.database.Reader('/var/lib/GeoIP/GeoLite2-Country.mmdb') as reader:
   response = reader.country(ip)
   info['country'] = response.country.iso_code
 except:
  info['country'] = None
 try:
  with geoip2.database.Reader('/var/lib/GeoIP/GeoLite2-City.mmdb') as reader:
   response = reader.city(ip)
   info['city'] = response.city.name
 except:
  info['city'] = None
 try:
  with geoip2.database.Reader('/var/lib/GeoIP/GeoLite2-ASN.mmdb') as reader:
   response = reader.asn(ip)
   info['asn'] = response.autonomous_system_number
   info['autonomous_system'] = response.autonomous_system_organization
 except:
  info['asn'] = None
  info['autonomous_system'] = None
 try:
  addr=dns.reversename.from_address(ip)
  info['reverse'] = str(dns.resolver.resolve(addr,"PTR")[0])
 except:
  info['reverse'] = None
 return info

def mimetype(ipfs_url, cid):
 try:
  r = requests.post('%s/api/v0/cat?arg=%s&offset=0&length=1000' % (ipfs_url, cid), timeout=REQUEST_TIMEOUT)
  filetype = magic.detect_from_content(r.content)
  return (filetype.mime_type, filetype.name)
 except Exception as e:
  return (None, None)

def cid64_to_cid58(cid64):
 cid = base64.b64decode(cid64)
 return base58check.b58encode(cid).decode()

def extract_line(line, pattern):
 try:
  extract_line2(line, pattern)
 except Exception as e:
  print(e, file=sys.stderr)

def process_peer(ipfs_url, peerid, timeout=REQUEST_TIMEOUT):
 # we find the detailed information on the peer (ip address)
 addrs = filter(list(set(findpeer(ipfs_url, peerid, timeout))))
 for addr, port in addrs:
  # check if the address is already in database
  addr_info = ip_info(addr)
  # add the address in the database
  print("insert into ip(addr, country, city, asn, autonomous_system, reverse) values('%s', '%s', '%s', '%s', '%s', '%s') on conflict do nothing;" % (addr, addr_info['country'], addr_info['city'], addr_info['asn'], addr_info['autonomous_system'], addr_info['reverse'] ))
  # and then we add the peer
  print("insert into peer(id, addr, port) values('%s', '%s', '%s') on conflict do nothing;" % (peerid, addr, port ))
  # violates the not-null constraint on addr field
  if addrs == []:
   print("insert into peer(id, addr, port) values('%s', null, null) on conflict do nothing;" % (peerid, ))

def process_file(ipfs_url, cid):
 # find the information about the file
 mime, description = mimetype(ipfs_url, cid)
 print("insert into files(cid, mimetype, description) values('%s', '%s', '%s') on conflict do nothing;" % (cid, mime, description, ))


def check_connectivity(ipfs_url):
 ok=False
 while not ok:
  try:
   r = requests.get(ipfs_url)
   ok = True
  except Exception as e:
   print(e, file=sys.stderr)
   print('bad connectivity %s' % (ipfs_url), file=sys.stderr)
   time.sleep(5)

def extract_line2(line, pattern):
 date = line.split('\t')[0]
 peerid = pattern.group(2)
 cid64 = pattern.group(4)
 cid58 = cid64_to_cid58(cid64)
 ipfs_url = IPFS_URLS[ threading.current_thread().native_id % len(IPFS_URLS) ]
 print((date, peerid, cid58, ipfs_url), file=sys.stderr)

 # check the connectivity to the ipfs node
 check_connectivity(ipfs_url)
 print('ok', file=sys.stderr)

 process_peer(ipfs_url, peerid)
 process_file(ipfs_url, cid58)

 # save the activity
 print("insert into activity(peerid, cid, date) values('%s', '%s', '%s') on conflict do nothing;" % (peerid, cid58, date, ))

 # find all the providers of the file
 for provider in findprovs(ipfs_url, cid58, timeout=0.5):
  process_peer(ipfs_url, provider, timeout=0.5)
  print("insert into storage(peerid, cid, date) values('%s', '%s', '%s') on conflict do nothing;" % (provider, cid58, date, ))


def main_file(filename):
 if not os.path.isfile(filename) or not os.access(filename, os.R_OK):
  print('Log file %s does not exist or is not readable' % (filename), file=sys.stderr);
  sys.exit(1)
 with concurrent.futures.ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
  with open(filename, 'r') as f:
   for line in f:
    m = LOG_PATTERN.search(line)
    if m:
     executor.submit(extract_line, line, m)

def main_stdin():
 with concurrent.futures.ThreadPoolExecutor(max_workers=NB_WORKERS) as executor:
  while True:
   try:
    for line in sys.stdin:
     m = LOG_PATTERN.search(line)
     if m:
      executor.submit(extract_line, line, m)
   except UnicodeDecodeError as e:
    continue


def main():
 if len(sys.argv) >= 2:
  main_file(sys.argv[1])
 else:
  main_stdin()

if '__main__' == __name__:
 main()
