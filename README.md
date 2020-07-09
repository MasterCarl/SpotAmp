# SpotAmp

This project transforms a vintage amplifier setup into an internet-connected Spotify speaker that turns on and
off automatically as you start and stop the music from e.g. your phone.

I included a turn-off delay in case the music only stops briefly.

## Components
1. Any basic amplifier
1. A Raspberry Pi running Raspberry OS (Debian-based), additional (e.g. USB) sound card recommended
1. A 433 MHz transmitter and corresponding switched socket that turns the amplifier on and off

## Setup
First, you need to connect your Raspberry Pi to your amplifier and to the internet.

Then, you need to install and set up [Raspotify](https://dtcooper.github.io/raspotify/).

Clone this repository to your Raspberry Pi and change to the new directory.
Install the rpi-rf dependency by running
```bash
python3 -m pip install rpi-rf
```
Now, change the rpi-rf codes defined in `amplifier.py` to match your setup.
I encourage you to test this setup (try `python -i amplifier.py`).

Then, copy the required scripts to /usr/local/ by running
```bash
sudo cp send_amp.sh amplifier.py /usr/local/
```

Copy and enable the systemd service by running
```bash
sudo cp systemd/amplifier.service /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable amplifier.service
sudo systemctl start amplifier.service
```

You can test the setup by running
```bash
echo -n start | nc -uU -w0 /tmp/amplifier/commands.sock
```
The amplifier should now turn on.

Now, to connect it to raspotify:
In `/etc/default/raspotify`, uncomment the OPTIONS line and add `--onevent /usr/local/send_amp.sh`, e.g.:
```
OPTIONS="--device hw:1,0 --onevent /usr/local/send_amp.sh"
```

---
That's it! You should now have a speaker setup that turns on or off with your music!
