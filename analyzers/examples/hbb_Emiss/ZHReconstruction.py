from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance2 as Resonance

import pprint 
#import itertools
#import copy

mass = {23: 91, 25: 125}

class ZHReconstruction(Analyzer):
#you dont really need this class. you can just compute mvis*sclaing_fac in the ROOT macro. 
    def process(self, event):
        jets = getattr(event, self.cfg_ana.input_jets)
        setattr(event, self.cfg_ana.output_higgs, Resonance(jets[0],jets[1],25))
