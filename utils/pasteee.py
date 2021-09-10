import aiohttp

api_url = "https://paste.ee/api"

async def new_paste(code: str) -> str:
	result = ""

	async with aiohttp.ClientSession() as session:
		async with session.post(api_url, data={
			"key": "public",
			"description": "",
			"paste": code,
			"expire": 300,
			"format": "simple"
		}) as response:
			if response.status == 200:
				result = await response.text()

	return result