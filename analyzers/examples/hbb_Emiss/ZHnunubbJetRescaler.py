from heppy.framework.analyzer import Analyzer
from heppy.configuration import Collider
from ROOT import TLorentzVector

import copy
import math

class ZHnunubbJetRescaler(Analyzer):

    def process(self, event):
        sqrts = Collider.SQRTS
        mZ = 91.
        pi = TLorentzVector(0, 0, 0, sqrts)
        jets = getattr(event, self.cfg_ana.jets)
        jets_rescaled = []
        setattr(event, self.cfg_ana.output, jets_rescaled)        
        if len(jets) == 0:
            return
        sump4 = TLorentzVector()
        for jet in jets:
            sump4 += jet.p4()
            # print jet
        a = sump4.Mag2()
        b = -pi * sump4 * 2.
        c = pi.Mag2() - mZ ** 2
        sqdelta = math.sqrt(b ** 2 -4*a*c)
        xmin = (-b - sqdelta) / (2 * a)
        xmax = (-b + sqdelta) / (2 * a)
        scaling_factor = xmin
## this solution leads to negative missing energy,
## going for the physical one
##        if abs(xmax-1) < abs(xmin-1):
##            scaling_factor = xmax
        # print xmin, xmax
        # print scaling_factor
        if self.cfg_ana.verbose:
            pi.Print()
            sump4.Print()
            print a, b, xmin, xmax, scaling_factor
        for jet in jets:
            jet_rescaled = copy.deepcopy(jet)
            jet_rescaled._tlv *= scaling_factor
            jets_rescaled.append(jet_rescaled)
            if self.cfg_ana.verbose:
                print jet
                print jet_rescaled
        
