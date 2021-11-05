import xml.etree.ElementTree as ET

OSMFILE = "Taylorsville.osm"

def is_hov_invalid(elem):
    return ((elem.attrib['k'] == "hov") & (elem.attrib['v'] == "lane"))


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf-8")
    invalid_count = 0
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_hov_invalid(tag):
                    invalid_count += 1
    osm_file.close()
    print('The count of invalid HOV tags is', invalid_count)
    return invalid_count


audit(OSMFILE)