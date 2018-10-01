from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.jet import Jet
from heppy.particles.jet import JetConstituents
from ROOT import TLorentzVector

import itertools

class JetCombinator(Analyzer):
    """
    combines jets
    """

    def merge_constituents(self, constituent_list):
        """
        returns the combination of the constituents lists
        @param constituent_list list of JetConstituent objects, e.g. [jet1.constituents, jet2.constituents]
        """
        ret = JetConstituents()
        for elem in constituent_list:
            for group in elem.values():
                for ptc in group:
                    ret.append(ptc)
        
        ret.sort()
        return ret

    def validateMomenta(self, jet, tolerance=.01):
        """
        Checks if the jetmomentum is the sum of the constituent momenta.
        """
        v = TLorentzVector(0, 0, 0, 0)
        for comp in jet.constituents.values():
            for ptc in comp:
                v += ptc.p4()

        ret = True

        if abs(jet.pt() - v.Pt())>tolerance:
            print 'pt unequal: ', jet.pt() - v.Pt()
            ret = False

        if abs(jet.theta() - v.Theta()) > tolerance:
            print 'theta unequal: ', jet.theta() - v.Theta()
            ret = False

        if abs(jet.eta() - v.Eta()) > tolerance:
            print 'eta unequal', jet.eta() - v.Eta()
            ret = False
            
        if abs(jet.phi() - v.Phi()) > tolerance:
            print 'phi unequal: ', jet.phi() - v.Phi()
            ret = False

        if abs(jet.m() - v.M()) > tolerance:
            print 'mass unequal: ', jet.m() - v.M()
            ret = False

        return ret
            
        

    def process(self, event):

        jets = getattr(event, self.cfg_ana.input_jets)

        setattr(event, self.cfg_ana.n_jets, len(jets))
        print jets
        print len(jets)

        for jet in jets:
            temp = self.validateMomenta(jet)
        return False
        if len(jets) < 4:
            return False

        
        while len(jets) > 4:

            pairs = [(a, b) for a, b in itertools.combinations(jets, 2)]
            pairs.sort(key = lambda x: (x[0].p4() + x[1].p4())*(x[0].p4() + x[1].p4()))

            for a, b in pairs:
                print (a.p4()+b.p4())*(a.p4()+b.p4())
            print '//////////////////'
            # combine jets
            jet_a, jet_b = pairs[0]
            print jet_a, jet_b
            newjet = Jet((jet_a.p4() + jet_b.p4()))
            newjet.constituents = self.merge_constituents([jet_a.constituents, jet_b.constituents])
            newjet.constituents.validate(newjet.e())
            self.validateMomenta(newjet)
            print newjet

            jets.remove(jet_a)
            jets.remove(jet_b)
            jets.append(newjet)
            jets.sort(key = lambda x: x.m())
            print(jets)
            
        print ';;;;;;;;;;;;;\n\n'
        assert(len(jets)==4)
	setattr(event, self.cfg_ana.output_jets, jets)
