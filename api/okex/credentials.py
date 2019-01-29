from lib.config import Config

config = Config()
creds = config.credentials("okex.json")

api_key = creds['apiKey']
pass_phrase = creds['passPhrase']
secret_key = creds['secretKey']
