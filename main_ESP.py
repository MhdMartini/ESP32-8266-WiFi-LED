"""
ESP
"""
import network
import socket
import json
from machine import Pin
from time import sleep

LED = Pin(2, Pin.OUT)


class Controller:
    ESP_IP = None  # IP address of ESP device under its own Access Point
    NEW_IP = None  # IP address of ESP device under the user wi-fi
    MOBILE_IP = None  # IP address of the user
    MOBILE = None  # User socket object

    SSID = None  # User wi-fi name
    PASSWORD = None  # User wi-fi password
    PORT = 1111  # Socket port known by both the ESP and the user
    sock = None  # socket object

    def __init__(self):
        # Connect to wi-fi. First look for the json file containing the wi-fi credentials.
        # If file was not found, or if wi-fi connection failed (credentials changed), go into pair routine

        # ACTION dictionary links user-sent commands to functions
        self.ACTION = {
            "LED": self.toggle_led
        }

        try:
            # Try to open the json file. If successful, load credentials (dictionary)
            # otherwise, go to pair method
            with open('wifi.json') as json_file:
                credentials = json.load(json_file)
                self.SSID, self.PASSWORD = credentials.values()

            # Create station interface. Block until created
            self.wifi = network.WLAN(network.STA_IF)
            self.wifi.active(True)
            while not self.wifi.active():
                pass

            # Connect to wi-fi. Block until connected. Blink if connection was successful
            self.wifi.connect(self.SSID, self.PASSWORD)
            while not self.wifi.isconnected():
                pass
            self.blink()

            # Save the new IP address
            self.NEW_IP = self.wifi.ifconfig()[0]

        except:
            # If connection to user wi-fi failed, blink 6 times and go to pair function
            self.blink()
            self.blink()
            self.pair()

        finally:
            # After connection is successful, start listening for user commands
            # temp = list(self.wifi.ifconfig())
            # temp[0] = "10.0.0.167"
            # self.wifi.ifconfig(tuple(temp))
            self.get_commands()

    def pair(self):
        # Create AP wifi named after the IP address / Port of the ESP socket (e.g. 192.168.4.1,1111)
        # User application will parse this information to communicate with the ESP
        # Create socket server to receive mobile IP and credentials

        # Create Access Point. Block until created
        wifi = network.WLAN(network.AP_IF)
        wifi.active(True)
        while not self.wifi.active():
            pass

        # Save the IP address of the ESP Access Point.
        # Rename the AP to the AP's IP address and PORT to which the ESP's socket is bound
        self.ESP_IP = wifi.ifconfig()[0]
        essid = self.ESP_IP + "," + str(self.PORT)
        wifi.config(essid=essid)

        # Create socket TCP server bound to the advertised information,
        # and waiting for a "connect" request from the mobile application
        self.server = socket.socket()
        self.server.bind((self.ESP_IP, self.PORT))
        self.server.listen(1)

        # Save the socket object (mobile_temp) when the user connects successfully
        # This socket object is used to receive credentials from the user
        mobile_temp, _ = self.server.accept()

        sleep(0.01)
        # Receive credentials. Credentials format: <SSID>,<PASSWORD>,<IP-ADDRESS>
        credentials = mobile_temp.recv(1024).decode("utf-8")
        self.SSID, self.PASSWORD, self.MOBILE_IP = credentials.split(",")

        # Save credentials, then connect to internet.
        # Create a socket TCP client to "connect" to mobile server. This will automatically send
        # ESP socket object to the mobile user who will user this IP address to send all future commands
        with open("wifi.json", "w") as file:
            json.dump({"ssid": self.SSID, "password": self.PASSWORD}, file)

        wifi.active(False)
        while wifi.active():
            pass

        # Create a station object
        self.wifi = network.WLAN(network.STA_IF)

        # Activate and connect to wi-fi. Block until done,
        # then blink 3 times to indicate connection was successful
        self.wifi.active(True)
        while not self.wifi.active():
            pass
        self.wifi.connect(self.SSID, self.PASSWORD)
        while not self.wifi.isconnected():
            pass
        self.blink()

        # Save the new IP address
        self.NEW_IP = self.wifi.ifconfig()[0]

        # TODO: DELETE
        print("Connected successfully to", self.SSID)
        print("New IP is:", self.NEW_IP)

        while True:
            # Keep trying until the mobile user goes back to their network and create a socket server
            # successfully using the IP address they had sent to the ESP among the "credentials"
            # NOTE: After this process is done, TCP protocol is no longer used.
            # Both the user and the ESP will communicate over UDP (ESP is server)
            try:
                client = socket.socket()
                client.connect((self.MOBILE_IP, self.PORT))
                client.close()
                break

            except:
                # TODO: DELETE
                sleep(1)
                continue

    def blink(self, i=6):
        # Blink i/2 number of times.
        for _ in range(i):
            LED.value(not LED.value())
            sleep(0.2)

    def get_commands(self):
        # Create a socket UDP server and receive mobile commands
        esp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        esp.bind((self.NEW_IP, self.PORT))

        while True:
            command = esp.recv(1024).decode("utf-8")
            self.ACTION.get(command)()

    # Command Methods---------------------------------------------------------------------------------------------------
    def toggle_led(self):
        LED.value(not LED.value())


if __name__ == '__main__':
    user = Controller()
