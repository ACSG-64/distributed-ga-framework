import os
from typing import Tuple

from shared.annotations.custom import UUID


def setup_settings_prompt() -> Tuple[UUID, int]:
    print('Set up settings')
    ex_id = input('> Experiment ID: ')
    ex_id = int(ex_id) if str.isdigit(ex_id) else ex_id
    cpu_cores_count = os.cpu_count()
    sample_size = input(f'> Sample size (default {cpu_cores_count}): ')
    sample_size = int(sample_size) if sample_size else cpu_cores_count
    return ex_id, sample_size
