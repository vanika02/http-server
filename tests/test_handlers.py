import json
import pytest 

import handlers

@pytest.fixture(autouse=True)
def reset_users():
    handlers.users.clear()