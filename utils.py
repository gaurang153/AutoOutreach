import json

def load_accounts():
        try:
            with open("accounts.json", "r") as file:
                accounts = json.load(file)
        except FileNotFoundError:
            accounts = []
        return accounts