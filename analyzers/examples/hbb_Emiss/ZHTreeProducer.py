from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.fcc_ee_higgs.analyzers.ntuple import *

from ROOT import TFile

class ZHTreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(ZHTreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        if hasattr(self.cfg_ana, 'recoil'):
            bookParticle(self.tree, 'recoil')
        if hasattr(self.cfg_ana, 'zeds'):  
            bookZed(self.tree, 'zed')
        self.taggers = ['b', 'bmatch', 'bfrac']
        for label in self.cfg_ana.jet_collections:  
            bookJet(self.tree, '{}_1'.format(label), self.taggers)
            bookJet(self.tree, '{}_2'.format(label), self.taggers)
        for label in self.cfg_ana.resonances:
            iso = False
            if 'zed' in label:
                iso = True
            bookResonanceWithLegs(self.tree, label, iso)
##        bookResonanceWithLegs(self.tree, 'genb1')
##        bookResonanceWithLegs(self.tree, 'genb2')
        for label in self.cfg_ana.misenergy:
            bookParticle(self.tree, label)
        var(self.tree, 'n_nu')
       
    def process(self, event):
        self.tree.reset()
        if hasattr(self.cfg_ana, 'recoil'):
            recoil = getattr(event, self.cfg_ana.recoil)    
            fillParticle(self.tree, 'recoil', recoil)
        if hasattr(self.cfg_ana, 'zeds'):  
            zeds = getattr(event, self.cfg_ana.zeds)
            if len(zeds)>0:
                zed = zeds[0]
                fillZed(self.tree, 'zed', zed)
        for label in self.cfg_ana.misenergy:        
            misenergy = getattr(event, label)
            fillParticle(self.tree, label, misenergy)      
        for label in self.cfg_ana.jet_collections:  
            jets = getattr(event, label)
            for ijet, jet in enumerate(jets):
                if ijet == 2:
                    break
                fillJet(self.tree, '{label}_{ijet}'.format(label=label, ijet=ijet+1),
                        jet, self.taggers)
        for label in self.cfg_ana.resonances:
            resonances = getattr(event, label)
            if len(resonances)>0:  
                resonance = resonances[0]
                iso = False
                if 'zed' in label:
                    iso = True                
                fillResonanceWithLegs(self.tree, label, resonance, iso)
        neutrinos = getattr(event, 'neutrinos', None)
        if neutrinos:
            fill(self.tree, 'n_nu', len(neutrinos))
##        for i, boson in enumerate(event.gen_bosons):
##            if i == 2:
##                break
##            fillResonanceWithLegs(self.tree, 'genb{i}'.format(i=i+1), boson)            
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        
