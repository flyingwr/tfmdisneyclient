from aiohttp import web
from gentoken import generate_token

import cryptjson
import json
import loadfiles
import os

class Api:
	def __init__(self):
		self.tokens = []
		
		loadfiles.read_files("./data")
		self.main_data = cryptjson.json_zip(loadfiles.data).decode()

		with open("config.json") as f, open("swfdata.json") as _f:
			config = json.load(f)
			self.vip_list = config["vip_list"]
			self.update_url = config["update_url"]
			self.version = config["version"]

			self.swf_data = cryptjson.text_encode(_f.read()).decode()

			print("Server data has been loaded.")
		
	async def auth(self, request):
		response = {}
		response['success'] = False
		status = 401

		key = request.query.get("key")
		client_version = request.query.get("version")

		if key is not None:
			if key in self.vip_list.keys():
				if client_version == self.version:
					response['success'] = True

					access_token = generate_token()
					self.tokens.append(access_token)

					response['access_token'] = access_token
					response['level'] = self.vip_list[key]
					status = 200
				else:
					response['error'] = 'outdated version'
					response['update_url'] = self.update_url
					status = 406
			else:
				response['error'] = 'invalid key'
		else:
			response['error'] = 'invalid query'

		return web.json_response(response, status=status)

	async def get_data(self, request):
		response = {}
		response['success'] = False
		status = 401

		access_token = request.query.get("access_token")
		data_type = request.query.get("data_type")
		if access_token is not None and data_type is not None:
			if access_token in self.tokens:
				response['success'] = True
				for name in data_type.split("-"):
					response[name + "_data"] = getattr(self, name + "_data")

				status = 200

				self.tokens.remove(access_token)
			else:
				response['error'] = 'expired/invalid access_token'
		else:
			response['error'] = 'invalid query'

		return web.json_response(response, status=status)

if __name__ ==  '__main__':
	app = web.Application()
	endpoint = Api()

	app.router.add_get('/auth', endpoint.auth)
	app.router.add_get('/get_data', endpoint.get_data)
	web.run_app(app, port=os.getenv("PORT"))