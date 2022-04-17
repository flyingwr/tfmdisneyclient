"""Read records spreadsheets of Transformice"""
from concurrent.futures import ThreadPoolExecutor
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
	result = {}

	spreadsheet = gc.open_by_key(key)

	with ThreadPoolExecutor() as executor:
		futures = [(
			executor.submit(
				spreadsheet.values_batch_get, [f"{cat}!B:B", f"{cat}!C:C", f"{cat}!D:D"]
			), executor.submit(
				spreadsheet.values_batch_get, [f"{cat}!J:J", f"{cat}!K:K", f"{cat}!L:L"]
			) if cat != "V" else None
		) for cat in cats]
		for left, right in futures:
			left = left.result()
			maps, players, times = (left["valueRanges"][i]["values"] for i in range(3))

			if (check_right := right is not None):
				right = right.result()
				rmaps, rplayers, rtimes = (right["valueRanges"][i]["values"] for i in range(3)[::-1]) # Reversed range

			last_player_key = 2
			for last_map_key in range(1, len(maps), 8):
				if (_map := maps[last_map_key]) and (map_code := _map[0]).startswith("@"):
					result[map_code] = temp = {}

					if (player := players[last_player_key]) and (_time := times[last_player_key]):
						temp["left"] = (player[0], _time[0])

					"""Dealing with reversed records"""
					if check_right:
						if last_map_key < len(rmaps) and last_player_key < len(rplayers):
							if (rplayer := rplayers[last_player_key]) and (rtime := rtimes[last_player_key]):
								temp["right"] = (rplayer[0], rtime[0])

				last_player_key += 8
				if last_player_key > len(players):
					break

	return result