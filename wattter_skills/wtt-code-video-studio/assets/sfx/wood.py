# SPDX-FileCopyrightText: 2026 Lemomo (LemoLab)
# SPDX-License-Identifier: MIT
# Upstream: styles/woodcut/demo/mix.py @ 00a7f9ec99c8686265a8ca4ed9a3fdaaf27ea6f4 (selected functions).
import numpy as np
from brick import SR, bp, lp, hp

rng = np.random.default_rng(7)


def t_(d): return np.arange(int(d * SR)) / SR


def nz(d): return rng.standard_normal(int(d * SR))


def env(d, a=.005, tau=.1):
    t = t_(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / tau)


def modal(parts, d, noise_amt=.0, click=.0):
    """parts: [(freq, amp, decay_s), ...] → struck object"""
    t = t_(d); y = np.zeros_like(t)
    for f, a, tau in parts: y += a * np.sin(2 * np.pi * f * t + rng.random() * 6) * np.exp(-t / tau)
    y *= np.minimum(1, t / .0015)
    if click: y[:int(.006 * SR)] += click * hp(nz(.006), 2500) * np.linspace(1, 0, int(.006 * SR))
    return y


def ins(y, s, i):
    i = max(0, i); e = min(len(y), i + len(s))
    if e > i: y[i:e] += s[:e - i]
    return y


def norm(x, p=1.): m = np.abs(x).max(); return x * p / m if m > 0 else x


def knife_bite(): return norm(modal([(180, 1, .04), (910, .5, .03), (2300, .3, .015)], .15, click=1.4) + .4 * bp(nz(.15), 2000, 6000) * env(.15, .001, .012), .9)


def paper_lay():
    d = .45; t = t_(d); y = lp(nz(d), 700) * np.sin(np.pi * t / d) ** 2 * .7
    th = modal([(95, 1, .05)], .2) * .5; ins(y, th, int(.3 * SR))
    return norm(y, .45)


def sum_shift(items, p):
    L = max(int((dt + len(y) / SR) * SR) for y, dt, g in items) + 10; out = np.zeros(L)
    for y, dt, g in items: i = int(dt * SR); ins(out, g * y, i)
    return norm(out, p)


def heap_rattle(): return sum_shift([(modal([(rng.uniform(900, 2600), 1, .05)], .12, click=.4), rng.uniform(.03, .3), rng.uniform(.1, .35)) for _ in range(6)], .25)


def clank(): return norm(modal([(880, 1, .12), (2120, .6, .08), (3390, .4, .05)], .5, click=1), .6)


def compass_drop(): return sum_shift([(modal([(2480, 1, .25), (5930, .4, .12)], .6, click=.7), 0, 1), (heap_rattle(), .02, .8), (modal([(2600, 1, .1)], .2, click=.5), .16, .35)], .7)


def wind(d, gust=1., lo=200, hi=1400):
    t = t_(d); x = nz(d); y = np.zeros_like(x)
    for f0, ph in [(lo, 0), (lo * 1.7, 2), (hi * .6, 4)]:
        y += bp(x, f0, f0 * 2.2) * (.5 + .5 * np.sin(2 * np.pi * (.13 + .05 * rng.random()) * t + ph)) ** 2
    return y * (.7 + .3 * gust * np.sin(2 * np.pi * .4 * t) ** 2)
