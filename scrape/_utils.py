import re

def to_mins(text: str) -> int:
    mins_rgx = re.compile('([0-9]+) min')
    hrs_rgx = re.compile('([0-9]+) hr')
    
    mins = 0
    hrs = 0
    
    mins_match = mins_rgx.search(text)
    if mins_match is not None:
        mins = int(mins_match.group(1))
    
    hrs_match = hrs_rgx.search(text)
    if hrs_match is not None:
        hrs = int(hrs_match.group(1))
    
    return mins + 60 * hrs