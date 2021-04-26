from dotenv import dotenv_values

config = dotenv_values(".env")

DB_URI = config["DB_URI"]
