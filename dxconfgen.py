#!/usr/bin/env python3

from jinja2 import Template
import json
import os, sys
import random
import string
import urllib.request
import argparse
import configparser

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
parser.add_argument('-n', '--configname', type=str, help='config file name', required=False, default=None)

args = parser.parse_args()

#print (args)

if args.blockchain:
  chainKey = ('[%s]' % (args.blockchain))  # chainKey = LTC/BTC/etc
  rpcuser = random_gen()
  rpcpass = random_gen()
  
  # find the URL for the chain
  try:
    xbridge_text = load_template(chain_lookup(args.blockchain))
  except urllib.error.HTTPError as e:
    print("Config for currency {} not found".format(args.blockchain))
    sys.exit(-1)
  xbridge_json = json.loads(xbridge_text)
  xtemplate = Template(xbridge_text)
  params = {}
  if args.p2pport:
    params['p2pPort'] = args.p2pport
  if args.rpcport:
    params['rpcPort'] = args.rpcport
  xresult = xtemplate.render(rpcusername=rpcuser, rpcpassword=rpcpass, **params)
  xbridge_json = json.loads(xresult)

  for x in xbridge_json: p2pport = (xbridge_json[x]['p2pPort'])
  for x in xbridge_json: rpcport = (xbridge_json[x]['rpcPort']) 
  res_conf = load_template(walletconfj2_url)  # generate wallet config
  template = Template(res_conf)
  result = template.render(rpcusername=rpcuser, rpcpassword=rpcpass, p2pPort=p2pport, rpcPort=rpcport)

  xbridge_config = configparser.ConfigParser()
  xbridge_config.optionxform = str 
  xbridge_config[args.blockchain] = list(xbridge_json.values())[0]
  confFile = list(xbridge_json.values())[0]['Title']
  if args.configname:
    confFile = args.configname
  with open(confFile+'-xbridge.conf', 'w') as configfile:
    xbridge_config.write(configfile, space_around_delimiters=False) 
  xbridge_config.write(sys.stdout, space_around_delimiters=False)
  print ('---')
  print (result)
  
  confFile = ('%s.conf' % confFile)
  print (confFile)
  save_config(result, confFile)
