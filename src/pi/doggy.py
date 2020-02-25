#! /usr/bin/env python3
import argparse
import serial
import websockets
import asyncio
import random
import math

test_modes = ["off", "random", "counter", "wave"]

def counter(i):
    return str(i % 100)

def wave(i):
    return str(int(50*math.sin(i/5)) + 50)

def rand(i):
    return str(random.randint(0, 100))

async def main(args):
    if args.verbose:
        print("Started up in main mode")
    ser = serial.Serial(args.serial, 9600)
    while True:
        if args.verbose:
            print("Attempting connection")
        try:
            if args.uri:
                if args.verbose:
                    print("Using websocket")
                async with websockets.connect(args.uri) as ws:
                    if args.verbose:
                        print("Connection established")
                    while True:
                        while ser.in_waiting == 0:
                            pass


                        try:
                            line = ser.readline()
                            line = line.decode("UTF-8").strip()
                            if args.verbose:
                                print(line)
                            await ws.send(line)
                        except:
                            pass
            else:
                if args.verbose:
                    print("No websocket provided")
                while True:
                    while ser.in_waiting == 0:
                        pass
                    line = ser.readline()

                    print(line)
        except Exception as e:
            if args.verbose:
                print("Exception occured. Connection closed due to ", e)
                print("Trying connection again in 5 seconds")
            await asyncio.sleep(5)

async def test(args):
    if args.verbose:
        print("Started up in test mode")

    func = None

    if args.test == test_modes[1]:
        func = rand
    elif args.test == test_modes[2]:
        func = counter
    elif args.test == test_modes[3]:
        func = wave

    while True:
        if args.verbose:
            print("Attempting connection")
        i = 0
        try:
            if args.uri:
                if args.verbose:
                    print("Using websocket")
                async with websockets.connect(args.uri) as ws:
                    if args.verbose:
                        print("Connection established")
                    while  True:
                        await asyncio.sleep(.1)

                        line = func(i)

                        if args.verbose:
                            print(line)

                        await ws.send(line)
                        i += 1
            else:
                if args.verbose:
                    print("No websocket provided")
                while True:
                    await asyncio.sleep(.1)

                    line = func(i)

                    print(line)
                    i += 1
        except Exception as e:
            if args.verbose:
                print("Exception occured. Connection closed due to ", e)
                print("Trying connection again in 5 seconds")
            await asyncio.sleep(5)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read given serial port.')
    parser.add_argument('-s', '--serial', help='serial port (ex: /dev/ttyACM0)', type=str, default="/dev/ttyACM0")
    parser.add_argument('-u', '--uri', help='the uri to connect to', type=str)
    parser.add_argument('-v', '--verbose', help='set verbose print', action='store_true')
    parser.add_argument('--test', help='set to test modes (default is "off")', choices=test_modes, default=test_modes[0])

    args = parser.parse_args()

    if args.test == test_modes[0]:
        asyncio.run(main(args))
    else:
        asyncio.run(test(args))
