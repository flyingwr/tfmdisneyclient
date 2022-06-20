import secrets

def gen_token() -> str:
	return secrets.token_urlsafe(32)

def gen_browser_token() -> str:
	return secrets.token_hex(16)

if __name__ == "__main__":
	print(gen_token())