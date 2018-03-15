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
xbridgeconfj2_url = "https://raw.githubusercontent.com/BlocknetDX/blocknet-docs/master/json-config-templates/xbridge.conf.j2"

def chain_lookup(s):
  return "https://raw.githubusercontent.com/BlocknetDX/blocknet-docs/master/json-config-templates/{}.json.j2".format(s.lower())

def generate_confs(blockchain, p2pport, rpcport, configname, rpcuser, rpcpass):
  if blockchain:
    if len(blockchain) > 1:
      if p2pport:
        print("Warning: parameter --p2pport ignored because multiple blockchains were selected.")
      if rpcport:
        print("Warning: parameter --rpcport ignored because multiple blockchains were selected.")
      if configname:
        print("Warning: parameter --configname ignored because multiple blockchains were selected.")
      if rpcuser:
        print("Warning: parameter --rpcuser ignored because multiple blockchains were selected.")
      if rpcpass:
        print("Warning: parameter --rpcpass ignored because multiple blockchains were selected.")
      rpcuser = random_gen()
      rpcpass = random_gen()
      p2pport = rpcport = configname = None
    for blockchain in blockchain:      
      # find the URL for the chain
      try:
        xbridge_text = load_template(chain_lookup(blockchain))
      except urllib.error.HTTPError as e:
        print("Config for currency {} not found".format(blockchain))
        continue
      xbridge_json = json.loads(xbridge_text)
      xtemplate = Template(xbridge_text)
      params = {}
      if args.p2pport:
        params['p2pPort'] = p2pport
      if args.rpcport:
        params['rpcPort'] = rpcport
      if not args.rpcuser:
        rpcuser = random_gen()
        params['rpcusername'] = rpcuser
      if args.rpcuser:
        params['rpcusername'] = rpcuser
      if not args.rpcpass:
        rpcpass = random_gen()
        params['rpcpassword'] = rpcpass
      if args.rpcpass:
        params['rpcpassword'] = rpcpass
      xresult = xtemplate.render(**params)
      xbridge_json = json.loads(xresult)

      confFile = list(xbridge_json.values())[0]['Title'].lower()
      if configname:
        confFile = args.configname.lower()
      
      # generate wallet config
      for x in xbridge_json: p2pport = (xbridge_json[x]['p2pPort'])
      for x in xbridge_json: rpcport = (xbridge_json[x]['rpcPort']) 
      res_conf = load_template(walletconfj2_url)  
      template = Template(res_conf)
      result = template.render(rpcpassword=rpcpass, rpcusername=rpcuser, p2pPort=p2pport, rpcPort=rpcport)
      save_config(result, '%s.conf' % confFile)
        
      # generate xbridge config
      xbridge_config = load_template(xbridgeconfj2_url)
      #f = open("xbridge.conf.j2", "r")
      #xbridge_config = f.read()
      xbridge_template = Template(xbridge_config)
      xbridge_result = xbridge_template.render(blockchain=blockchain, val=list(xbridge_json.values())[0])
      save_config(xbridge_result, confFile+'-xbridge.conf')
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='blockdx-conf-gen')
  parser.add_argument('--verbose', action='store_true', help='verbose flag' )

  # Add arguments
  parser.add_argument('-c', '--blockchain', type=str, help='Blockchain config to download', required=True, nargs = '*')
  parser.add_argument('-p2p', '--p2pport', type=str, help='p2pport override', required=False, default=None)
  parser.add_argument('-rpc', '--rpcport', type=str, help='rpcport override', required=False, default=None)
  parser.add_argument('-n', '--configname', type=str, help='config file name', required=False, default=None)
  parser.add_argument('-u', '--rpcuser', type=str, help='rpc username', required=False, default=None)
  parser.add_argument('-p', '--rpcpass', type=str, help='rpc password', required=False, default=None)

  args = parser.parse_args()
generate_confs(args.blockchain, args.p2pport, args.rpcport, args.configname, args.rpcuser, args.rpcpass)
