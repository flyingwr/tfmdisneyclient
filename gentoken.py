from numpy import base_repr
from random import randrange

def generate_token() -> str:
	return "-".join([base_repr(randrange(0x24 ** (3 + (i * 2))), 0x24).zfill(0) for i in range(1, 4)])