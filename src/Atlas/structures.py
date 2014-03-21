import numpy as np

from math import pi, sqrt, sin, cos, atan2

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Array

from poperties import SparProperties, ChordProperties, WireProperties


class Strain(object):
    def __init__(self, Ns):
        self.top    = np.zeros(3, Ns + 1)
        self.bottom = np.zeros(3, Ns + 1)
        self.back   = np.zeros(3, Ns + 1)
        self.front  = np.zeros(3, Ns + 1)

        self.bending_x = np.zeros(1, Ns + 1)
        self.bending_z = np.zeros(1, Ns + 1)
        self.axial_y   = np.zeros(1, Ns + 1)
        self.torsion_y = np.zeros(1, Ns + 1)


class StrCalc(Component):

    # inputs
    yN    = Array(iotype='in', desc='node locations for each element along the span')

    R = Array(iotype='in', desc='description')
    b = Array(iotype='in', desc='description')
    cE = Array(iotype='in', desc='description')
    xEA = Array(iotype='in', desc='description')
    xtU = Array(iotype='in', desc='description')
    d = Array(iotype='in', desc='description')

    theta = Array(iotype='in', desc='wrap angle')
    nTube = Array(iotype='in', desc='number of tube layers')
    nCap = Array(iotype='in', desc='number of cap strips')

    Jprop = Array(iotype='in', desc='Properties at joint location for buckling analysis')

    yWire = Array(iotype='in', desc='description')
    zWire = Array(iotype='in', desc='description')
    tWire = Array(iotype='in', desc='description')
    TWire = Array(iotype='in', desc='description')
    TEtension = Array(iotype='in', desc='description')
    ycmax = Array(iotype='in', desc='description')
    lBiscuit = Array(iotype='in', desc='description')
    dQuad = Array(iotype='in', desc='description')
    thetaQuad = Array(iotype='in', desc='description')
    nTubeQuad = Array(iotype='in', desc='description')
    lBiscuitQuad = Array(iotype='in', desc='description')
    RQuad = Array(iotype='in', desc='description')
    hQuad = Array(iotype='in', desc='description')
    mElseRotor = Array(iotype='in', desc='description')
    mElseCentre = Array(iotype='in', desc='description')
    mElseR = Array(iotype='in', desc='description')
    mPilot = Array(iotype='in', desc='description')
    Fblade = Array(iotype='in', desc='description')
    presLoad = Array(iotype='in', desc='description')
    flags = Array(iotype='in', desc='description')

    # outputs
    Mtot = Array(iotype='out', desc='description')
    mChord = Array(iotype='out', desc='description')
    mQuad = Array(iotype='out', desc='description')
    mCover = Array(iotype='out', desc='description')
    mWire = Array(iotype='out', desc='description')

    EIx = Array(iotype='out', desc='description')
    EIz = Array(iotype='out', desc='description')
    EA = Array(iotype='out', desc='description')
    GJ = Array(iotype='out', desc='description')
    mSpar = Array(iotype='out', desc='description')

    q = Array(iotype='out', desc='description')
    EIQuad = Array(iotype='out', desc='description')
    GJQuad = Array(iotype='out', desc='description')

    # internal forces and strains
    Finternal = Array(iotype='out', desc='description')
    strain = Array(iotype='out', desc='description')

    # factor of safety for each failure mode
    fail = Array(iotype='out', desc='description')

    Ns = max(yN.shape) - 1  # number of elements
    dy = np.zeros(Ns, 1)
    for s in range(1, (Ns+1)):
        dy[(s-1)] = yN[(s + 1-1)] - yN[(s-1)]  # length of each element

    # Compute structural properties and mass of each element
    # ------------------------------------------------------

    spar = SparProperties(yN, d, theta, nTube, nCap, lBiscuit, flags.CFRPType)
    EIx = spar.EIx
    EIz = spar.EIz
    EA = spar.EA
    GJ = spar.GJ
    mspar = spar.mSpar

    joint = SparProperties(np.array([0, 1]).reshape(1, -1), Jprop.d,
                Jprop.theta, Jprop.nTube, Jprop.nCap, Jprop.lBiscuit, flags.CFRPType)
    EIxJ = joint.EIxJ
    EIzJ = joint.EIzJ
    EAJ = joint.EAJ
    GJJ = joint.GJJ
    mSparJ = joint.mSparJ

    chord = ChordProperties(yN, cE, d, flags.GWing, xtU)
    mChord = chord.mChord
    xCGChord = chord.xCGchord

    xCG = (xCGChord.dot(mChord) + xEA.dot(mSpar)) / (mChord + mSpar)

    if flags.Quad:
        lQuad = sqrt(RQuad**2 + hQuad**2)
        # EIxQuad, EIzQuad,EAQuad,GJQuad,mQuad = SparProperties(np.array([0,lQuad]).reshape(1,-1),dQuad,thetaQuad,nTubeQuad,np.array([0,0]).reshape(1,-1),lBiscuitQuad,flags)
        quad = SparProperties(np.array([0, lQuad]).reshape(1, -1), dQuad,
                    thetaQuad, nTubeQuad, np.array([0, 0]).reshape(1, -1),
                    lBiscuitQuad, flags)
        EIxQuad = quad.EIxQuad
        EIzQuad = quad.EIzQuad
        EAQuad = quad.EAQuad
        GJQuad = quad.GJQuad
        mQuad = quad.mQuad
        EIQuad = quad.EIx
    else:
        mQuad = 0
        EIQuad = 0

    if flags.Cover:
        mCover = (ycmax**2 * 0.0528 + ycmax * 0.605 / 4) * 1.15
    else:
        mCover = 0

    # RHOWire,EWire,ULTIMATEWire = WireProperties(flags.WireType)
    wire = WireProperties(flags.WireType)

    LWire = sqrt(zWire**2 + yWire**2)
    mWire = pi * (tWire / 2)**2 * wire.RHO * LWire

    if flags.Quad:
        Mtot = (np.sum(mSpar)*b + np.sum(mChord)*b + mWire*b + mQuad + mCover) * 4 + mElseRotor + mElseCentre + mElseR * R + mPilot
    else:
        Mtot = np.sum(mSpar)*b + np.sum(mChord)*b + mWire*b + mCover + mElseRotor + mElseCentre + mElseR * R + mPilot

    # FEM computation for structural deformations
    # -------------------------------------------

    # Initialize global stiffness matrix
    K = np.zeros((Ns + 1) * 6, (Ns + 1) * 6)
    F = np.zeros((Ns + 1) * 6, 1)

    # Create global stiffness maxtrix and force vector
    k = np.zeros(12, 12, Ns)

    for s in range(1, (Ns + 1)):

        # Local elastic stiffness matrix
        k[0,   0, (s-1)] = 12 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[0,   5, (s-1)] = -6 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[5,   0, (s-1)] = k[0, 5, (s-1)]
        k[0,   6, (s-1)] = -12 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[6,   0, (s-1)] = k[0, 6, (s-1)]
        k[0,  11, (s-1)] = -6 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[11,  0, (s-1)] = k[0, 11, (s-1)]
        k[1,   1, (s-1)] = EA[(s-1)] / dy[(s-1)]
        k[1,   7, (s-1)] = -EA[(s-1)] / dy[(s-1)]
        k[7,   1, (s-1)] = k[1, 7, (s-1)]
        k[2,   2, (s-1)] = 12 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[2,   3, (s-1)] = 6 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[3,   2, (s-1)] = k[2, 3, (s-1)]
        k[2,   8, (s-1)] = -12 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[8,   2, (s-1)] = k[2, 8, (s-1)]
        k[2,   9, (s-1)] = 6 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[9,   2, (s-1)] = k[2, 9, (s-1)]
        k[3,   3, (s-1)] = 4 * EIz[(s-1)] / dy[(s-1)]
        k[3,   8, (s-1)] = -6 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[8,   3, (s-1)] = k[3, 8, (s-1)]
        k[3,   9, (s-1)] = 2 * EIz[(s-1)] / dy[(s-1)]
        k[9,   3, (s-1)] = k[3, 9, (s-1)]
        k[4,   4, (s-1)] = GJ[(s-1)] / dy[(s-1)]
        k[4,  10, (s-1)] = -GJ[(s-1)] / dy[(s-1)]
        k[10,  4, (s-1)] = k[4, 10, (s-1)]
        k[5,   5, (s-1)] = 4 * EIx[(s-1)] / dy[(s-1)]
        k[5,   6, (s-1)] = 6 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[6,   5, (s-1)] = k[5, 6, (s-1)]
        k[5,  11, (s-1)] = 2 * EIx[(s-1)] / dy[(s-1)]
        k[11,  5, (s-1)] = k[5, 11, (s-1)]
        k[6,   6, (s-1)] = 12 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[6,  11, (s-1)] = 6 * EIx[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[11,  6, (s-1)] = k[6, 11, (s-1)]
        k[7,   7, (s-1)] = EA[(s-1)] / dy[(s-1)]
        k[8,   8, (s-1)] = 12 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)] * dy[(s-1)])
        k[8,   9, (s-1)] = -6 * EIz[(s-1)] / (dy[(s-1)] * dy[(s-1)])
        k[9,   8, (s-1)] = k[8, 9, (s-1)]
        k[9,   9, (s-1)] = 4 * EIz[(s-1)] / dy[(s-1)]
        k[10, 10, (s-1)] = GJ[(s-1)] / dy[(s-1)]
        k[11, 11, (s-1)] = 4 * EIx[(s-1)] / dy[(s-1)]

        # Perform dihedral and sweep rotations here if needed

        # Assemble global stiffness matrix
        K[(6*s - 4):(6*s + 6), (6*s - 4):(6*s + 6)] = \
            K[(6*s - 4):(6*s + 6), (6*s - 4):(6*s + 6)] + k[:, :, (s-1)]

        Faero = np.zeros(6, 1)
        if flags.Load == 0:  # include aero forces
            # aerodynamic forces
            xAC = 0.25
            Faero[0] = Fblade.Fx(s) / 2
            Faero[1] = 0
            Faero[2] = Fblade.Fz(s) / 2
            Faero[3] = Fblade.Fz(s) * dy[(s-1)] / 12
            Faero[4] = Fblade.My(s) / 2 + (xEA[(s-1)] - xAC) * cE[(s-1)] * Fblade.Fz(s) / 2
            Faero[5] = -Fblade.Fx(s) * dy[(s-1)] / 12

        Fg = np.zeros(6, 1)
        Fwire = np.zeros(12, 1)

        if (flags.Load == 0) or (flags.Load == 1):
            # gravitational forces
            g = 9.81
            Fg[0] = 0
            Fg[1] = 0
            Fg[2] = -(mSpar[(s-1)] + mChord[(s-1)]) * g / 2
            Fg[3] = -(mSpar[(s-1)] + mChord[(s-1)]) * g * dy[(s-1)] / 12
            Fg[4] = (xCG[(s-1)] - xEA[(s-1)]) * cE[(s-1)] * (mSpar[(s-1)] + mChord[(s-1)]) * g / 2
            Fg[5] = 0

            # Wire forces (using consistent force vector)
            for w in range(1, (max(yWire.shape) + 1)):
                if (yWire[(w-1)] >= yN[(s-1)]) and (yWire[(w-1)] < yN[(s + 1-1)]):
                    thetaWire = atan2(zWire, yWire[(w-1)])
                    a = yWire[(w-1)] - yN[(s-1)]
                    L = dy[(s-1)]
                    FxWire = -cos(thetaWire) * TWire[(w-1)]
                    FzWire = -sin(thetaWire) * TWire[(w-1)]
                    Fwire[0] = 0
                    Fwire[1] = FxWire * (1 - a / L)
                    Fwire[2] = FzWire * (2 * (a / L)**3 - 3 * (a / L)**2 + 1)
                    Fwire[3] = FzWire * a * ((a / L)**2 - 2 * (a / L) + 1)
                    Fwire[4] = 0
                    Fwire[5] = 0
                    Fwire[6] = 0
                    Fwire[7] = FxWire * (a / L)
                    Fwire[8] = FzWire * (- 2 * (a / L)**3 + 3 * (a / L)**2)
                    Fwire[9] = FzWire * a * ((a / L)**2 - (a / L))
                    Fwire[10] = 0
                    Fwire[11] = 0
                else:
                    Fwire = np.zeros(12, 1)

        Fpres = np.zeros(12, 1)

        if flags.Load == 2:
            # Prescribed point load (using consistent force vector)
            if (presLoad.y >= yN[(s-1)]) and (presLoad.y < yN[(s + 1-1)]):
                a = presLoad.y - yN[(s-1)]
                L = dy[(s-1)]
                Fpres[0] = 0
                Fpres[1] = 0
                Fpres[2] = presLoad.pointZ * (2 * (a / L)**3 - 3 * (a / L)**2 + 1)
                Fpres[3] = presLoad.pointZ * a * ((a / L)**2 - 2 * (a / L) + 1)
                Fpres[4] = presLoad.pointM * (1 - a / L)
                Fpres[5] = 0
                Fpres[6] = 0
                Fpres[7] = 0
                Fpres[8] = presLoad.pointZ * (- 2 * (a / L)**3 + 3 * (a / L)**2)
                Fpres[9] = presLoad.pointZ * a * ((a / L)**2 - (a / L))
                Fpres[10] = presLoad.pointM * (a / L)
                Fpres[11] = 0

            # Prescribed distributed load
            Fpres[0] = Fpres[0] + presLoad.distributedX * dy[(s-1)] / 2
            Fpres[1] = Fpres[1] + 0
            Fpres[2] = Fpres[2] + presLoad.distributedZ * dy[(s-1)] / 2
            Fpres[3] = Fpres[3] + presLoad.distributedZ * dy[(s-1)] * dy[(s-1)] / 12
            Fpres[4] = Fpres[4] + presLoad.distributedM * dy[(s-1)] / 2
            Fpres[5] = Fpres[5] - presLoad.distributedX * dy[(s-1)] * dy[(s-1)] / 12
            Fpres[6] = Fpres[6] + presLoad.distributedX * dy[(s-1)] / 2
            Fpres[7] = Fpres[7] + 0
            Fpres[8] = Fpres[8] + presLoad.distributedZ * dy[(s-1)] / 2
            Fpres[9] = Fpres[9] - presLoad.distributedZ * dy[(s-1)] * dy[(s-1)] / 12
            Fpres[10] = Fpres[10] + presLoad.distributedM * dy[(s-1)] / 2
            Fpres[11] = Fpres[11] + presLoad.distributedX * dy[(s-1)] * dy[(s-1)] / 12

        # Assemble global force vector
        F[((s-1)*6 + 0)] = F[((s-1)*6 + 0)] + Fpres[0] + Fwire[0] + Fg[0] + Faero[0]  # x force
        F[((s-1)*6 + 1)] = F[((s-1)*6 + 1)] + Fpres[1] + Fwire[1] + Fg[1] + Faero[1]  # y force
        F[((s-1)*6 + 2)] = F[((s-1)*6 + 2)] + Fpres[2] + Fwire[2] + Fg[2] + Faero[2]  # z force
        F[((s-1)*6 + 3)] = F[((s-1)*6 + 3)] + Fpres[3] + Fwire[3] + Fg[3] + Faero[3]  # x moment
        F[((s-1)*6 + 4)] = F[((s-1)*6 + 4)] + Fpres[4] + Fwire[4] + Fg[4] + Faero[4]  # y moment
        F[((s-1)*6 + 5)] = F[((s-1)*6 + 5)] + Fpres[5] + Fwire[5] + Fg[5] + Faero[5]  # z moment
        F[((s-1)*6 + 6)] = F[((s-1)*6 + 6)] + Fpres[6] + Fwire[6] + Fg[0] + Faero[0]  # x force
        F[((s-1)*6 + 7)] = F[((s-1)*6 + 7)] + Fpres[7] + Fwire[7] + Fg[1] + Faero[1]  # y force
        F[((s-1)*6 + 8)] = F[((s-1)*6 + 8)] + Fpres[8] + Fwire[8] + Fg[2] + Faero[2]  # z force
        F[((s-1)*6 + 9)] = F[((s-1)*6 + 9)] + Fpres[9] + Fwire[9] - Fg[3] - Faero[3]  # x moment
        F[((s-1)*6 + 10)] = F[((s-1)*6 + 10)] + Fpres[10] + Fwire[10] + Fg[4] + Faero[4]  # y moment
        F[((s-1)*6 + 11)] = F[((s-1)*6 + 11)] + Fpres[11] + Fwire[11] - Fg[5] - Faero[5]  # z moment

    # Add constraints to all 6 dof at root

    if flags.wingWarp > 0:  # Also add wingWarping constraint
        ii = np.array([])
        for ss in range(1, ((Ns + 1) * 7)):
            if (ss > 6) and (ss != flags.wingWarp*6 + 5):
                ii = np.array([ii, ss]).reshape(1, -1)
        Fc = F[(ii-1)]
        Kc = K[(ii-1), (ii-1)]
    else:
        Fc = F[6:]
        Kc = K[6:, 6:]

    # Solve constrained system
    qc = np.linalg.solve(Kc, Fc)

    if flags.wingWarp > 0:
        q[ii, 1] = qc
    else:
        q = np.array([0, 0, 0, 0, 0, 0, qc]).reshape(1, -1)

    # Compute internal forces and strains
    # -----------------------------------

    Ftemp = np.zeros(12, Ns)
    Finternal = np.zeros(6, Ns + 1)

    strain = Strain(Ns)

    for s in range(1, (Ns+1)):
        # Determine internal forces acting at the nodes of each element
        Ftemp[:, (s-1)] = -(k[:, :, (s-1)] * q[((s-1) * 6):(s-1) * 6 + 12] - F[((s-1) * 6 + 1-1):(s-1) * 6 + 12])
        Finternal[:, (s-1)] = Ftemp[0:6, (s-1)]

        # Determine strains at each node
        x_hat = d[(s-1)] / 2
        z_hat = d[(s-1)] / 2
        r_hat = d[(s-1)] / 2

        # Break out displacement vector for element
        qq = q[((s-1) * 6):(s-1) * 6 + 12]

        strain.bending_x[1, s] = -np.array([(-(6 * x_hat) / (dy[(s-1)]**2)),
                                            ((4 * x_hat) / dy[(s-1)]),
                                            ((6 * x_hat) / (dy[(s-1)]**2)),
                                            ((2 * x_hat) / dy[(s-1)])]).reshape(1, -1) \
                                 * np.array([qq[0], qq[5], qq[6], qq[11]]).reshape(1, -1).T

        strain.bending_z[1, s] = -np.array([(-(6 * z_hat) / (dy[(s-1)]**2)),
                                            ((-4 * z_hat) / dy[(s-1)]),
                                            ((+6 * z_hat) / (dy[(s-1)]**2)),
                                            ((-2 * z_hat) / dy[(s-1)])]).reshape(1, -1) \
                                 * np.array([qq[2], qq[3], qq[8], qq[9]]).reshape(1, -1).T

        strain.axial_y[1, s] = np.array([(-1 / dy[(s-1)]), (1 / dy[(s-1)])]).reshape(1, -1) \
                               * np.array([qq[1], qq[7]]).reshape(1, -1).T

        strain.torsion_y[1, s] = r_hat * np.array([(-1 / dy[(s-1)]), (1 / dy[(s-1)])]).reshape(1, -1) \
                                 * np.array([qq[4], qq[10]]).reshape(1, -1).T

        strain.top   [:, s] = np.array([+strain.bending_z(1, s) + strain.axial_y(1, s), 0, strain.torsion_y(1, s)]).reshape(1, -1).T
        strain.bottom[:, s] = np.array([-strain.bending_z(1, s) + strain.axial_y(1, s), 0, strain.torsion_y(1, s)]).reshape(1, -1).T
        strain.back  [:, s] = np.array([+strain.bending_x(1, s) + strain.axial_y(1, s), 0, strain.torsion_y(1, s)]).reshape(1, -1).T
        strain.front [:, s] = np.array([-strain.bending_x(1, s) + strain.axial_y(1, s), 0, strain.torsion_y(1, s)]).reshape(1, -1).T

    # Loads at the tip are zero
    Finternal[:, Ns] = np.array([0, 0, 0, 0, 0, 0]).reshape(1, -1).T

    # Strains at tip are zero
    strain.top   [:, Ns + 1] = np.array([0, 0, 0]).reshape(1, -1).T
    strain.bottom[:, Ns + 1] = np.array([0, 0, 0]).reshape(1, -1).T
    strain.back  [:, Ns + 1] = np.array([0, 0, 0]).reshape(1, -1).T
    strain.front [:, Ns + 1] = np.array([0, 0, 0]).reshape(1, -1).T

    # Strains at tip are zero
    strain.bending_x[1, Ns + 1] = 0
    strain.bending_z[1, Ns + 1] = 0
    strain.axial_y  [1, Ns + 1] = 0
    strain.torsion_y[1, Ns + 1] = 0

    # Compute factor of safety for each failure mode
    # ----------------------------------------------

    TQuad = np.sum(Fblade.Fz) * b - (np.sum(mSpar + mChord) * b + mElseRotor / 4) * 9.81

    # fail = FailureCalc(yN, Finternal, strain, d, theta, nTube, nCap, yWire, zWire, EIxJ, EIzJ, lBiscuit,
    #                    dQuad, thetaQuad, nTubeQuad, lBiscuitQuad, RQuad, hQuad, TQuad, EIQuad, GJQuad,
    #                    tWire, TWire, TEtension, flags)
    # return Mtot,mSpar,mChord,mQuad,mCover,mWire,EIx,EIz,EA,GJ,q,EIQuad,GJQuad,Finternal,strain,fail
