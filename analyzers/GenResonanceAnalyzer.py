from heppy.framework.analyzer import Analyzer
from heppy.particles.tlv.resonance import Resonance2
from heppy.particles.genbrowser import GenBrowser

import pprint

class GenResonanceAnalyzer(Analyzer):

    def process(self, event):
        
        bosons = [ptc for ptc in event.gen_particles
                  if abs(ptc.pdgid()) in self.cfg_ana.pdgids
                  and ptc.status() in self.cfg_ana.statuses]
        if not hasattr(event, 'genbrowser'):
            event.genbrowser = GenBrowser(event.gen_particles,
                                          event.gen_vertices)
        output = []
        for boson in bosons:
            daughters = event.genbrowser.decay_daughters(boson)
            assert(len(daughters) == 2)
            if hasattr(self.cfg_ana, 'decay_pdgids') and \
               not ( abs(daughters[0].pdgid()) in self.cfg_ana.decay_pdgids and \
                     abs(daughters[1].pdgid()) in self.cfg_ana.decay_pdgids ):
                continue
            d0, d1 = daughters[0], daughters[1]
            # putting particle before anti particle
            if d1.pdgid() > d0.pdgid():
                d0, d1 = d1, d0
            # but if the 1st particle is neutral, put it at the end (W->lnu)
            if d0.q() == 0:
                d0, d1 = d1, d0
            resonance = Resonance2(d0, d1, 
                                   boson.pdgid(), boson.status())
            output.append(resonance)
        output.sort(key=lambda x: x.pdgid())
        idstring = '_'.join(map(str, self.cfg_ana.pdgids))
        output_name = '_'.join(['gen_bosons', idstring])  # e.g. gen_bosons_23_25 
        if hasattr(self.cfg_ana, 'output'):
            output_name = self.cfg_ana.output
        setattr(event, output_name, output)
        if self.verbose:
            print self
            if not len(output):
                print 'no boson found'
            else:
                for gb in output:
                    print gb
                    pprint.pprint(gb.legs)
            print
