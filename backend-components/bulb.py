import asyncio
import time
import multiprocessing as mpc

from plugp100.common.credentials import AuthCredential
from plugp100.new.device_factory import connect, DeviceConnectConfiguration

class Bulb:

    def __init__(self, email, password, host):

        device_configuration = DeviceConnectConfiguration(
                host=host,
                credentials=AuthCredential(email, password)
            )

        async def create_dev():
            device = await connect(device_configuration)
            await device.update()
            return device

        self.loop   = asyncio.new_event_loop()
        self.device = self.loop.run_until_complete(create_dev())

        self.command_queue = mpc.Queue(50)
        self.commands_subprocess = mpc.Process(
            target = self._comand_on_subprocess
            )
        self.commands_subprocess.start()

    def _comand_on_subprocess(self):
        while True:
            if self.command_queue.empty():
                time.sleep(0.2)
                continue

            command = self.command_queue.get()

            if command == "turn-on":
                self.loop.run_until_complete(self.device.turn_on())
            
            if command == "turn-off":
                self.loop.run_until_complete(self.device.turn_off())

            if command.split(":")[0] == "color":
                self.loop.run_until_complete(
                        self.device.set_hue_saturation(
                            int(command.split(":")[1]),
                            int(command.split(":")[2])
                        )
                    )


    def turn_on(self):
        if not self.command_queue.full():
            self.command_queue.put("turn-on")

    def turn_off(self):
        if not self.command_queue.full():
            self.command_queue.put("turn-off")

    def set_hue_saturation(self, hue, sat):
        if not self.command_queue.full():
            self.command_queue.put("color:{}:{}".format(hue, sat))


## example
if __name__ == "__main__":
    from random import randint

    if __name__ == "__main__":
        b1 = Bulb(AuthCredential("emanuel.ionescu@nxp.com", "nxp12345"), "192.168.1.92")
        
        i = 0
        while True:
            i+= 1
            time.sleep(3)
            if i%2 == 0:
                b1.set_hue_saturation(randint(0, 360), 100)
            else:
                b1.turn_off()
