import pytest
from model_bakery import baker


@pytest.fixture
def tag_a():
    return baker.make('Tag', nome='TagA')


@pytest.fixture
def tag_b():
    return baker.make('Tag', nome='TagB')


@pytest.fixture
def tag_c():
    return baker.make('Tag', nome='TagXpto')


@pytest.fixture
def payload_update_tag(tag_a):
    payload = {
        'nome': 'TagA - Updated',
    }
    return payload
