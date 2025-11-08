from dotenv import load_dotenv
import os

load_dotenv("infra/.env")

print(os.getenv("POSTGRES_DB"))
