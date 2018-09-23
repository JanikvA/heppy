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

#def isosum_calc(dR, p1, p2 ,ptcCollection, debug=False):
#    iso1=0
#    iso2=0
#    num1=0
#    num2=0
#    pass1=[]
#    for ptc in ptcCollection:
#        if ptc is p1: print "HOW"
#        if ptc is p2: print "HOW"
#        if deltaR(p1.eta(),p1.phi(),ptc.eta(),ptc.eta())<dR:
#            iso1+=ptc.e()
#            num1+=1
#        if deltaR(p2.eta(),p2.phi(),ptc.eta(),ptc.eta())<dR:
#            print deltaR(p2.eta(),p2.phi(),ptc.eta(),ptc.eta())
#            iso2+=ptc.e()
#            num2+=1
#            pass1.append(ptc)
#    isosum=iso1/p1.e() + iso2/p2.e()
#    if debug:
#        print num1,num2
#        print iso1,iso2
#        return pass1
#    return isosum
#
#def isosum_calc2(dR, p1, p2 ,ptcCollection):
#    iso1=0
#    iso2=0
#    for ptc in ptcCollection:
#        if ptc is p1: print "HOW"
#        if ptc is p2: print "HOW"
#        if dR_phitheta(p1,ptc)<dR:
#            iso1+=ptc.e()
#        if dR_phitheta(p2,ptc)<dR:
#            iso2+=ptc.e()
#    isosum=iso1/p1.e() + iso2/p2.e()
#    return isosum




class isoClass(object):
    def __init__(self, ptc, ptcColl, dR):
        self.ptc=ptc
        self.ptcColl=ptcColl

        self.isoe=0
        self.num=0
        self.ptcs=[]

        self.isosum_calc2(dR)

#    def isosum_calc(self, dR):
#        for ptc in self.ptcColl:
#            #print deltaR(self.ptc.eta(),self.ptc.phi(),ptc.eta(),ptc.eta())
#            if deltaR(self.ptc.eta(),self.ptc.phi(),ptc.eta(),ptc.eta())<dR:
#                self.isoe+=ptc.e()
#                self.num+=1
#                self.ptcs.append(ptc)

    def isosum_calc2(self, dR):
        for ptc in self.ptcColl:
            #print dR_phitheta(self.ptc,ptc)
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
        bookParticle(self.tree, 'missing_energy')

        var(self.tree, "isosum")
        var(self.tree, "deta")
        var(self.tree, "dHtheta")
        var(self.tree, "njet")
        var(self.tree, "zed_mass")
        
        var(self.tree, "jj_mass")
        var(self.tree, "jj_phi")
        var(self.tree, "jj_theta")
        var(self.tree, "jj_dphi")
        var(self.tree, "jj_dtheta")
        var(self.tree, "jj_dR")
        var(self.tree, "m_vis")
        var(self.tree, "isosum01")
        var(self.tree, "isosum02")
        var(self.tree, "isosum03")
        var(self.tree, "isosum04")
        var(self.tree, "isosum05")
        var(self.tree, "isosum06")
        var(self.tree, "isosum08")
        var(self.tree, "isosum10")
        var(self.tree, "isosum15")
        var(self.tree, "isosum20")
       
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


        if len(jets)>1:
            jj=(jets[0]._tlv+jets[1]._tlv)
            fill(self.tree, "jj_mass", jj.M())
            fill(self.tree, "jj_phi", jj.Phi())
            fill(self.tree, "jj_theta", jj.Theta())
            fill(self.tree, "jj_dphi", deltaPhi(jets[0].phi(),jets[1].phi()))
            fill(self.tree, "jj_dtheta", abs(jets[0].eta()-jets[1].eta()))
            fill(self.tree, "jj_dR", deltaR(jets[0].theta(),jets[0].phi(),jets[1].theta(),jets[1].phi()))
            fill(self.tree, "m_vis", (jj+higgs._tlv).M())
        else:
            fill(self.tree, "jj_mass", -99)
            fill(self.tree, "jj_phi", -99)
            fill(self.tree, "jj_theta", -99)
            fill(self.tree, "jj_dphi", -99)
            fill(self.tree, "jj_dtheta", -99)
            fill(self.tree, "jj_dR", -99)
            fill(self.tree, "m_vis", -99)

        # own isosum calculation
        recoPtcs=getattr(event, self.cfg_ana.recoPtcs)


        # This shows that Colins code is not adapting correctly to lepton collider. Isolation is still calculated with eta,phi and not theta,phi
        #print "##########"
        #g2=isoClass(photons[1],recoPtcs, 0.4)
        #if g2.isoe!=photons[1].iso.sume:
        #    for ptc in g2.ptcs:
        #        print "ptc: ",ptc.pdgid()
        #        if ptc in photons[1].iso.particles:
        #            continue                    
        #        print deltaR(ptc,photons[1])
        #        print deltaR(photons[1],ptc)
        #        print dR_phitheta(photons[1],ptc)
        #        print deltaR(photons[1].eta(),photons[1].phi(),ptc.eta(),ptc.phi())
        #        print deltaR(photons[1].theta(),photons[1].phi(),ptc.theta(),ptc.phi())
        #print "##########"

        fill(self.tree, "isosum01", isosum_calc(0.1,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum02", isosum_calc(0.2,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum03", isosum_calc(0.3,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum04", isosum_calc(0.4,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum05", isosum_calc(0.5,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum06", isosum_calc(0.6,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum08", isosum_calc(0.8,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum10", isosum_calc(1.0,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum15", isosum_calc(1.5,photons[0],photons[1],recoPtcs))
        fill(self.tree, "isosum20", isosum_calc(2.0,photons[0],photons[1],recoPtcs))


        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        

