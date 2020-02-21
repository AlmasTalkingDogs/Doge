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
        print("Started up")
    ser = serial.Serial(args.serial, 9600)
    try:
        if args.uri:
            if args.verbose:
                print("Using websocket")
            async with websockets.connect(args.uri) as ws:
                while True:
                    print(ws)
                    while ser.in_waiting == 0:
                        pass

                    line = ser.readline()

                    if args.verbose:
                        print(line)

                    await ws.send(line)
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
        pass

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

    i = 0
    try:
        if args.uri:
            if args.verbose:
                print("Using websocket")
            async with websockets.connect(args.uri) as ws:
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
        pass



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
