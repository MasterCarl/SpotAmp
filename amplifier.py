#!/usr/bin/env python3
import sched
import socket
import threading
import time
import os

from rpi_rf import RFDevice


delay_seconds = 3 * 60

scheduler = sched.scheduler(time.time, time.sleep)
scheduled = None

rfdevice = RFDevice(17)
rfdevice.enable_tx()
rfdevice.tx_repeat = 10
CODE_ON = 5260625
CODE_OFF = 5260624


def turn_on():
    rfdevice.tx_code(CODE_ON, 1, 350, 24)


def turn_off():
    global scheduled
    scheduled = None
    print('turning off')
    rfdevice.tx_code(CODE_OFF, 1, 350, 24)


def run_scheduler_thread():
    thread = threading.Thread(target=scheduler.run, args=(), daemon=True)
    thread.start()


def cancel_scheduled_off():
    if scheduled is not None:
        print('cancelling scheduled off')
        try:
            scheduler.cancel(scheduled)
        except ValueError:
            pass


def schedule_off():
    print('scheduling off in', delay_seconds)
    global scheduled
    scheduled = scheduler.enter(delay_seconds, 1, turn_off, ())
    run_scheduler_thread()


last_message = None


def listen_for_udp():
    global last_message
    socket_path = '/tmp/amplifier/commands.sock'
    dirname = os.path.dirname(socket_path)
    original_umask = os.umask(0)

    if not os.path.exists(dirname):
        os.mkdir(dirname, 0o0777)
    try:
        os.unlink(socket_path)
    except OSError:
        if os.path.exists(socket_path):
            raise
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)  # UDP

    sock.bind(socket_path)
    os.chmod(socket_path, 0o0777)
    os.umask(original_umask)

    print(f'listening for UDP commands at {socket_path}')
    while True:
        data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        message = data.decode()
        print("received message:", message)
        if message == 'stop':
            cancel_scheduled_off()
            if last_message == 'stop':
                print('double stop, stopping now')
                last_message = None
                turn_off()
            else:
                schedule_off()
        elif message == 'start':
            cancel_scheduled_off()
            turn_on()
        last_message = message


thread = threading.Thread(target=listen_for_udp, args=(), daemon=True)
thread.start()  # Start the execution
thread.join()
