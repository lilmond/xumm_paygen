import requests
import os

def get_currency(wallet_address):
    return requests.get(f"https://api.xrpscan.com/api/v1/account/{wallet_address}/obligations?origin=https://xrpl.services").json()[0]["currency"]

def get_payload(payload_url):
    args_dict = {}
    args = payload_url.split("?", 1)[1].split("&")
    for arg in args:
        arg_name, arg_value = arg.split("=", 1)
        args_dict[arg_name] = arg_value
    
    if not "currency" in args_dict: return
    args_dict["currency"] = get_currency(args_dict["issuer"])

    payload = {
        "options": {
            "xrplAccount": None,
            "web": True,
            "referer": "https://xrpl.services/"
        },
        "payload": {
            "txjson": {
                "TransactionType": "TrustSet",
                "Flags": 131072,
                "LimitAmount": {
                    "issuer": args_dict["issuer"],
                    "currency": args_dict["currency"],
                    "value": args_dict["limit"]
                }
            },
            "custom_meta": {
                "instruction": f"Issuer Address: {args_dict['issuer']} #~ This payload is generated by XRP Paygen. ~#",
                "blob": {
                    "noSignIn": True
                }
            },
            "options": {
                "expire": 5
            }
        }
    }

    return payload

def generate_payload(payload):
    http = requests.post("https://api.xrpl.services/api/v1/platform/payload", json=payload, headers={"Origin": "https://xrpl.services/"})
    payload = http.json()
    uuid = payload["uuid"]

    return f"xumm://xrpl.services/sign/{uuid}/deeplink"

def main():
    try:
        payload_url = input("Payload URL: ").strip()
    except KeyboardInterrupt:
        return

    try:
        payload = get_payload(payload_url)
    except Exception:
        print(f"Error: Invalid Payload URL: {payload_url}")
        return

    while True:
        try:
            input(":PRESS ENTER TO GENERATE PAYLOAD:")
            try:
                url = generate_payload(payload)
            except Exception:
                print("Error: Unable to generate sign URL. Try again.")
                continue
            #print(f"Sign URL: {url}")
            os.system(f"termux-open-url {url}")
        except KeyboardInterrupt:
            return

if __name__ == "__main__":
    main()
