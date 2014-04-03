import numpy as np
from math import pi, atan2

from openmdao.main.api import Assembly, Component
from openmdao.main.datatypes.api import Int, Float, Array, VarTree

from Atlas import AtlasConfiguration, DiscretizeProperties, Aero, Aero2, Structures, Fblade

# see: HeliCalc.m


class Results(Component):
    # inputs
    b          = Int(iotype='in', desc='number of blades')
    Ns         = Int(iotype='in', desc='number of elements')
    yN         = Array(iotype='in', desc='node locations')
    yE         = Array(iotype='in', desc='')
    cE         = Array(iotype='in', desc='chord of each element')
    Cl         = Array(iotype='in', desc='lift coefficient distribution')
    q          = Array(iotype='in', desc='deformation')
    phi        = Array(iotype='in', desc='')
    collective = Float(iotype='in', desc='collective angle in radians')
    fblade     = VarTree(Fblade(), iotype='in')

    # outputs
    di         = Array(iotype='out', desc='dihedral angle')
    alphaJig   = Array(iotype='out', desc='aerodynamic jig angle')
    Ttot       = Float(iotype='out', desc='')
    Qtot       = Float(iotype='out', desc='')
    MomRot     = Float(iotype='out', desc='')
    Ptot       = Float(iotype='out', desc='')

    def execute(self):
        # Compute aerodynamic jig angle
        self.alphaJig = np.zeros(self.cE.shape)

        qq = np.zeros((6, self.Ns+1))
        for s in range(1, self.Ns+1):
            qq[:, s] = self.q[s*6:s*6+6].T

        Clalpha = 2*pi
        for s in range(0, max(self.yN.shape)-1):
            self.alphaJig[s] = self.Cl[s] / Clalpha            \
                             - (qq[4, s] + qq[4, s+1]) / 2     \
                             + self.phi[s] - self.collective

        # Compute dihedral angle
        self.di = np.zeros((self.Ns, 1))
        for s in range(0, self.Ns):
            self.di[s] = atan2(qq[2, s+1] - qq[2, s], self.yN[s+1] - self.yN[s])

        # Compute totals
        self.Ttot   = np.sum(self.fblade.Fz.reshape(-1, 1) * np.cos(self.di)) * self.b * 4
        self.MomRot = np.sum(self.fblade.Fz.reshape(-1, 1) * self.yE)
        self.Qtot   = np.sum(self.fblade.Q)  * self.b * 4
        Pitot       = np.sum(self.fblade.Pi) * self.b * 4
        Pptot       = np.sum(self.fblade.Pp) * self.b * 4
        self.Ptot   = Pptot + Pitot


class AeroStructural(Assembly):
    """
    Performs an aerodynamic and structural computation on a single
    configuration given the full set of design parameters. The aerodynamic
    computation returns the thrust, torque, power, and induced velocity. The
    structural computation first computes the mass of the helicopter based on
    the structural description of the spars and chord lengths. It then
    computes the deformation of the spars, the strains, and the resulting
    factor of safety for each of the failure modes.
    """

    def configure(self):
        self.add('config', AtlasConfiguration())

        # Take parameterized properties and get property for each element
        self.add('discrete', DiscretizeProperties())
        self.connect('config.Ns',           'discrete.Ns')
        self.connect('config.ycmax',        'discrete.ycmax')
        self.connect('config.R',            'discrete.R')
        self.connect('config.c',            'discrete.c_in')
        self.connect('config.Cl',           'discrete.Cl_in')
        self.connect('config.Cm',           'discrete.Cm_in')
        self.connect('config.t',            'discrete.t_in')
        self.connect('config.xtU',          'discrete.xtU_in')
        self.connect('config.xtL',          'discrete.xtL_in')
        self.connect('config.xEA',          'discrete.xEA_in')
        self.connect('config.yWire',        'discrete.yWire')
        self.connect('config.d',            'discrete.d_in')
        self.connect('config.theta',        'discrete.theta_in')
        self.connect('config.nTube',        'discrete.nTube_in')
        self.connect('config.nCap',         'discrete.nCap_in')
        self.connect('config.lBiscuit',     'discrete.lBiscuit_in')

        # First run Aero calc with simple blade-element model. Lift is
        # accurate with this simple model since Cl is pre-defined
        self.add('aero', Aero())
        self.connect('config.b',            'aero.b')
        self.connect('config.R',            'aero.R')
        self.connect('config.Ns',           'aero.Ns')
        self.connect('discrete.yN',         'aero.yN')
        self.connect('config.dr',           'aero.dr')
        self.connect('config.r',            'aero.r')
        self.connect('config.h',            'aero.h')
        self.connect('config.ycmax[0]',     'aero.ycmax')
        self.connect('config.rho',          'aero.rho')
        self.connect('config.visc',         'aero.visc')
        self.connect('config.vw',           'aero.vw')
        self.connect('config.vc',           'aero.vc')
        self.connect('config.Omega',        'aero.Omega')
        self.connect('discrete.cE',         'aero.c')
        self.connect('discrete.Cl',         'aero.Cl')
        self.connect('discrete.d',          'aero.d')
        self.connect('config.yWire',        'aero.yWire')
        self.connect('config.zWire',        'aero.zWire')
        self.connect('config.tWire',        'aero.tWire')
        self.connect('discrete.Cm',         'aero.Cm')
        self.connect('discrete.xtU',        'aero.xtU')
        self.connect('discrete.xtL',        'aero.xtL')

        # Then run Structures Calc (simply to determine the spar
        # deflection for accurate ground effect computation)
        self.add('struc', Structures())
        self.connect('config.flags',        'struc.flags')
        self.connect('discrete.yN',         'struc.yN')
        self.connect('discrete.d',          'struc.d')
        self.connect('discrete.theta',      'struc.theta')
        self.connect('discrete.nTube',      'struc.nTube')
        self.connect('discrete.nCap',       'struc.nCap')
        self.connect('discrete.lBiscuit',   'struc.lBiscuit')
        self.connect('config.Jprop',        'struc.Jprop')
        self.connect('config.b',            'struc.b')
        self.connect('discrete.cE',         'struc.cE')
        self.connect('discrete.xEA',        'struc.xEA')
        self.connect('discrete.xtU',        'struc.xtU')
        self.connect('config.dQuad',        'struc.dQuad')
        self.connect('config.thetaQuad',    'struc.thetaQuad')
        self.connect('config.nTubeQuad',    'struc.nTubeQuad')
        self.connect('config.lBiscuitQuad', 'struc.lBiscuitQuad')
        self.connect('config.RQuad',        'struc.RQuad')
        self.connect('config.hQuad',        'struc.hQuad')
        self.connect('config.ycmax[0]',     'struc.ycmax')
        self.connect('config.yWire',        'struc.yWire')
        self.connect('config.zWire',        'struc.zWire')
        self.connect('config.tWire',        'struc.tWire')
        self.connect('config.TWire',        'struc.TWire')
        self.connect('config.TEtension',    'struc.TEtension')
        self.connect('config.mElseRotor',   'struc.mElseRotor')
        self.connect('config.mElseCentre',  'struc.mElseCentre')
        self.connect('config.mElseR',       'struc.mElseR')
        self.connect('config.R',            'struc.R')
        self.connect('config.mPilot',       'struc.mPilot')
        self.connect('aero.Fblade',         'struc.fblade')
        self.connect('config.presLoad',     'struc.presLoad')

        # Then run more accurate Vortex method
        self.add('aero2', Aero2())
        self.connect('config.b',            'aero2.b')
        self.connect('config.R',            'aero2.R')
        self.connect('config.Ns',           'aero2.Ns')
        self.connect('discrete.yN',         'aero2.yN')
        self.connect('config.dr',           'aero2.dr')
        self.connect('config.r',            'aero2.r')
        self.connect('config.h',            'aero2.h')
        self.connect('config.ycmax[0]',     'aero2.ycmax')
        self.connect('config.rho',          'aero2.rho')
        self.connect('config.visc',         'aero2.visc')
        self.connect('config.vw',           'aero2.vw')
        self.connect('config.vc',           'aero2.vc')
        self.connect('config.Omega',        'aero2.Omega')
        self.connect('discrete.cE',         'aero2.c')
        self.connect('discrete.Cl',         'aero2.Cl')
        self.connect('discrete.d',          'aero2.d')
        self.connect('config.yWire',        'aero2.yWire')
        self.connect('config.zWire',        'aero2.zWire')
        self.connect('config.tWire',        'aero2.tWire')
        self.connect('discrete.Cm',         'aero2.Cm')
        self.connect('discrete.xtU',        'aero2.xtU')
        self.connect('discrete.xtL',        'aero2.xtL')
        self.connect('struc.q',             'aero2.q')
        self.connect('config.anhedral',     'aero2.anhedral')

        # Perform structural calculation once more with more accurate idea of drag
        self.add('struc2', Structures())
        self.connect('config.flags',        'struc2.flags')
        self.connect('discrete.yN',         'struc2.yN')
        self.connect('discrete.d',          'struc2.d')
        self.connect('discrete.theta',      'struc2.theta')
        self.connect('discrete.nTube',      'struc2.nTube')
        self.connect('discrete.nCap',       'struc2.nCap')
        self.connect('discrete.lBiscuit',   'struc2.lBiscuit')
        self.connect('config.Jprop',        'struc2.Jprop')
        self.connect('config.b',            'struc2.b')
        self.connect('discrete.cE',         'struc2.cE')
        self.connect('discrete.xEA',        'struc2.xEA')
        self.connect('discrete.xtU',        'struc2.xtU')
        self.connect('config.dQuad',        'struc2.dQuad')
        self.connect('config.thetaQuad',    'struc2.thetaQuad')
        self.connect('config.nTubeQuad',    'struc2.nTubeQuad')
        self.connect('config.lBiscuitQuad', 'struc2.lBiscuitQuad')
        self.connect('config.RQuad',        'struc2.RQuad')
        self.connect('config.hQuad',        'struc2.hQuad')
        self.connect('config.ycmax[0]',     'struc2.ycmax')
        self.connect('config.yWire',        'struc2.yWire')
        self.connect('config.zWire',        'struc2.zWire')
        self.connect('config.tWire',        'struc2.tWire')
        self.connect('config.TWire',        'struc2.TWire')
        self.connect('config.TEtension',    'struc2.TEtension')
        self.connect('config.mElseRotor',   'struc2.mElseRotor')
        self.connect('config.mElseCentre',  'struc2.mElseCentre')
        self.connect('config.mElseR',       'struc2.mElseR')
        self.connect('config.R',            'struc2.R')
        self.connect('config.mPilot',       'struc2.mPilot')
        self.connect('aero2.Fblade',        'struc2.fblade')
        self.connect('config.presLoad',     'struc2.presLoad')

        self.add('results', Results())
        self.connect('config.b',            'results.b')
        self.connect('config.Ns',           'results.Ns')
        self.connect('discrete.yN',         'results.yN')
        self.connect('discrete.yE',         'results.yE')
        self.connect('discrete.cE',         'results.cE')
        self.connect('discrete.Cl',         'results.Cl')
        self.connect('struc2.q',            'results.q')
        self.connect('aero2.phi',           'results.phi')
        self.connect('config.collective',   'results.collective')
        self.connect('aero2.Fblade',        'results.fblade')

        self.driver.workflow.add('config')
        self.driver.workflow.add('discrete')
        self.driver.workflow.add('aero')
        self.driver.workflow.add('struc')
        self.driver.workflow.add('aero2')
        self.driver.workflow.add('struc2')
        self.driver.workflow.add('results')


if __name__ == "__main__":
    top = AeroStructural()
    top.run()
