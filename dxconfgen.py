#!/usr/bin/env python3

from jinja2 import Template
import json
import os, sys
import random
import string
import urllib.request
import argparse

def random_gen(size=32, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
  return ''.join(random.choice(chars) for x in range(size))

def load_template(template_url):
  # load_template - downloads from url provided and returns the data
  with urllib.request.urlopen(template_url) as response:
    data = response.read()
    result = data.decode('utf-8')
  return result

def save_config(configData, confFile):
  with open(confFile, 'w') as outfile:
    #out.write(data, outfile)
    outfile.write(configData)
  return

walletconfj2_url = "https://raw.githubusercontent.com/BlocknetDX/blocknet-docs/master/json-config-templates/wallet.conf.j2"

def chain_lookup(s):
    return "https://raw.githubusercontent.com/BlocknetDX/blocknet-docs/master/json-config-templates/{}.json.j2".format(s.lower())

parser = argparse.ArgumentParser(description='blockdx-conf-gen')
parser.add_argument('--verbose',
    action='store_true',
    help='verbose flag' )

# Add arguments
parser.add_argument('-c', '--blockchain', type=str, help='Blockchain config to download', required=True)
parser.add_argument('-p2p', '--p2pport', type=str, help='p2pport override', required=False, default=None)
parser.add_argument('-rpc', '--rpcport', type=str, help='rpcport override', required=False, default=None)

args = parser.parse_args()

#print (args)

if args.blockchain:
  #print (args.blockchain)
  chainKey = ('[%s]' % (args.blockchain))  # chainKey = LTC/BTC/etc
  # find the URL for the chain
  #print (chain_lookup(args.blockchain))
  try:
    res_text = load_template(chain_lookup(args.blockchain))
  except urllib.error.HTTPError as e:
    print("Config for currency {} not found".format(args.blockchain))
    sys.exit(-1)
  jres_text = json.loads(res_text)
  res_conf = load_template(walletconfj2_url)  # generate wallet config
  template = Template(res_conf)

  rpcuser = random_gen()
  rpcpass = random_gen()

  for x in jres_text: p2pport = (jres_text[x]['p2pPort'])
  for x in jres_text: rpcport = (jres_text[x]['rpcPort'])
  if args.p2pport:
    p2pport = args.p2pport
  if args.rpcport:
    rpcport = args.rpcport
  result = template.render(rpcusername=rpcuser, rpcpassword=rpcpass, p2pPort=p2pport, rpcPort=rpcport)
  xtemplate = Template(res_text)
  xresult = xtemplate.render(rpcusername=rpcuser, rpcpassword=rpcpass, p2pPort=p2pport, rpcPort=rpcport)
  # this is the code needed for fileoutput, disabled as its TODO
  #print (result)
  #iprint (' XBRIDGE.CONF ')
  tz = chainKey + '\r\n'
  jres_text = json.loads(xresult)
  for x in jres_text: 
    for z in jres_text[x]:
      xz = ( '='.join([z, str (jres_text[x][z])] ))
      tz = tz + xz + '\r\n'
      #print (xz)
  print (tz)
  print ('---')
  print (result)
  for x in jres_text: confFile = (jres_text[x]['Title'])
  save_config(tz, confFile+'-xbridge.conf') # chain config for xbridge.conf
  confFile = ('%s.conf' % confFile)
  print (confFile)
  save_config(result, confFile)
