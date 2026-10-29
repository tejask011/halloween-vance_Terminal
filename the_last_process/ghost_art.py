"""
Halloween & Ghost ASCII Art & Frame Animations for THE LAST PROCESS.
Designed for 100% stable rendering across all Windows PowerShell and CMD consoles.
"""

import sys
import time
import os

# Multi-frame animated floating ghost
GHOST_FRAMES = [
    r"""
           .-.
         .'   '.
        /  o   o\
        |   .-.  |
        \   \-/  /
         '.     .'
           | | |
           / / \ \
          '-'   '-'
    """,
    r"""
           .-.
         .'   '.
        /  O   O\
        |   '-'  |
        \  \---/ /
         '.     .'
          \ \ / /
           \ V /
          '-' '-'
    """,
    r"""
           .-.
         .'   '.
        /  o   o\
        |   ===  |
        \        /
         '.     .'
          (  |  )
           / | \
          '-' '-'
    """
]

# Skull glitch frames
SKULL_FRAMES = [
    r"""
          .---.
         /     \
        | () () |
         \  ^  /
          |||||
    """,
    r"""
         .x---x.
        /  X X  \
       |  ( ! )  |
        \  ===  /
         |||||||
    """,
    r"""
         .XXXXX.
        / [O] [O]\
       |    v    |
        \  ===  /
         | | | |
    """
]

# Gravestone Header
GRAVEYARD_BANNER = r"""
       .-'''''-.              .-'''''-.
      /  R.I.P.  \           /  R.I.P.  \
      |  VANCE   |           | ENTITY 0 |
      |  23:40   |           |  ACTIVE  |
     _|          |_         _|          |_
    |______________|       |______________|
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

def play_ghost_animation(console, theme_color="green", loops=1):
    """
    Renders floating ghost without cursor-up buffer corruption on Windows.
    Prints cleanly with slight pauses.
    """
    console.print(f"[{theme_color}]{GHOST_FRAMES[0]}[/{theme_color}]")
    time.sleep(0.3)

def play_skull_glitch(console, theme_color="red", loops=1):
    """
    Renders skull glitch cleanly.
    """
    console.print(f"[{theme_color}]{SKULL_FRAMES[1]}[/{theme_color}]")
    time.sleep(0.3)
