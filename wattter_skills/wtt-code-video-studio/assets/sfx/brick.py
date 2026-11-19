# SPDX-FileCopyrightText: 2026 Lemomo (LemoLab)
# SPDX-License-Identifier: MIT
# Upstream: core/audio/sfx.py @ 00a7f9ec99c8686265a8ca4ed9a3fdaaf27ea6f4 (selected functions).
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
_rng = np.random.default_rng(7)


def t_(d): return np.arange(int(round(d * SR))) / SR


def env_exp(d, tau): return np.exp(-t_(d) / tau)


def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)


def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)


def noise(d): return _rng.standard_normal(int(round(d * SR)))


def norm(x, p=1.0): m = np.abs(x).max(); return x * (p / m) if m > 0 else x


def click(pitch=1.0, v=1.0):
    """Plastic bricks snapping together: very short noise transient + two high resonances + a little low end"""
    d = .06; tt = t_(d)
    tr = hp(noise(d), 2500) * env_exp(d, .0015)
    res = sum(a * np.sin(2 * np.pi * f * pitch * tt + _rng.random() * 6) * env_exp(d, tau)
              for f, a, tau in [(2900, .6, .012), (4600, .4, .008), (1500, .35, .018)])
    body = np.sin(2 * np.pi * 190 * pitch * tt) * env_exp(d, .01) * .5
    return norm(tr * .8 + res + body) * v


def clack(pitch=1.0, v=1.0):
    """Brick dropped on a tabletop: the wood's mids + the plastic's highs"""
    d = .09; tt = t_(d); p = pitch * (.85 + _rng.random() * .3)
    x = hp(noise(d), 1200) * env_exp(d, .004) + sum(a * np.sin(2 * np.pi * f * p * tt) * env_exp(d, tau)
        for f, a, tau in [(1200, .6, .02), (2300, .5, .012), (380, .5, .03)])
    return norm(x) * v


def whoosh(d=.35, v=1.0):
    n = noise(d); tt = t_(d); out = np.zeros_like(n)
    for i in range(0, len(n), 480):   # swept bandpass
        hi = min(len(n), i + 480)     # when the last block is shorter than 480 samples, take its actual length (so it doesn't crash when d isn't a multiple of 0.01 s)
        f = 600 + 2600 * np.sin(np.pi * i / len(n)); seg = bp(n[max(0, i - 2000):hi], f * .7, f * 1.3)[-(hi - i):]; out[i:hi] = seg
    return norm(out * np.sin(np.pi * tt / d) ** 2) * v


def thump(v=1.0, f=70):
    d = .35; tt = t_(d)
    return norm(np.sin(2 * np.pi * f * tt * (1 - .3 * tt)) * env_exp(d, .07) + lp(noise(d), 300) * env_exp(d, .02) * .5) * v


def step(v=1.0):
    d = .05; tt = t_(d)
    return norm(hp(noise(d), 1800) * env_exp(d, .004) + np.sin(2 * np.pi * 2200 * tt) * env_exp(d, .006) * .5) * v


def ding(v=1.0):
    d = 1.6; tt = t_(d)
    x = sum(a * np.sin(2 * np.pi * f * tt) * env_exp(d, tau) for f, a, tau in [(1318, 1, .6), (2637, .5, .35), (3951, .3, .2), (1976, .25, .5), (5274, .15, .1)])
    return norm(x) * v


def pop(v=1.0):
    d = .18; tt = t_(d); f = 500 + 1400 * tt / d
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, .05)) * v
