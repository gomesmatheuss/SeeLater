from enum import Enum

class LoadStatus(Enum):
    JSON_IMPORTED = "json_imported"
    READY_FOR_LOAD = "ready_for_load"
    LOADING = "loading"
    LOAD_SUCCESS = "load_success"
    LOAD_FAILED = "load_failed"
    WATCHED = "watched"
    DELETED = "deleted"
    INCLUDED_BY_URL = "inclued_by_url"
