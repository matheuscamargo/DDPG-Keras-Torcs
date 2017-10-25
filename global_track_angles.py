import xml.etree.ElementTree as xml
import re
import math

class Straight(object):
    def __init__(self, length):
        self.length = length

    def print_info(self):
        print 'Length: ', self.length

    def get_length_in_m(self):
        return self.length

    def angle_from_segment_start(self, distance_in_m):
        return 0.0

class Turn(object):
    def __init__(self, radius, arc):
        self.radius = radius
        self.arc = arc

    def print_info(self):
        print 'Radius: ', self.radius, \
              ' Arc: ', self.arc, \
              ' Length: ', self.get_length_in_m()

    def get_length_in_m(self):
        return 2 * math.pi * self.radius * self.arc / 360

    def angle_from_segment_start(self, distance_in_m):
        if self.get_length_in_m() == 0:
            return 0
        arc = self.arc * distance_in_m / self.get_length_in_m()
        return 90 - arc

def main():
    """Main function for testing"""
    tracks_path = "../../gym_torcs/vtorcs-RL-color/data/tracks"
    content = open(tracks_path + "/g-track-1/g-track-1.xml", 'r').read()

    # Remove lines starting with '&'
    content = re.sub(r"\n\s*&.*", "\n", content)

    tree = xml.fromstring(content)
    track_segments = tree.find(".//section[@name='Track Segments']")

    segments_list = []

    for element in track_segments:
        segment_type = element.find(".//attstr[@name='type']")
        type_str = segment_type.attrib.get('val')

        if type_str == "str":
            segment_length = element.find(".//attnum[@name='lg']")
            length_str = segment_length.attrib.get('val')
            segments_list.append(Straight(float(length_str)))
        elif type_str == "lft" or type_str == "rgt":
            segment_radius = element.find(".//attnum[@name='radius']")
            segment_arc = element.find(".//attnum[@name='arc']")
            radius_str = segment_radius.attrib.get('val')
            arc_str = segment_arc.attrib.get('val')
            segments_list.append(Turn(float(radius_str), float(arc_str)))

    for element in segments_list:
        element.print_info()

if __name__ == "__main__":
    main()
