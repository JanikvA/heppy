from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *
import math

from ROOT import TFile

from heppy.utils.deltar import deltaR, deltaPhi

def dR_phitheta(p1,p2):
    dphi=deltaPhi(p1.phi(),p2.phi())
    dtheta=abs(p1.theta()-p2.theta())
    dR=math.sqrt(dphi**2+dtheta**2)
    return dR



class isoClass(object):
    def __init__(self, ptc, ptcColl, dR):
        self.ptc=ptc
        self.ptcColl=ptcColl

        self.isoe=0
        self.num=0
        self.ptcs=[]

        self.isosum_calcInternal(dR)


    def isosum_calcInternal(self, dR):
        for ptc in self.ptcColl:
            if dR_phitheta(self.ptc,ptc)<dR:
                self.isoe+=ptc.e()
                self.num+=1
                self.ptcs.append(ptc)


def isosum_calc(dR,p1,p2,ptcColl):
    isosum=0
    g1=isoClass(p1,ptcColl,dR)
    g2=isoClass(p2,ptcColl,dR)
    return g1.isoe/p1.e()+g2.isoe/p2.e()




class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName, 'tree.root']), 'recreate')
        self.tree = Tree( 'events', '')
        bookParticle(self.tree, 'higgs')
        bookParticle(self.tree, 'photon1')
        bookParticle(self.tree, 'photon2')

        var(self.tree, "isosum")
        var(self.tree, "deta")
        var(self.tree, "dHtheta")
        var(self.tree, "njet")
        var(self.tree, "zed_mass")
        var(self.tree, "isosum02")
       
    def process(self, event):
        self.tree.reset()
        photons = getattr(event, self.cfg_ana.selected_photons)
        higgs = getattr(event, self.cfg_ana.higgs)
        isosum = getattr(event, self.cfg_ana.isosum)
        deta = getattr(event, self.cfg_ana.deta)
        dHtheta = getattr(event, self.cfg_ana.dHtheta)
        zed_mass = getattr(event, self.cfg_ana.zed_mass)
        jets = getattr(event, self.cfg_ana.jets)

        fillParticle(self.tree, 'photon1', photons[0] )        
        fillParticle(self.tree, 'photon2', photons[1] )        
        fillParticle(self.tree, 'higgs', higgs )        

        fill(self.tree, "isosum", isosum)
        fill(self.tree, "deta", deta)
        fill(self.tree, "dHtheta", dHtheta)
        fill(self.tree, "njet", len(jets))
        fill(self.tree, "zed_mass", zed_mass)



        recoPtcs=getattr(event, self.cfg_ana.recoPtcs)
        fill(self.tree, "isosum02", isosum_calc(0.2,photons[0],photons[1],recoPtcs))


        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        

