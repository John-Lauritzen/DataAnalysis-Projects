import xml.etree.ElementTree as ET

OSMFILE = "Taylorsville.osm"

def is_name1(elem):
    return (elem.attrib['k'] == "name1")


def audit(osmfile):
    osm_file = open(osmfile, "r", encoding="utf-8")
    name1_count = 0
    for event, elem in ET.iterparse(osm_file, events=('start',)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_name1(tag):
                    name1_count += 1
    osm_file.close()
    print('The count of outdated name1 tags is', name1_count)
    return name1_count


audit(OSMFILE)