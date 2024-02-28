import sys
import getopt
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring

try:
    opts, _ = getopt.getopt(sys.argv[1:], "h", ["help"])
except getopt.GetoptError as err:
    exit(10)

for o, a in opts:
    if o in ("-h", "--help") and len(sys.argv) == 2:
        print("Usage: parse.py [options] <file>")
        sys.exit(0)
    else:
        print("Error: parametr --help/-h can't be combined with other options")
        sys.exit(10)

