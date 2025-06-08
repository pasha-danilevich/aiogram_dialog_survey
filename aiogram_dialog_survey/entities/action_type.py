from enum import StrEnum


class ActionType(StrEnum):
    ON_SELECT = "on_select"
    ON_INPUT_SUCCESS = "on_input_success"
    ON_MULTISELECT = "on_multiselect"

    ON_ACCEPT = "on_accept"
    ON_SKIP = "on_skip"
