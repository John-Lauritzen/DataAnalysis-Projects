import xml.etree.ElementTree as ET
import pprint
import re
from collections import defaultdict

OSMFILE = "Taylorsville.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "East", "West", "North", "South", "Way", "Circle", "Temple", 
            "Cove", "Bay", "Center", "Frontage"]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf-8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


pprint.pprint(audit(OSMFILE))