from math import inf, floor

class EllipticCurve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p

    # Add two points on the curve
    def add(self, p1, p2):
        x1,y1 = p1
        x2,y2 = p2

        if x1 == x2 and y1 == -y2:
            return (inf, inf)

        if p1 == (inf, inf):
            return p2
        if p2 == (inf, inf):
            return p1

        if p1 == p2:
            slope = ((3*pow(x1, 2, self.p) + self.a) * pow(2*y1, -1, self.p)) % self.p
        else:
            slope = ((y2 - y1) * pow(x2-x1, -1, self.p)) % self.p

        x3 = (slope**2 - x1 - x2) % self.p
        y3 = (slope*(x1-x3)-y1) % self.p
        return (x3, y3) 

    # Perform Scalar Multiplication by Double-and-Add Algorithm
    def multiply(self, p, n):
        r = (inf, inf)
        q = p
        while n > 0:
            if n % 2 == 1:
                r = self.add(r, q)
            q = self.add(q, q)
            n //= 2
        return r

    def multiply_alt(self, p, n):
        r = (inf, inf)
        while n > 0:
            r = self.add(r, r)
            if n % 2 == 1:
                r = self.add(r, p)
            n //= 2
        return r

class ECDH:
    def __init__(self, curve, G, nA, nB):
        self.curve = curve
        self.secret = self.multiply(G, nA*nB)


