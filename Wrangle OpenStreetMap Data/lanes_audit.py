import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict
import re

OSMFILE = "Taylorsville.osm"
TURN_LANES_CHECK = re.compile(r'^turn:lanes')

def is_turn_lanes(elem):
    return (TURN_LANES_CHECK.match(elem.attrib['k']))


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf-8")
    lane_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_turn_lanes(tag):
                    lane_type = tag.attrib['v']
                    if lane_type in lane_types:
                        lane_types[lane_type] += 1
                    else:
                        lane_types[lane_type] = 1
    osm_file.close()
    return lane_types


pprint.pprint(audit(OSMFILE))