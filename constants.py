from typing import Dict

from teams import Region

MAX_TEAMS_PER_REGION = 3

# Total EPT points + 1
BIG_M = 28161

DL_S26_TEAMS_PER_REGION: Dict[Region, int] = {
    Region.WEU: 3,
    Region.SA: 2,
    Region.SEA: 2,
    Region.NA: 1,
    Region.MESWA: 1,
    Region.CN: 2,
    Region.EEU: 1
}

# Print intermediate results
DEBUG_DL_S26 = False