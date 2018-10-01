from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from fcc_ee_higgs.analyzers.ntuple import *

from ROOT import TFile
import math
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




def mkl(label, i=None):
    if i is None:
        return 'n_{}'.format(label)
    else:
        return '{}_{}'.format(label, i)
    
    
class TreeProducer(Analyzer):

    def _book(self, book_fun, cfg, *args, **kwargs):
        for label, n in cfg:
            var(self.tree, mkl(label))            
            for i in range(n):
                book_fun(self.tree, mkl(label, i), *args, **kwargs)    

    def _fill(self, fill_fun, cfg, event, *args, **kwargs):
        for label, n in cfg:
            ptcs = getattr(event, label)
            if not hasattr(ptcs, '__len__'):
                ptcs = [ptcs]
            fill(self.tree, mkl(label), len(ptcs))                
            for i, ptc in enumerate(ptcs):
                if i == n:
                    break
                fill_fun(self.tree, mkl(label, i), ptc, *args, **kwargs)
  

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        
        self._book(bookParticle, self.cfg_ana.particles)
        self.taggers = ['b', 'bmatch', 'bfrac']   
        self._book(bookJet, self.cfg_ana.jets, self.taggers)
        self.iso = False
        self._book(bookResonanceWithLegs, self.cfg_ana.resonances, self.iso)
        self._book(bookIsoParticle, self.cfg_ana.iso_particles)

        bookParticle(self.tree, 'higgs')

        var(self.tree, "isosum")
        var(self.tree, "deta")
        var(self.tree, "dHtheta")
        var(self.tree, "njet")
        var(self.tree, "zed_mass")
        var(self.tree, "isosum02")
                
       
    def process(self, event):
        self.tree.reset()

        self._fill(fillParticle, self.cfg_ana.particles, event)
        self._fill(fillJet, self.cfg_ana.jets, event, self.taggers)
        self._fill(fillResonanceWithLegs, self.cfg_ana.resonances, event,
                   self.iso)
        self._fill(fillIsoParticle, self.cfg_ana.iso_particles, event)
        
        higgs = getattr(event, self.cfg_ana.higgs)
        photons = getattr(event, self.cfg_ana.selected_photons)
        isosum = getattr(event, self.cfg_ana.isosum)
        deta = getattr(event, self.cfg_ana.deta)
        dHtheta = getattr(event, self.cfg_ana.dHtheta)
        zed_mass = getattr(event, self.cfg_ana.zed_mass)
        jets1 = getattr(event, self.cfg_ana.jets1)

        fillParticle(self.tree, 'higgs', higgs )

        fill(self.tree, "isosum", isosum)
        fill(self.tree, "deta", deta)
        fill(self.tree, "dHtheta", dHtheta)
        fill(self.tree, "njet", len(jets1))
        fill(self.tree, "zed_mass", zed_mass)
        recoPtcs=getattr(event, self.cfg_ana.recoPtcs)
        fill(self.tree, "isosum02", isosum_calc(0.2,photons[0],photons[1],recoPtcs))

        self.tree.tree.Fill()

    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
