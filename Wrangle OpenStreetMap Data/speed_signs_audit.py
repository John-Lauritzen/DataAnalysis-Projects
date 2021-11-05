import xml.etree.ElementTree as ET
import pprint

OSMFILE = "Taylorsville.osm"

def is_maxspeed_invalid(elem):
    return ((elem.attrib['k'] == "maxspeed:type") & (elem.attrib['v'] == "sign"))


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf-8")
    sign_count = 0
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_maxspeed_invalid(tag):
                    sign_count += 1
    osm_file.close()
    print('The count of invalid maxspeed:type = sign tags is', sign_count)
    return sign_count


audit(OSMFILE)