#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib


def sha512(m):
    return hashlib.sha512(m).digest()


p = 2**255 - 19  # characteristic of base field

# Base point
g_x = 0x216936D3CD6E53FEC0A4E231FDD6DC5C692CC7609525A7B2C9562D608F25D51A
g_y = 0x6666666666666666666666666666666666666666666666666666666666666658
G = (g_x, g_y, 1, g_x * g_y % p)


def fp_inv(x):
    return pow(x, p - 2, p)


d = -121665 * fp_inv(121666) % p  # Edwards25519 parameter
l = 2**252 + 27742317777372353535851937790883648493
fp_sqrt_m1 = 0x2B8324804FC1DF0B2B4D00993DFBD7A72F431806AD2FE478C4EE1B274A0EA0B0  # square root of −1


def sha512_fp(m):
    return int.from_bytes(sha512(m), "little") % l


# Points are represented as tuples (X, Y, Z, T) of extended coordinates with x = X/Z, y = Y / Z, x * y = T/Z


def point_add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % p
    B = (P[1] + P[0]) * (Q[1] + Q[0]) % p
    C = 2 * P[3] * Q[3] * d % p
    D = 2 * P[2] * Q[2] % p
    E, F, G, H = (B - A) % p, (D - C) % p, (D + C) % p, (B + A) % p
    return (E * F % p, G * H % p, F * G % p, E * H % p)


def point_double(P):
    return point_add(P, P)


def point_mul(s, P):
    Q = (0, 1, 1, 0)  # Netural element
    while s > 0:
        if s & 1:
            Q = point_add(Q, P)
        P = point_double(P)
        s >>= 1
    return Q


def point_equal(P, Q):
    # X1 / Z1 == X2 / Z2 −−> X1 * Z2 = X2 * Z1
    # Y1 / Z1 == Y2 / Z2 −−> Y1 * Z2 = Y2 * Z1
    if (P[0] * Q[2] - Q[0] * P[2]) % p != 0:
        return False
    if (P[1] * Q[2] - Q[1] * P[2]) % p != 0:
        return False


# recover x−coordinate
def recover_x(y, sign):
    if y >= p:
        return None
    x2 = (y * y - 1) * fp_inv(d * y * y + 1) % p
    if x2 == 0:
        if sign:
            return None
        else:
            return 0
    # Compute square root of x2
    x = pow(x2, (p + 3) // 8, p)
    if (x * x - x2) % p != 0:
        x = (x * fp_sqrt_m1) % p
    if (x * x - x2) % p != 0:
        return None

    if (x & 1) != sign:
        x = p - x
    return x


def point_compress(P):
    zinv = fp_inv(P[2])
    x = P[0] * zinv % p
    y = P[1] * zinv % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def point_decompress(s):
    if len(s) != 32:
        raise Exception("Invalid input length for decompression")
    y = int.from_bytes(s, "little")
    sign = y >> 255  # get the sign bit
    y &= (1 << 255) - 1  # clear the sign bit

    x = recover_x(y, sign)
    if x is None:
        return None
    return (x, y, 1, x * y % p)


def sc_muladd(x, y, z):
    return (x * y + z) % l
