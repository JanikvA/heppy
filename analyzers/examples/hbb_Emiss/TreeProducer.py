from heppy.framework.analyzer import Analyzer
from heppy.statistics.tree import Tree
from heppy.analyzers.ntuple import *
import math

from ROOT import TFile

class TreeProducer(Analyzer):

    def beginLoop(self, setup):
        super(TreeProducer, self).beginLoop(setup)
        self.rootfile = TFile('/'.join([self.dirName,
                                        'tree.root']),
                              'recreate')
        self.tree = Tree( 'events', '')
        self.taggers = ['b','bmatch','bfrac','eff','btag','ctag','udsgtag','b_pvprob']
        bookJet(self.tree, 'jet1', self.taggers)
        bookJet(self.tree, 'jet2', self.taggers)
        bookJet(self.tree, 'scaledjet1', self.taggers)
        bookJet(self.tree, 'scaledjet2', self.taggers)
#        bookJet(self.tree, 'jet3', self.taggers)
#        bookJet(self.tree, 'jet4', self.taggers)
        bookJet(self.tree, 'genjet1', self.taggers)
        bookJet(self.tree, 'genjet2', self.taggers)
#        bookJet(self.tree, 'genjet3', self.taggers)
#        bookJet(self.tree, 'genjet4', self.taggers)
        bookParticle(self.tree, 'genmisenergy')
        bookParticle(self.tree, 'misenergy')
        bookParticle(self.tree, 'higgs')
        bookParticle(self.tree, 'higgsnosf')
        bookParticle(self.tree, 'zed')
      
        bookParticle(self.tree, 'zed_parton1')
        bookParticle(self.tree, 'zed_parton2')
        bookParticle(self.tree, 'higgs_parton1')
        bookParticle(self.tree, 'higgs_parton2')

        var(self.tree, 'jet1res')
        var(self.tree, 'jet2res')
        var(self.tree, 'absjet1res')
        var(self.tree, 'absjet2res')
        var(self.tree, 'cross')
        var(self.tree, 'ctracks')
        var(self.tree, 'mvis')
        var(self.tree, 'genmvis')
        var(self.tree, 'emratio')
#        var(self.tree, 'quarkdR')
#        var(self.tree, 'jetdR')
        var(self.tree, 'alpha')
        var(self.tree, 'beta')
        var(self.tree, 'pLges')
        var(self.tree, 'pTges')
        var(self.tree, 'scaling_fac')
        var(self.tree, 'scaling_fac2')
        var(self.tree, 'n_jets') 
        var(self.tree, 'n_genjets') 
	var(self.tree, 'bquarks')       
	var(self.tree, 'n_genptc_23')

#        var(self.tree, 'n10') 
#        var(self.tree, 'n15') 
#        var(self.tree, 'n25') 
#	var(self.tree, 'n35')       

    def process(self, event):
        self.tree.reset()
#        n10=getattr(event, self.cfg_ana.num10)
#        n15=getattr(event, self.cfg_ana.num15)
#        n25=getattr(event, self.cfg_ana.num25)
#        n35=getattr(event, self.cfg_ana.num35)
#        fill(self.tree, 'n10', n10)
#        fill(self.tree, 'n15', n15)
#        fill(self.tree, 'n25', n25)
#        fill(self.tree, 'n35', n35)
        gen_particles=getattr(event, self.cfg_ana.gen_particles)
        ptc23=[]
	totbquarks=0
	for ptc in gen_particles:
	    if ptc.status()==23 and abs(ptc.pdgid())==5:
	        totbquarks+=1
        for ptc in gen_particles:
            if ptc.status()==23:
                ptc23.append(ptc)
	fill(self.tree, 'bquarks',totbquarks)
	fill(self.tree, 'n_genptc_23',len(ptc23))
        cross=getattr(event, self.cfg_ana.cross)
        fill(self.tree, 'cross', cross)
        ctracks=getattr(event, self.cfg_ana.ctracks)
        fill(self.tree, 'ctracks', ctracks)
        mvis=getattr(event, self.cfg_ana.mvis)
        fill(self.tree, 'mvis', mvis)
        scalingfac = getattr(event, self.cfg_ana.scalingfac)
        fill(self.tree, 'scaling_fac', scalingfac)
        scalingfac2 = getattr(event, self.cfg_ana.scalingfac2)
        fill(self.tree, 'scaling_fac2', scalingfac2)
        emratio = getattr(event, self.cfg_ana.emratio)
        fill(self.tree, 'emratio', emratio)
        alpha = getattr(event, self.cfg_ana.alpha)
        fill(self.tree, 'alpha', alpha)
#        quarkdr = getattr(event, self.cfg_ana.drquark)
#        fill(self.tree, 'quarkdR', quarkdr)
#        jetdr = getattr(event, self.cfg_ana.drjet)
#        fill(self.tree, 'jetdR', jetdr)
        beta = getattr(event, self.cfg_ana.beta)
        fill(self.tree, 'beta', beta)
        pLges = getattr(event, self.cfg_ana.pLges)
        fill(self.tree, 'pLges', pLges)
        pTges = getattr(event, self.cfg_ana.pTges)
        fill(self.tree, 'pTges', pTges)

        misenergy = getattr(event, self.cfg_ana.misenergy)
        fillParticle(self.tree, 'misenergy', misenergy )        
#        genmisenergy = getattr(event, self.cfg_ana.genmisenergy)
#        fillParticle(self.tree, 'genmisenergy', genmisenergy )

        jets = getattr(event, self.cfg_ana.jets)

        for ijet, jet in enumerate(jets):
            if ijet==2:
                break
            fillJet(self.tree, 'jet{ijet}'.format(ijet=ijet+1),
                    jet, self.taggers)

        scaledjets = getattr(event, self.cfg_ana.scaledjets)
        for ijet, scaledjet in enumerate(scaledjets):
            if ijet==2:
                break
            fillJet(self.tree, 'scaledjet{ijet}'.format(ijet=ijet+1),
                    scaledjet, self.taggers)

        genjets = getattr(event, self.cfg_ana.genjets)
        for ijet, genjet in enumerate(genjets):
            if ijet==2:
                break
            fillJet(self.tree, 'genjet{ijet}'.format(ijet=ijet+1),
                    genjet, self.taggers)

	genpvis=genjets[0].p4()+genjets[1].p4()
	genmvis=genpvis.M()
        fill(self.tree, 'genmvis', genmvis)


 
        higgs = getattr(event, self.cfg_ana.higgs)
        if higgs:
            fillParticle(self.tree, 'higgs', higgs)

#        higgsnosf=getattr(event, self.cfg_ana.higgsnosf)
#        if higgsnosf:
#            fillParticle(self.tree, 'higgsnosf', higgsnosf)

#        zed = getattr(event, self.cfg_ana.zed)
#        if zed:
#            fillParticle(self.tree, 'zed', zed)

#        if len(event.partons_from_Z)==2:
#            fillParticle(self.tree, 'zed_parton1', event.partons_from_Z[0])
#            fillParticle(self.tree, 'zed_parton2', event.partons_from_Z[1])

#        if len(event.partons_from_H)==2:
#            fillParticle(self.tree, 'higgs_parton1', event.partons_from_H[0])
#            fillParticle(self.tree, 'higgs_parton2', event.partons_from_H[1])



#        if (jets[0].match and jets[1].match) is not None:
#            jet1res=(jets[0].e()-jets[0].match.e())/(jets[0].match.e())
#            jet2res=(jets[1].e()-jets[1].match.e())/(jets[1].match.e())
#        else:
#            jet1res=-50
#            jet2res=-50
        
#        fill(self.tree, 'jet1res', jet1res)
#        fill(self.tree, 'jet2res', jet2res)
#        fill(self.tree, 'absjet1res', abs(jet1res))
#        fill(self.tree, 'absjet2res', abs(jet2res))

        fill( self.tree, 'n_jets', len(jets) )
        fill( self.tree, 'n_genjets', len(genjets) )
        
        self.tree.tree.Fill()
        
    def write(self, setup):
        self.rootfile.Write()
        self.rootfile.Close()
        

