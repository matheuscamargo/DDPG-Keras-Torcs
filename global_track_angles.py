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

    def angle_in_rad_from_distance(self, distance_in_m):
        return 0.0

    def angle_delta_in_rad(self):
        return 0.0

class Turn(object):
    def __init__(self, radius, arc, is_right_turn):
        self.radius = radius
        self.arc = arc
        self.is_right_turn = 1 if is_right_turn else -1

    def print_info(self):
        print 'Radius: ', self.radius, \
              ' Arc: ', self.arc, \
              ' Length: ', self.get_length_in_m(), \
              ' Is right turn: ', self.is_right_turn

    def get_length_in_m(self):
        return 2 * math.pi * self.radius * self.arc / 360

    def angle_in_rad_from_distance(self, distance_in_m):
        if self.radius == 0:
            return 0
        arc = distance_in_m / self.radius
        return self.is_right_turn * arc

    def angle_delta_in_rad(self):
        return self.arc * self.is_right_turn

class TrackAngles(object):
    def __load_segments__(self, track_segments):
        for element in track_segments:
            segment_type = element.find(".//attstr[@name='type']")
            type_str = segment_type.attrib.get('val')

            if type_str == "str":
                segment_length = element.find(".//attnum[@name='lg']")
                length_str = segment_length.attrib.get('val')
                self.segments_list.append(Straight(float(length_str)))
            elif type_str == "lft" or type_str == "rgt":
                segment_radius = element.find(".//attnum[@name='radius']")
                segment_arc = element.find(".//attnum[@name='arc']")
                segment_type = element.find(".//attstr[@name='type']")
                radius_str = segment_radius.attrib.get('val')
                arc_str = segment_arc.attrib.get('val')
                type_str = segment_type.attrib.get('val')
                self.segments_list.append( \
                    Turn(float(radius_str), float(arc_str), type_str == 'rgt'))

    def __init__(self, track_path, number_of_angles, interval_in_m_between_angles):
        self.number_of_angles = number_of_angles
        self.interval = interval_in_m_between_angles
        self.segments_list = []
        content = open(track_path, 'r').read()
        # Remove lines starting with '&'
        content = re.sub(r"\n\s*&.*", "\n", content)
        tree = xml.fromstring(content)
        track_segments = tree.find(".//section[@name='Track Segments']")
        self.__load_segments__(track_segments)

    def get_angles_in_rad_from_distance(self, initial_distance_in_m):
        index = 0
        current_distance = 0.0
        while index < len(self.segments_list) and \
              self.segments_list[index].get_length_in_m() + current_distance < \
              initial_distance_in_m:
            current_distance += self.segments_list[index].get_length_in_m()
            index += 1
        if index > len(self.segments_list):
            # Querying a distance greater than the track length. Shouldn't happen.
            return []
        result = []
        current_distance_in_segment = initial_distance_in_m - current_distance
        accumulated_angle = \
            self.segments_list[index].angle_in_rad_from_distance(current_distance_in_segment)
        initial_angle = accumulated_angle
        while len(result) < self.number_of_angles:
            remaining_interval = self.interval
            remaining_segment_length = \
                self.segments_list[index].get_length_in_m() - current_distance_in_segment
            while remaining_interval >= remaining_segment_length:
                accumulated_angle += \
                    self.segments_list[index].angle_in_rad_from_distance(remaining_segment_length)
                remaining_interval -= remaining_segment_length
                index = (index + 1) % len(self.segments_list)
                remaining_segment_length = self.segments_list[index].get_length_in_m()
                current_distance_in_segment = 0
            current_distance_in_segment += remaining_interval
            accumulated_angle += \
                self.segments_list[index].angle_in_rad_from_distance(remaining_interval)
            result.append(accumulated_angle - initial_angle)
        return result

    def print_list_info(self):
        for element in self.segments_list:
            element.print_info()

def main():
    tracks_path = "../../gym_torcs/vtorcs-RL-color/data/tracks"
    track_xml = "/g-track-1/g-track-1.xml"
    angles = TrackAngles(tracks_path + track_xml, 220, 10)
    angles.print_list_info()

    print angles.get_angles_in_rad_from_distance(0)

if __name__ == "__main__":
    main()
