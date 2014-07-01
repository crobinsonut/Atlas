# pylint: disable=line-too-long, invalid-name, bad-whitespace, trailing-whitespace, too-many-locals, line-too-long
# Partially autogenerated with SMOP version 0.22
# /OpenMDAO/dev/hschilli/latest/devenv/bin/smop lift_drag.m -o lift_drag.py
from math import sqrt, sin, cos, atan2
import numpy as np

from openmdao.lib.datatypes.api import Int, Float, Array, VarTree
from openmdao.main.api import Component, VariableTree


class Fblade(VariableTree):
    Fx = Array(units='N/m', desc='drag axis')
    Fz = Array(units='N/m', desc='lift axis')
    My = Array(desc='')
    Q  = Array(desc='Torque')
    P  = Array(desc='Power')
    Pi = Array(desc='')
    Pp = Array(desc='')


class LiftDrag(Component):
    """
    Computes lift and drag
    """

    Ns  = Int(iotype="in", desc="number of Elements")
    yN  = Array(iotype="in", desc='node locations')

    rho   = Float(iotype='in', desc='air density')
    visc  = Float(iotype='in', desc='air viscosity')
    vw    = Float(iotype='in', desc='wind')
    vc    = Float(iotype='in', desc='vertical velocity')
    Omega = Float(iotype='in', desc='Rotor angular velocity')

    r  = Array(iotype='in', desc='radial location of each element')
    vi = Array(iotype='in', desc='induced downwash distribution')
    c  = Array(iotype='in', desc='chord distribution')
    Cl = Array(iotype='in', desc='lift coefficient distribution')
    dr = Array(iotype='in', desc='length of each element')
    d  = Array(iotype='in', desc='spar diameter distribution')

    yWire     = Array(iotype='in', desc='location of wire attachment along span')
    zWire     = Float(iotype='in', desc='depth of wire attachement')
    tWire     = Float(iotype='in', desc='thickness of wire')
    chordFrac = Array(iotype='in', desc='')

    Cm  = Array(iotype='in', desc='')
    xtU = Array(iotype='in', desc='fraction of laminar flow on the upper surface')
    xtL = Array(iotype='in', desc='fraction of laminar flow on the lower surface')

    # outputs
    Re  = Array(iotype='out', desc='Reynolds number')
    Cd  = Array(iotype='out', desc='drag coefficients')
    phi = Array(iotype='out', desc='')
    Fblade = VarTree(Fblade(), iotype='out', desc='')

    def execute(self):
        # Pre-allocate output arrays
        self.Re = np.zeros(self.Ns)
        self.Cd = np.zeros(self.Ns)
        self.phi = np.zeros(self.Ns)
        self.Fblade.Fx = np.zeros(self.Ns)
        self.Fblade.Fz = np.zeros(self.Ns)
        self.Fblade.My = np.zeros(self.Ns)
        self.Fblade.Q = np.zeros(self.Ns)
        self.Fblade.P = np.zeros(self.Ns)
        self.Fblade.Pi = np.zeros(self.Ns)
        self.Fblade.Pp = np.zeros(self.Ns)

        # Compute lift and drag using full angles
        for s in range(self.Ns):
            # where vw is wind, vc is vertical velocity
            U = sqrt((self.Omega * self.r[s] + self.vw)**2 + (self.vc + self.vi[s])**2)

            # wing section
            if self.c[s] > 0.001:
                self.Re[s] = self.rho * U * self.c[s] / self.visc
                self.Cd[s] = self.dragCoefficientFit(self.Re[s], self.xtU[s], self.xtL[s])
                dL = 0.5 * self.rho * U**2 * self.Cl[s] * self.c[s] * self.dr[s]
                dD = 0.5 * self.rho * U**2 * self.Cd[s] * self.c[s] * self.dr[s]
            else:
                # root spar section
                self.Re[s] = self.rho * U * self.d[s] / self.visc
                if self.Re < 3500:
                    self.Cd[s] = -1e-10*self.Re[s]**3 + 7e-07*self.Re[s]**2 - 0.0013*self.Re[s] + 1.7397
                else:
                    self.Cd[s] = 1
                dL = 0
                dD = 0.5 * self.rho * U**2 * self.Cd[s] * self.d[s] * self.dr[s]

            # add wire drag
            for w in range(len(self.yWire)):
                if self.yN[s] < self.yWire[w]:
                    if self.yN[s + 1] < self.yWire[w]:
                        L = self.dr[s] * sqrt(self.zWire**2 + self.yWire[w]**2) / self.yWire[w]
                    else:
                        L = (self.yWire[w] - self.yN[s]) * sqrt(self.zWire**2 + self.yWire[w]**2) / self.yWire[w]
                    ReWire = self.rho * U * self.tWire / self.visc
                    CdWire = -1e-10*ReWire**3 + 7e-07*ReWire**2 - 0.0013*ReWire + 1.7397
                    dD = dD + 0.5 * self.rho * U**2 * CdWire * self.tWire * L

            self.phi[s] = atan2(self.vc + self.vi[s], self.vw + self.Omega * self.r[s])
            self.Fblade.Fz[s] = self.chordFrac[s] * (dL * cos(self.phi[s]) - dD * sin(self.phi[s]))
            self.Fblade.Fx[s] = self.chordFrac[s] * (dD * cos(self.phi[s]) + dL * sin(self.phi[s]))
            self.Fblade.My[s] = self.chordFrac[s] * (0.5 * self.rho * U**2 * self.Cm[s] * self.c[s] * self.c[s] * self.dr[s])
            self.Fblade.Q[s]  = self.Fblade.Fx[s] * self.r[s]
            self.Fblade.P[s]  = self.Fblade.Q[s]  * self.Omega
            self.Fblade.Pi[s] = self.chordFrac[s] * (dL * sin(self.phi[s]) * self.r[s] * self.Omega)
            self.Fblade.Pp[s] = self.chordFrac[s] * (dD * cos(self.phi[s]) * self.r[s] * self.Omega)

    def dragCoefficientFit(self, Re, xtU, xtL):
        """
        Computes the drag coefficient of an airfoil at Reynolds number Re,
        with thickness to chord ratio tc, and with xtcU and xtcL fraction of
        laminar flow on the upper and lower surfaces respectively.
        The result is a fit on existing HPH airfoils.
        """
        Cf15_15 = 0.6798*Re**(-0.283)
        Cf60_100 = 22.09*Re**(-0.604)

        xtc = xtU + xtL
        Cd = Cf15_15 + (Cf60_100 - Cf15_15)*(xtc - 0.3)/(1.6 - 0.3)
        return Cd
