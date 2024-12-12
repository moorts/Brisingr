from sage.all import *
import sage

class TwistedEdwardsCurvePoint:
    def __init__(self, curve, u, v):
        self.curve = curve
        self.u = u
        self.v = v

class TwistedEdwardsCurve:
    def __init__(self, field, params, normalize=True):
        """Create n (twisted) edwards curve, i.e. a curve of the form:
            a*x^2 + y^2 = 1 + d*x^2*y^2.
        """
        self.Fp = field
        self.a, self.d = params

        if self.Fp.characteristic() == 2:
            raise NotImplementedError("Fields with characteristic 2 are not supported.")

        self.is_twisted = self.a == 1

        # Step 1: Convert to montgomery curve parameters.

        self.A = Fp(2)*(self.a + self.d)/(self.a - self.d)
        self.B = Fp(4)/(self.a - self.d)

        if normalize and kronecker(self.B, self.Fp.order()) != 1:
            raise NotImplementedError("Can only normalize if B is a quadratic residue (?).")

        if normalize:
            self.scalar_factor = self.B.sqrt().inverse()
            self.normalize = True

        # Step 2: Convert to weierstrass curve parameters.

        a = (3 - self.A**2)/(3*self.B**2)
        b = (2*self.A**3 - 9*self.A)/(27*self.B**3)

        self.curve = EllipticCurve(Fp, [a, b])

        self.montgomery_model, self.to_montgomery = self.curve.montgomery_model(morphism=True)

        if type(self.to_montgomery) == sage.schemes.elliptic_curves.weierstrass_morphism.WeierstrassIsomorphism:
            self.to_weierstrass = self.to_montgomery.dual()
        else:
            self.to_weierstrass = self.to_montgomery.inverse()


    def lift_y(self, y):
        x_squared = (1 - y**2)/(self.a - self.d*y**2)

        x = x_squared.sqrt()

        return x

    def __call__(self, u, v, montgomery=True):
        # Convert to montgomery point.
        u, v = self.Fp(u), self.Fp(v)
        mx = (1+v)/(1-v)
        my = (1+v)/((1-v)*u)

        if self.normalize:
            my = my / self.scalar_factor

        if montgomery:
            return self.montgomery_model(mx, my)

        return self.to_weierstrass(self.montgomery_model(mx, my))

Fp = GF(pow(2, 255) - 19)
a = Fp(-1)
d = -Fp(121665)/Fp(121666)

curve = TwistedEdwardsCurve(Fp, [a, d])

Bx, By = (9, 14781619447589544791020593568409986887264606134616475288964881837755586237401)

y = Fp(4)/Fp(5)
x = curve.lift_y(y)

print(curve(x, y, montgomery=False))
