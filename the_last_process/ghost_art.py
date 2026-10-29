"""
Halloween & Ghost ASCII Art & Frame Animations for THE LAST PROCESS.
"""

import sys
import time

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
          / /   \ \
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
           / . \
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
           \ | /
           / | \
          '-' '-'
    """
]

# Skull glitch frames for high suspicion / contradiction moments
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

# Halloween Jack-o'-Lantern monitor
PUMPKIN_ART = r"""
        ___
     .-'   '-.
    /  ^   ^  \
   |  (.) (.)  |
   |     <     |
    \  \___/  /
     '-.____.-'
"""

# Tombstone
TOMBSTONE_ART = r"""
       .-'''''-.
      /  R.I.P.  \
      |  VANCE   |
      |  23:40   |
     _|          |_
    |______________|
"""

# Cobweb corner
COBWEB_LEFT = r"""
\  |  /
 \ | /
--\|/--
  /|\
"""

def play_ghost_animation(console, theme_color="green", loops=2, delay=0.18):
    """Plays an in-terminal animated floating ghost apparition."""
    for _ in range(loops):
        for frame in GHOST_FRAMES:
            # Print frame with themed phosphor glow
            console.print(f"[{theme_color}]{frame}[/{theme_color}]")
            time.sleep(delay)
            # Move cursor up to overwrite frame if possible, or create flowing illusion
            sys.stdout.write(f"\033[{frame.count(chr(10)) + 1}A\r")
            sys.stdout.flush()
    # Final clear of cursor line
    sys.stdout.write("\n" * (GHOST_FRAMES[0].count(chr(10)) + 1))
    sys.stdout.flush()

def play_skull_glitch(console, theme_color="red", loops=3, delay=0.1):
    """Plays an animated chattering glitch skull when suspicion spikes."""
    for _ in range(loops):
        for frame in SKULL_FRAMES:
            console.print(f"[{theme_color}]{frame}[/{theme_color}]")
            time.sleep(delay)
            sys.stdout.write(f"\033[{frame.count(chr(10)) + 1}A\r")
            sys.stdout.flush()
    sys.stdout.write("\n" * (SKULL_FRAMES[0].count(chr(10)) + 1))
    sys.stdout.flush()
