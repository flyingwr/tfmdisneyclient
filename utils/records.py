"""Read records spreadsheets of Transformice"""

from typing import Dict

import gspread
gc = gspread.service_account(filename="service_account_credentials.json")

# Supported categories of records
cats = ("P3", "P5", "P6", "P7", "P9", "P13", "P17", "P18", "P19", "V", "WJ")

def read_spreadsheet(key: str) -> Dict:
	"""Read a spreadsheet by key, which can be found in their URL: https://docs.google.com/spreadsheets/d/<KEY>

	:param str key: Key of a spreadsheet
	:returns: A dictionary with all records read
		>>> {
			"@123": {
				"left": ("Dummy", "20.21s"),
				"right": ("Dummy", "20.21s")
			}, ...
		}
	:rtype: dict
	"""

	_range = range(3)

	result = {}

	spreadsheet = gc.open_by_key(key)

	for cat in cats:
		left_side = spreadsheet.values_batch_get([f"{cat}!B:B", f"{cat}!C:C", f"{cat}!D:D"])
		maps, players, times = (left_side["valueRanges"][i]["values"] for i in _range)

		_reversed = None

		"""Fetching reversed records
		`V` category is not included as it has no reversed records
		"""
		if cat != "V":
			_reversed = spreadsheet.values_batch_get([f"{cat}!J:J", f"{cat}!K:K", f"{cat}!L:L"])
			rmaps, rplayers, rtimes = (_reversed["valueRanges"][i]["values"] for i in _range[::-1]) # Reversed range

		last_player_key = 2
		for last_map_key in range(1, len(maps), 8):
			_map = maps[last_map_key]
			if _map and "@" in _map[0]: # Check if value is truthy
				result[_map[0]] = temp = { "cat": cat }

				player, _time = players[last_player_key], times[last_player_key]
				if player and _time: # Check if value is truthy
					temp["left"] = (player[0], _time[0])

				"""Dealing with reversed records"""
				if _reversed is not None:
					if last_map_key < len(rmaps) and last_player_key < len(rplayers):
						rplayer, rtime = rplayers[last_player_key], rtimes[last_player_key]
						if rplayer and rtime: # Check if value is truthy
							temp["right"] = (rplayer[0], rtime[0])

			last_player_key += 8
			if last_player_key > len(players):
				break

	return result