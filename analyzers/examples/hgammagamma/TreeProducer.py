from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *

from ROOT import TFile

class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName, 'tree.root']), 'recreate')
        self.tree = Tree( 'events', '')
        bookParticle(self.tree, 'higgs')
        bookParticle(self.tree, 'photon1')
        bookParticle(self.tree, 'photon2')
        bookParticle(self.tree, 'missing_energy')

        var(self.tree, "isosum")
        var(self.tree, "deta")
        var(self.tree, "dHtheta")
        var(self.tree, "njet")
        var(self.tree, "zed_mass")
        
       
    def process(self, event):
        self.tree.reset()
        photons = getattr(event, self.cfg_ana.selected_photons)
        higgs = getattr(event, self.cfg_ana.higgs)
        isosum = getattr(event, self.cfg_ana.isosum)
        deta = getattr(event, self.cfg_ana.deta)
        dHtheta = getattr(event, self.cfg_ana.dHtheta)
        zed_mass = getattr(event, self.cfg_ana.zed_mass)
        missing_energy = getattr(event, self.cfg_ana.missing_energy)
        jets = getattr(event, self.cfg_ana.jets)

        fillParticle(self.tree, 'photon1', photons[0] )        
        fillParticle(self.tree, 'photon2', photons[1] )        
        fillParticle(self.tree, 'higgs', higgs )        
        fillParticle(self.tree, 'missing_energy', missing_energy )        

        fill(self.tree, "isosum", isosum)
        fill(self.tree, "deta", deta)
        fill(self.tree, "dHtheta", dHtheta)
        fill(self.tree, "njet", len(jets))
        fill(self.tree, "zed_mass", zed_mass)

        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        

