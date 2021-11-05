import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

OSM_PATH = "Taylorsville.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
STREET_TYPE = re.compile(r'\b\S+\.?$', re.IGNORECASE)
TURN_LANES_CHECK = re.compile(r'^turn:lanes')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
STREET_MAPPING = {"Ave": "Avenue", "St.": "Street", "Rd.": "Road", "Blvd": "Boulevard", "Cir": "Circle",
                  "Dr": "Drive", "E": "East", "Ln": "Lane", "Pl": "Place", "Rd": "Road", "S": "South",
                  "St": "Street", "W": "West", "avenue": "Avenue", "cove": "Cove", "st": "Street",
                  "street": "Street"} #Mapping based on results of street_audit.py


# ================================================== #
#           Audit & Cleaning Functions               #
# ================================================== #
def is_maxspeed_invalid(elem):
    return ((elem.attrib['k'] == "maxspeed:type") & (elem.attrib['v'] == "sign"))

def update_street_name(name, mapping):
    street_update = re.search(STREET_TYPE, name).group() #Determines street type at end of name
    if street_update in mapping:
        name = re.sub(STREET_TYPE, mapping[street_update], name) #Updates street type in name using provided mapping
    return name

def update_turn_lanes(lanes):
    lanes = re.sub("^\|", "none|", lanes) #First replaces blank | at the start of the string, if present
    lanes = re.sub("\|$", "|none", lanes) # Same as above, but replacing at the end of the string
    lanes = re.sub("\|\|", "|none|", lanes) #Replaces || with |none| to improve readability
    lanes = re.sub("\|\|", "|none|", lanes) #Runs a second time to catch any new pairs of || created by the first pass
    return lanes

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_hov_invalid(elem):
    return ((elem.attrib['k'] == "hov") & (elem.attrib['v'] == "lane"))

def is_turn_lanes(elem):
    return (TURN_LANES_CHECK.match(elem.attrib['k']))

def is_name1(elem):
    return (elem.attrib['k'] == "name1")


# ================================================== #
#              Shape Data Function                   #
# ================================================== #
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    if element.tag == 'node':
        for i in node_attr_fields: #For node attributes simply iterate through each field pulled in from NODE_FIELDS and store it
            node_attribs[i] = element.attrib[i]
            
    elif element.tag == 'way': 
        node_count = 0 #Value used for recording position of node
        for i in way_attr_fields:
            way_attribs[i] = element.attrib[i]
        for child in element: #Additional steps for handling node elements as part of ways
            if child.tag == 'nd':
                way_node_set = {"id": element.attrib["id"], "node_id": child.attrib["ref"], "position": node_count}
                way_nodes.append(way_node_set)
                node_count += 1 #Increment position value for next node   
    for child in element: #Independant method for handling tags, regardless of if they come from a way or node
        set_tags = {} #Short term attribute for compiling 
        if child.tag == 'tag':
            if problem_chars.match(child.attrib["k"]):
                continue #Ignore tags that contain invalid characters in the k tag
            elif is_maxspeed_invalid(child) or is_hov_invalid(child):
                continue #Skip tags that have been determined as outdated and to be cleaned
            elif LOWER_COLON.match(child.attrib["k"]):
                set_tags["type"] = child.attrib["k"].split(':', 1)[0] #Split k tags that contain : so type is recorded
                set_tags["key"] = child.attrib["k"].split(':', 1)[1]
                set_tags["id"] = element.attrib["id"]
                if is_street_name(child):
                    street_name = update_street_name(child.attrib["v"], STREET_MAPPING)
                    set_tags["value"] = street_name
                elif is_turn_lanes(child):
                    turn_lanes = update_turn_lanes(child.attrib["v"])
                    set_tags["value"] = turn_lanes
                else:
                    set_tags["value"] = child.attrib["v"]
            else:
                set_tags["type"] = default_tag_type
                if is_name1(child):
                    set_tags["key"] = "alt_name" #Updating name1 key to alt_name
                else:
                    set_tags["key"] = child.attrib["k"]
                set_tags["id"] = element.attrib["id"]
                set_tags["value"] = child.attrib["v"]
            tags.append(set_tags)
    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Function                      #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w', encoding="utf-8") as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w', encoding="utf-8") as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w', encoding="utf-8") as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w', encoding="utf-8") as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w', encoding="utf-8") as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()


        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    process_map(OSM_PATH)