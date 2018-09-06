from heppy.framework.analyzer import Analyzer
from heppy.statistics.counter import Counter

from heppy.particles.tlv.resonance import Resonance2 as Resonance
from ROOT import TLorentzVector
import itertools
import math 

class Selection(Analyzer):

    def beginLoop(self, setup):
        super(Selection, self).beginLoop(setup)
        self.counters.addCounter('cut_flow') 
        self.counters['cut_flow'].register('All events')
        self.counters['cut_flow'].register('>=2 good photons')
    
    def process(self, event):
        self.counters['cut_flow'].inc('All events')

        ptcs = getattr(event, self.cfg_ana.reco_ptc)        

        # Selecting all "good" photons
        gammas = [g for g in ptcs if (abs(g.pdgid())==22 and g.e()>40. and g.eta()<2.5)]
        if len(gammas)<2:
            return False
        self.counters['cut_flow'].inc('>=2 good photons')

        # Selecting the 2 photons making up the higgs candidate
        if len(gammas)==2:
            higgs_cand=Resonance(gammas[0],gammas[1],25)
        else:
            higgses = []
            initial_tlv = TLorentzVector(0,0,0,240.)
            for leg1, leg2 in itertools.combinations(gammas,2):
                higgses.append( Resonance(leg1, leg2, 25) )
            higgses.sort(key=lambda x: abs((initial_tlv-x._tlv).M()-91.2))
            higgs_cand = higgses[0]
        h_gammas=[higgs_cand.leg1(),higgs_cand.leg2()]

        # Photon isolationsum
        iso_sum = 0
        for g in h_gammas:
            iso_sum += g.iso.sume/g.e() 

        # Pseudo rapidity gap of photons
        deta = abs(h_gammas[0].eta()-h_gammas[1].eta())

        # Angle between beampipe and higgs
        dtheta = 90.-higgs_cand.theta()*360./(2*math.pi)

        setattr(event, "selected_photons", h_gammas)
        setattr(event, "higgs", higgs_cand)
        setattr(event, "isosum", iso_sum)
        setattr(event, "deta", deta)
        setattr(event, "dHtheta", dtheta)