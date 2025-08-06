from enum import Enum

class LoadStatus(Enum):
    JSON_IMPORTED = 1
    LOAD_SUCCESS = 2
    LOAD_FAILED = 3
    WATCHED = 4
    DELETED = 5
    INCLUDED_BY_URL = 6
    READY_FOR_LOAD = 7
    