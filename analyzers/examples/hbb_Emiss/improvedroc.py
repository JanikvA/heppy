import heppy.statistics.rrandom as random
import math
from heppy.framework.analyzer import Analyzer

class BTagger(Analyzer):
    def process(self, event):
        jets = getattr(event, self.cfg_ana.input_jets)
        for jet in jets:
            jet.tags['ctag']=0
            jet.tags['btag']=0
            jet.tags['udsgtag']=0
            if jet.match and jet.match.match and abs(jet.match.match.pdgid())==5:
                eff = 0.85*math.tanh(0.0025*jet.pt())*(25.0/(1+0.063*jet.pt()))
                jet.tags['btag']=1
            elif jet.match and jet.match.match and abs(jet.match.match.pdgid())==4:
                eff = 0.25*math.tanh(0.018*jet.pt())*(1/(1+ 0.0013*jet.pt()))
                jet.tags['ctag']=1
            elif jet.match and jet.match.match and (abs(jet.match.match.pdgid()) in [1,2,3,21]):
                eff = 0.01+0.000038*jet.pt()
                jet.tags['udsgtag']=1
            else:
                eff = 0
#            is_b_tagged = random.uniform(0,1) < eff
            jet.tags['eff'] = eff
            #jet.tags['b'] = is_b_tagged
