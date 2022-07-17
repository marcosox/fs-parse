"""
"""
import sys

from bs4 import BeautifulSoup


def main():
    try:
        input_file = sys.argv[1]
    except KeyError:
        print(f"Usage: {sys.argv[0]} path/to/placement_file.xml")
        sys.exit(1)
    try:
        with open(input_file, "r") as infile:
            soup = BeautifulSoup(infile, "lxml")
    except FileNotFoundError:
        print(f"File not found")
        sys.exit(1)
    all_coords = []
    for child in soup.find_all("sceneryobject"):
        coords = (round(float(child['lat']), 6), round(float(child['lon']), 6))
        if coords in all_coords:
            print("found duplicate", child)
        else:
            all_coords.append(coords)
    print("done")


if __name__ == '__main__':
    main()
