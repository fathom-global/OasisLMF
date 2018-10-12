from __future__ import unicode_literals

__all__ = [
    'canonical_exposure_data',
    'coverage_type_ids',
    'keys_data',
    'keys_status_flags',
    'peril_ids',
    'write_input_files'
]

import string
import six

from itertools import chain
from chainmap import ChainMap
from collections import OrderedDict

import pandas as pd

from hypothesis import given
from hypothesis.strategies import (
    booleans,
    fixed_dictionaries,
    integers,
    just,
    lists,
    sampled_from,
    text,
    tuples,
)

from oasislmf.model_execution.files import (
    GUL_INPUT_FILES, 
    OPTIONAL_INPUT_FILES, 
    IL_INPUT_FILES, 
    TAR_FILE, INPUT_FILES,
)
from oasislmf.utils.coverage import (
    BUILDING_COVERAGE_CODE,
    CONTENTS_COVERAGE_CODE,
    OTHER_STRUCTURES_COVERAGE_CODE,
    TIME_COVERAGE_CODE,
)
from oasislmf.utils.peril import (
    PERIL_ID_FLOOD,
    PERIL_ID_QUAKE,
    PERIL_ID_SURGE,
    PERIL_ID_WIND,
)
from oasislmf.utils.status import (
    KEYS_STATUS_FAIL,
    KEYS_STATUS_NOMATCH,
    KEYS_STATUS_SUCCESS,
)


coverage_type_ids = [BUILDING_COVERAGE_CODE, CONTENTS_COVERAGE_CODE, OTHER_STRUCTURES_COVERAGE_CODE, TIME_COVERAGE_CODE]

keys_status_flags = [KEYS_STATUS_FAIL, KEYS_STATUS_NOMATCH, KEYS_STATUS_SUCCESS]

peril_ids = [PERIL_ID_FLOOD, PERIL_ID_QUAKE, PERIL_ID_QUAKE, PERIL_ID_WIND]

# Used simple echo command rather than ktools conversion utility for testing purposes
ECHO_CONVERSION_INPUT_FILES = {k: ChainMap({'conversion_tool': 'echo'}, v) for k, v in INPUT_FILES.items()}

def standard_input_files(min_size=0):
    return lists(
        sampled_from([target['name'] for target in chain(six.itervalues(GUL_INPUT_FILES), six.itervalues(OPTIONAL_INPUT_FILES))]),
        min_size=min_size,
        unique=True,
    )


def il_input_files(min_size=0):
    return lists(
        sampled_from([target['name'] for target in six.itervalues(IL_INPUT_FILES)]),
        min_size=min_size,
        unique=True,
    )


def tar_file_targets(min_size=0):
    return lists(
        sampled_from([target['name'] + '.bin' for target in six.itervalues(INPUT_FILES)]),
        min_size=min_size,
        unique=True,
    )


def canonical_exposure_data(num_rows=10, min_value=None, max_value=None):
    return lists(tuples(integers(min_value=min_value, max_value=max_value)), min_size=num_rows, max_size=num_rows).map(
        lambda l: [(i + 1, 1.0) for i, _ in enumerate(l)]
    )


def keys_data(
    from_ids=integers(min_value=1, max_value=10),
    from_peril_ids=just(PERIL_ID_WIND),
    from_coverage_type_ids=just(BUILDING_COVERAGE_CODE),
    from_area_peril_ids=integers(min_value=1, max_value=10),
    from_vulnerability_ids=integers(min_value=1, max_value=10),
    from_statuses=sampled_from(keys_status_flags),
    from_messages=text(min_size=1, max_size=100, alphabet=string.ascii_letters),
    size=None,
    min_size=1,
    max_size=10
):

    return lists(
        fixed_dictionaries(
            {
                'id': from_ids,
                'peril_id': from_peril_ids,
                'coverage_type': from_coverage_type_ids,
                'area_peril_id': from_area_peril_ids,
                'vulnerability_id': from_vulnerability_ids,
                'status': from_statuses,
                'message': from_messages
            }
        ),
        min_size=(size if size else min_size),
        max_size=(size if size else max_size)
    )


def write_input_files(
    keys,
    keys_file_path,
    exposures,
    exposures_file_path,
    profile_element_name='profile_element'
):
    heading_row = OrderedDict([
        ('id', 'LocID'),
        ('peril_id', 'PerilID'),
        ('coverage_type', 'CoverageTypeID'),
        ('area_peril_id', 'AreaPerilID'),
        ('vulnerability_id', 'VulnerabilityID'),
    ])

    pd.DataFrame(
        columns=heading_row.keys(),
        data=[heading_row]+keys,
    ).to_csv(
        path_or_buf=keys_file_path,
        index=False,
        encoding='utf-8',
        header=False
    )

    heading_row = OrderedDict([
        ('row_id', 'ROW_ID'),
        (profile_element_name, 'ProfileElementName'),
    ])
    exposures_df = pd.DataFrame(
        columns=heading_row.keys(),
        data=exposures
    )
    exposures_df[profile_element_name] = exposures_df[profile_element_name].astype(float)
    exposures_df.to_csv(
        path_or_buf=exposures_file_path,
        index=False,
        encoding='utf-8',
        header=True
    )
