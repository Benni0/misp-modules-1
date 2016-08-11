import json
import stix
import csv
from stix.core import STIXPackage
import re
import base64

misperrors = {'error': 'Error'}
userConfig = {}
inputSource = ['file']

moduleinfo = {'version': '0.1', 'author': 'Hannah Ward',
              'description': 'Import some stix stuff',
              'module-type': ['import']}

moduleconfig = []


def handler(q=False):
    #Just in case we have no data
    if q is False:
        return False

    #The return value 
    r = {'results': []}

    #Load up that JSON
    q = json.loads(q)

    #It's b64 encoded, so decode that stuff
    package = str(base64.b64decode(q.get("data", None)), 'utf-8')
     
    #If something really weird happened
    if not package:
      return json.dumps({"success":0})

    #Load up the package into STIX
    package = loadPackage(package)

    #Build all the observables
    if package.observables:
      for obs in package.observables:
        r["results"].append(buildObservable(obs))
      
    return r

#Quick and dirty regex for IP addresses
ipre = re.compile("([0-9]{1,3}.){3}[0-9]{1,3}")

def buildObservable(o):
  """
    Take a STIX observable
    and extract the value
    and category
  """

  #Life is easier with json
  o = json.loads(o.to_json())
   
  #Make a new record to store values in
  r = {"values":[]}

  #Get the object properties. This contains all the
  #fun stuff like values
  props = o["object"]["properties"]

  #If it has an address_value field, it's gonna be an address

  #Kinda obvious really
  if props["address_value"]:

    #We've got ourselves a nice little address
    value = props["address_value"]

    #Is it an IP?
    if ipre.match(value):

      #Yes!
      r["values"].append(value)
      r["types"] = ["ip-src", "ip-dst"]
    else:

      #Probably a domain yo
      r["values"].append(value)
      r["types"] = ["domain", "hostname"]

  return r

def loadPackage(data):
  #Write the stix package to a tmp file
  with open("/tmp/stixdump", "w") as f:
    f.write(data)
  try:
    #Try loading it into every format we know of
    try:
      package = STIXPackage().from_xml(open("/tmp/stixdump", "r"))
    except:  
      package = STIXPackage().from_json(open("/tmp/stixdump", "r"))
  except:
    print("Failed to load package")
    raise ValueError("COULD NOT LOAD STIX PACKAGE!")
  return package

def introspection():
    modulesetup = {}
    try:
        userConfig
        modulesetup['userConfig'] = userConfig
    except NameError:
        pass
    try:
        inputSource
        modulesetup['inputSource'] = inputSource
    except NameError:
        pass
    return modulesetup


def version():
    moduleinfo['config'] = moduleconfig
    return moduleinfo
