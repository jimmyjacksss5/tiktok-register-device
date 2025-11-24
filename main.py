import json
import random
import uuid
import string
import time
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs

import tls_client



def get_rand_from_file(path):
    with open(path, "r") as f:
        return random.choice(json.load(f))


def random_string(length, pattern="#"):
    out = ""
    for ch in pattern:
        if ch == "#":
            out += random.choice(string.digits)
        elif ch == "a":
            out += random.choice(string.ascii_lowercase)
        else:
            out += random.choice(string.ascii_letters + string.digits)

    while len(out) < length:
        out += random.choice(string.ascii_letters + string.digits)

    return out[:length]


def random_mac():
    return ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))


class TikTok:
    def __init__(self):
        self.session = tls_client.Session(
            client_identifier="chrome_120",
            random_tls_extension_order=True
        )

        self.device = {}
        self.sig = {}

    def generate_device(self):
        randDevice = get_rand_from_file("devices.json")
        randCarrier = get_rand_from_file("carriers.json")

        self.device = {
            "default": {
                "ac": "wifi",
                "channel": "googleplay",
                "aid": "1233",
                "app_name": "musical_ly",
                "version_code": "130211",
                "app_version": "13.2.11",
                "device_platform": "android",
                "ab_version": "13.2.11",
                "ssmix": "a",
                "device_type": randDevice[1],
                "device_brand": randDevice[0],
                "language": "en",
                "os_api": "25",
                "os_version": "7.1.2",
                "uuid": random_string(15, "#"),
                "openudid": random_string(15, "a#"),
                "manifest_version_code": "2019092901",
                "resolution": randDevice[2],
                "dpi": randDevice[3],
                "update_version_code": "2019092901",
                "app_type": "normal",
                "sys_region": "US",
                "is_my_cn": "0",
                "pass-route": "1",
                "mcc_mnc": randCarrier[0] + randCarrier[1],
                "pass-region": "1",
                "timezone_name": "America/New_York",
                "carrier_region_v2": randCarrier[0],
                "timezone_offset": "0",
                "build_number": "13.2.11",
                "region": "US",
                "uoo": "0",
                "app_language": "en",
                "carrier_region": "US",
                "locale": "en",
                "ac2": "wifi5g"
            },

            "user-agent": (
                f"com.zhiliaoapp.musically/2019092901 "
                f"(Linux; U; Android 7.1.2 en; {randDevice[1]}; "
                f"Build/{randDevice[1]}; Cronet/58.0.2991.0)"
            ),

            "mac": random_mac(),
            "google_aid": str(uuid.uuid4()),
            "clientudid": str(uuid.uuid4()),
            "carrier": randCarrier
        }

        return self.device


    def build_url(self, protocol, hostname, path, query: dict):
        query = dict(query)

        install_id = self.device.get("install_id")
        device_id = self.device.get("device_id")

        if install_id:
            query["iid"] = install_id

        if device_id:
            query["did"] = device_id
            query["device_id"] = device_id

        if hostname in ("log2.musical.ly", "api2.musical.ly"):
            query["_rticket"] = int(time.time() * 1000) * 1000
            query["ts"] = int(time.time())

        url = urlunparse((protocol, hostname, path, "", urlencode(query), ""))

        parsed = urlparse(url)
        qs = parse_qs(parsed.query)

        self.rticket = qs.get("_rticket", [None])[0]

        return {
            "href": url,
            "query": query
        }

    def register_device(self):
        protocol = "https"
        hostname = "log2.musical.ly"
        path = "service/2/device_register/"

        req_url = self.build_url(protocol, hostname, path, self.device["default"])
        print(req_url)

        body = {
            "magic_tag": "ss_app_log",
            "header": {
                "display_name": "TikTok",
                "update_version_code": 2019092901,
                "manifest_version_code": 2019092901,
                "aid": 1233,
                "channel": "googleplay",
                "appkey": "5559e28267e58eb4c1000012",
                "package": "com.zhiliaoapp.musically",
                "app_version": "13.2.11",
                "version_code": 130211,
                "sdk_version": "2.5.5.8",
                "os": "Android",
                "os_version": "7.1.2",
                "os_api": "25",
                "device_model": self.device["default"]["device_type"],
                "device_brand": self.device["default"]["device_brand"],
                "cpu_abi": "arm64-v8a",
                "density_dpi": self.device["default"]["dpi"],
                "resolution": self.device["default"]["resolution"],
                "language": "en",
                "mc": self.device["mac"],
                "access": "wifi",
                "carrier": self.device["carrier"][2],
                "mcc_mnc": self.device["default"]["mcc_mnc"],
                "google_aid": self.device["google_aid"],
                "openudid": self.device["default"]["openudid"],
                "clientudid": self.device["clientudid"],
                "tz_name": "America/New_York"
            },
            "_gen_time": int(time.time() * 1000)
        }


        headers = {
            "host": hostname,
            "sdk-version": "1",
            "content-type": "application/json; charset=utf-8",
            "user-agent": self.device["user-agent"],
        }

        r = self.session.post(
            req_url["href"],
            headers=headers,
            json=body
        )

        data = r.json()
        if data.get("new_user") == 1:
            self.device["install_id"] = data["install_id_str"]
            self.device["device_id"] = data["device_id_str"]

            print("[+] Device registered successfully.")
            print(f"    install_id (iid): {self.device['install_id']}")
            print(f"    device_id (did): {self.device['device_id']}")

            
    
        else:
            print("[-] Device registration failed or not a new device.")

        return data



if __name__ == "__main__":
    bot = TikTok()
    bot.generate_device()
    print(bot.register_device())
