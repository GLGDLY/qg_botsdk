#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import edwards25519


class SigningKey:
    def __init__(self, a, prefix):
        self.a = a
        self.prefix = prefix

    @classmethod
    def from_seed(cls, seed: bytes):
        while len(seed) < 32:
            seed *= 2
        seed = seed[:32]
        h = edwards25519.sha512(seed)
        a = int.from_bytes(h[:32], "little")
        a &= (1 << 254) - 8
        a |= 1 << 254
        return cls(a, h[32:])

    def sign(self, message: bytes):
        A = edwards25519.point_compress(edwards25519.point_mul(self.a, edwards25519.G))
        r = edwards25519.sha512_fp(self.prefix + message)
        R = edwards25519.point_compress(edwards25519.point_mul(r, edwards25519.G))
        h = edwards25519.sha512_fp(R + A + message)
        s = edwards25519.sc_muladd(h, self.a, r)
        return R + s.to_bytes(32, "little")
