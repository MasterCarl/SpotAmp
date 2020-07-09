#!/usr/bin/env bash
echo -n "$PLAYER_EVENT" | nc -uU -w0 /tmp/amplifier/commands.sock
