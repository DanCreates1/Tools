#!/usr/bin/env python3
"""
ASCII spinning donut (torus) – pure Python version of the classic
donut.c demo.  The drawing uses the characters

    ".,-~:;=!*#$@"

as a grayscale ramp (dark → light).

Press Ctrl‑C to stop the animation.
"""

import math
import sys
import time
import os

# ----------------------------------------------------------------------
# configuration (feel free to tweak)
# ----------------------------------------------------------------------
WIDTH = 80                # number of columns in the terminal
HEIGHT = 22               # number of rows (22 gives the original appearance)
SIZE = WIDTH * HEIGHT
SHADES = ".,-~:;=!*#$@"    # 12 characters, from dark to bright

# step sizes for the two torus angles (in radians)
STEP_THETA = 0.07   # outer loop – around the big circle
STEP_PHI   = 0.02   # inner loop – around the tube

# rotation speed (radians added each frame)
A_SPEED = 0.04
B_SPEED = 0.02

# frame pause – roughly 30‑40 fps on a typical terminal
FRAME_TIME = 0.03
# ----------------------------------------------------------------------


def hide_cursor():
    """Tell the terminal to hide the text cursor."""
    sys.stdout.write("\x1b[?25l")
    sys.stdout.flush()


def show_cursor():
    """Restore the cursor when we quit."""
    sys.stdout.write("\x1b[?25h")
    sys.stdout.flush()


def clear_screen():
    """Clear everything once at the start – subsequent frames just reuse the buffer."""
    sys.stdout.write("\x1b[2J")
    sys.stdout.flush()


def main():
    # Enable ANSI escape codes on Windows (requires the `colorama` package)
    if os.name == "nt":
        try:
            import colorama  # noqa: F401
            os.system("")    # activates VT processing in newer consoles
        except ImportError:
            # If colorama is missing we still try – many modern Windows terminals
            # understand VT sequences out of the box.
            pass

    hide_cursor()
    clear_screen()

    # rotation angles
    A = 0.0   # rotation about X axis
    B = 0.0   # rotation about Z axis

    try:
        while True:
            # ----- buffers -------------------------------------------------
            # screen holds the character to be printed at each cell
            screen = [" "] * SIZE
            # zbuffer stores the largest 1/z (the nearest point) per cell
            zbuffer = [0.0] * SIZE

            # ----- loop over the torus surface ---------------------------
            theta = 0.0
            while theta < 2 * math.pi:
                # pre‑compute some trig once per outer loop
                sin_theta = math.sin(theta)
                cos_theta = math.cos(theta)

                phi = 0.0
                while phi < 2 * math.pi:
                    sin_phi = math.sin(phi)
                    cos_phi = math.cos(phi)

                    # ------- 3‑D point before rotation (R = 2, r = 1) ------
                    # (R + r·cosθ) is the distance of the point from the centre of the torus
                    # multiplied by cosφ / sinφ to get the x‑y position.
                    # z = r·sinθ
                    #   x = (2 + cosθ) * cosφ
                    #   y = (2 + cosθ) * sinφ
                    #   z = sinθ
                    # The code below uses a compact algebraic expansion that also
                    # incorporates the two rotations (A and B) and the perspective divide.

                    # ---- rotation components --------------------------------
                    sin_A = math.sin(A)
                    cos_A = math.cos(A)
                    sin_B = math.sin(B)
                    cos_B = math.cos(B)

                    # helper variables matching the original C code
                    c = sin_theta
                    d = cos_phi
                    e = sin_A
                    f = sin_phi
                    g = cos_A
                    h = d + 2.0

                    # perspective (1 / depth)
                    D = 1.0 / (c * h * e + f * g + 5.0)

                    # the rotated x‑y‑z before projection
                    l = cos_theta
                    m = cos_B
                    n = sin_B
                    t = c * h * g - f * e

                    # screen coordinates (centered, then offset a little)
                    x = int(40 + 30 * D * (l * h * m - t * n))
                    y = int(12 + 15 * D * (l * h * n + t * m))

                    # index into the flat buffers
                    idx = x + WIDTH * y

                    # ---- luminance (dot product with a light source) -------
                    # The original expression is an expanded form of the dot product.
                    N = int(8 * ((f * e - c * d * g) * m
                                 - c * d * e
                                 - f * g
                                 - l * d * n))

                    # ----- draw pixel if it is visible and nearer ------------
                    if 0 <= x < WIDTH and 0 <= y < HEIGHT and D > zbuffer[idx]:
                        zbuffer[idx] = D
                        # Clamp N to the valid range of shades
                        if N < 0:
                            N = 0
                        elif N >= len(SHADES):
                            N = len(SHADES) - 1
                        screen[idx] = SHADES[N]

                    phi += STEP_PHI
                theta += STEP_THETA

            # ----- output -------------------------------------------------
            # Move cursor to top‑left without clearing (we already erased each cell)
            sys.stdout.write("\x1b[H")
            for i, ch in enumerate(screen):
                sys.stdout.write(ch)
                if (i + 1) % WIDTH == 0:
                    sys.stdout.write("\n")
            sys.stdout.flush()

            # ----- update rotation -----------------------------------------
            A += A_SPEED
            B += B_SPEED

            # ----- control frame rate ---------------------------------------
            time.sleep(FRAME_TIME)

    except KeyboardInterrupt:
        # user pressed Ctrl‑C – clean up
        show_cursor()
        sys.stdout.write("\nDonut animation stopped.\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
