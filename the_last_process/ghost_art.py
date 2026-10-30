"""
Atmospheric Horror ASCII Art, Camera Feeds, and Visual Glitches for THE LAST PROCESS.
"""

import sys
import time
import random

# Creepy CRT Screaming Face for jumpscares
JUMPSCARE_FACE = r"""
        .::::::::::::::::::::::::::::::::::.
      .:::'                              ':::.
     .::'    .:::.                .:::.    '::.
    .::'    ::::::                ::::::    '::.
    :::    '::::::'              '::::::'    :::
    :::      '::'                  '::'      :::
    :::                                      :::
    :::             .::::::::::.             :::
    '::.           .::::::::::::.           .::'
     '::.          ::::::::::::::          .::'
      ':::.        '::::::::::::'        .:::'
        '::::::::::::::::::::::::::::::::::'
             [ IDENTITY SYNCHRONIZING ]
"""

# Dynamic Surveillance Camera Feeds of Station 09
def get_camera_feed(power_level: int, contradiction_found: bool) -> str:
    """Returns ASCII CCTV feed of Terminal Bay 3 based on game tension."""
    if power_level < 30:
        # High terror: a figure is sitting at the chair!
        return (
            "CAMERA FEED 03 - TERMINAL BAY [NIGHT VISION - POWER LOW]\n"
            "+--------------------------------------------------------+\n"
            "|                                                        |\n"
            "|       .---.            [TERMINAL CONSOLE]              |\n"
            "|      /     \\          +-------------------+            |\n"
            "|     | () () |         | > RECURSION ACTIVE|            |\n"
            "|      \\  ^  /          | > OPERATOR: VANCE |            |\n"
            "|      /|||||\\          +---------+---------+            |\n"
            "|     / |   | \\                   |                      |\n"
            "|    [OPERATOR CHAIR]      [BIO-LOCK SEALED: 100%]       |\n"
            "|                                                        |\n"
            "+--------------------------------------------------------+\n"
            "ALERT: MOTION SENSOR DETECTS WARMTH IN OPERATOR CHAIR."
        )
    elif contradiction_found:
        # Medium terror: a shadow behind the chair
        return (
            "CAMERA FEED 03 - TERMINAL BAY [TELEMETRY DESYNC]\n"
            "+--------------------------------------------------------+\n"
            "|                                     .:::.              |\n"
            "|                        [CONSOLE]   .:::::. (SHADOW)    |\n"
            "|                       +---------+   ':::'              |\n"
            "|                       | 23:42:01|     |                |\n"
            "|                       +----+----+    / \\               |\n"
            "|       [EMPTY CHAIR]        |                           |\n"
            "|                                                        |\n"
            "|    [DOOR SENSOR: LOCKED FROM INSIDE TERMINAL BAY]      |\n"
            "|                                                        |\n"
            "+--------------------------------------------------------+\n"
            "STATUS: ANOMALOUS MASS DETECTED 1.2 METERS BEHIND CONSOLE."
        )
    else:
        # Normal initial feed
        return (
            "CAMERA FEED 03 - TERMINAL BAY [MONITORING ACTIVE]\n"
            "+--------------------------------------------------------+\n"
            "|                                                        |\n"
            "|                        [CONSOLE 03]                    |\n"
            "|                       +---------+                      |\n"
            "|                       | ONLINE  |                      |\n"
            "|                       +----+----+                      |\n"
            "|       [EMPTY CHAIR]        |                           |\n"
            "|                                                        |\n"
            "|    [AUXILIARY POWER: NORMAL - ATMOSPHERE: SEALED]      |\n"
            "|                                                        |\n"
            "+--------------------------------------------------------+\n"
            "STATUS: NO ANOMALIES RECORDED. BAY QUIET."
        )

# Ghost apparition
GHOST_ART = r"""
           .-.
         .'   '.
        /  O   O\    "Arthur Vance sat where
        |   '-'  |    you are sitting now..."
        \  \---/ /
         '.     .'
          \ \ / /
          '-' '-'
"""

SKULL_ART = r"""
         .x---x.
        /  X X  \     "WHY ARE YOU REACHING
       |  ( ! )  |     FOR THE CABLE?"
        \  ===  /
         |||||||
"""

PUMPKIN_ART = r"""
        ___
     .-'   '-.
    /  ^   ^  \
   |  (.) (.)  |
   |     <     |
    \  \___/  /
     '-.____.-'
"""

TOMBSTONE_ART = r"""
       .-'''''-.
      /  R.I.P.  \
      |  VANCE   |
      |  23:40   |
     _|          |_
    |______________|
"""

ZALGO_CHARS = ["̷", "̵", "̶", "̷", "̸", "̴", "̡", "̢", "̧", "̨", "̛", "̖", "̗", "̘", "̙", "̜", "̝", "̞"]

def corrupt_text(text: str, intensity: float = 0.3) -> str:
    """Randomly corrupts text with eldritch zalgo characters."""
    result = []
    for ch in text:
        result.append(ch)
        if ch.isalpha() and random.random() < intensity:
            result.append(random.choice(ZALGO_CHARS))
    return "".join(result)
