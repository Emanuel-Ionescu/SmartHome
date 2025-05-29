from random import randint as rdint
from requests import get as GET, post as POST
import json
import time


class Controller:

    def __init__(self, HA_acces_token, HA_port_nr = 8123):

        self.url = "http://localhost:{}/api/".format(HA_port_nr)
        self.headers = {
            "Authorization" : "Bearer {}".format(HA_acces_token),
            "content-type" : "aplication/json"
        }

        self.services = json.loads(GET(self.url+"services", headers=self.headers).text)
        states   = json.loads(GET(self.url+"states",   headers=self.headers).text)

        self.devices = {}
        for i in range(len(states)):
            try:
                self.devices[ 
                    states[i]["attributes"]["friendly_name"] 
                    ] = states[i]
            except Exception as e:
                pass
                #print(states[i]["entity_id"], e)

    def list_devices(self):
        for dev_name in self.devices.keys():
            print("{} --> {} : {}".format(
                dev_name,
                self.devices[dev_name]["entity_id"],
                self.devices[dev_name]["state"]
            ))

    def set(self, device_name : str, state : str, args : dict = None):
        
        device_id = self.devices[device_name]["entity_id"]
        device_type = device_id.split('.')[0].lower()

        data = {}
        data["entity_id"] = device_id
        
        if args is not None:
            for key in args.keys():
                data[key] = args[key]

        response = POST(
            self.url+"services/{}/turn_{}".format(device_type, state.lower()),
            headers=self.headers,
            json=data
            )
        return response

    def get(self, device_name):

        device_id = self.devices[device_name]["entity_id"]

        response = GET(
            self.url+"states/{}".format(device_id),
            headers=self.headers
        )

        return json.loads(response.text)
        

if __name__ == "__main__":

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJlNDNhNWNmNGRlOGE0OGZmYWJmZTIyZmYzYTVmNTY1MCIsImlhdCI6MTcyNTk0NTU4NywiZXhwIjoyMDQxMzA1NTg3fQ.scMF5c8_gvAeQ1_akqqvCNUgZ4k8uXK6C6GBD8uQZMY"
    con = Controller(token)
    
    def setters():
        con.set("Outlet1", "ON")

        con.set("Bulb13", "OFF")
        time.sleep(1)
        con.set("Bulb13", "ON")
        time.sleep(1)

        #give some colors to bulb
        for i in range(10):
            con.set("Bulb13", "ON", {"rgb_color" : [rdint(0, 255), rdint(0, 255), rdint(0, 255)]})
            time.sleep(0.5)

        con.set("Outlet1", "OFF")
        time.sleep(1)
        con.set("Outlet1", "ON")
        time.sleep(1)
        con.set("Outlet1", "OFF")
        time.sleep(1)
        con.set("Outlet1", "ON")
        time.sleep(1)
        con.set("Outlet1", "OFF")
        time.sleep(1)
        con.set("Outlet1", "ON")

    def getters():
        for i in range(100):
            print("                                                                             ", end="\r")
            print(  "Outlet1 :", con.get("Outlet1")["state"], 
                  #"  Door1   :", con.get("LivingroomDoor")["state"], 
                 # "  Door2   :", con.get("EntranceDoor")["state"], 
                  "  Bulb13  :", con.get("Bulb13")["attributes"]["rgb_color"], end="\r")
            time.sleep(1)

    setters()

