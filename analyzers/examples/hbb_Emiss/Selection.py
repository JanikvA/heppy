from heppy.framework.analyzer import Analyzer
from heppy.statistics.counter import Counter
import math
from ROOT import TLorentzVector,TVector3
from heppy.utils.deltar import * 

class Selection(Analyzer):

    def beginLoop(self, setup):
        super(Selection, self).beginLoop(setup)
        self.counters.addCounter('cut_flow') 
        self.counters['cut_flow'].register('All events')
        self.counters['cut_flow'].register('1 b jet')
        self.counters['cut_flow'].register('2 jets')
        self.counters['cut_flow'].register('2 b jets')
        self.counters['cut_flow'].register('mvis between 10 and 180')
        self.counters['cut_flow'].register('m_miss between 65 and 125')
        self.counters['cut_flow'].register('Trans momentum > 15 GeV')
        self.counters['cut_flow'].register('Long momentum < 50 GeV')
        self.counters['cut_flow'].register('Angle between jets > 100 degrees')
        self.counters['cut_flow'].register('cross > 10')
        self.counters['cut_flow'].register('Total # of events after cuts')

        
    def process(self, event):

	#survival variable is for an artififcal cut flow because the real selection is done in the ROOT macro
        survival='dead'
        self.counters['cut_flow'].inc('All events')
        
	det = getattr(event, self.cfg_ana.det)
        if det == 1:
            print 'no Solution for scaling factor!'
	    return False
    
        jets = getattr(event, self.cfg_ana.input_jets)
        if len(jets) == 2:
            self.counters['cut_flow'].inc('2 jets')
#bjets are actually all jets
	bjets = [jet for jet in jets]
        realbjets=[jet for jet in jets if jet.tags['bmatch']]#assuming 100% b-tag efficiency
        if len(realbjets) == 2:
            self.counters['cut_flow'].inc('2 b jets')
            survival = 'alive'
        elif len(realbjets) == 1:
            self.counters['cut_flow'].inc('1 b jet')

#emratio returns the energy ration (electromagnetic E/total E) of the jet in which it is the greatest 
        emratio=[]
        for i in range(2):
            emratio.append(bjets[i].constituents[22].e()/bjets[i].e())
        setattr(event, self.cfg_ana.emratio, max(emratio))

#Total visible mass######################################
	pvis=bjets[0].p4()+bjets[1].p4()
	mvis=pvis.M()
        setattr(event, self.cfg_ana.mvis, mvis)

        if mvis<10 or mvis>180:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('mvis between 10 and 180')




#missing mass############################################
        misenergy = getattr(event, self.cfg_ana.misenergy)
        if misenergy.m()>125 or misenergy.m()<65:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('m_miss between 65 and 125')


#transversal momentum###########################################
#cross check: succeeded
#        print 'compare ', bjets[0].pt(),' to ',math.sqrt(bjets[0].p3().Px()**2+bjets[0].p3().Py()**2)

        pTges=0
        lix=[]
        liy=[]
        for jet in bjets:
            lix.append(jet.p3().Px())
            liy.append(jet.p3().Py())
        xve=lix[0]+lix[1]
        yve=liy[0]+liy[1]
        pTges=math.sqrt(xve**2+yve**2)
        setattr(event, self.cfg_ana.pTges, pTges)
        if pTges<=15.:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('Trans momentum > 15 GeV')
#cross check: succeeded
#        pTtest=math.sqrt((bjets[0].p3().Px()+bjets[1].p3().Px())**2+(bjets[0].p3().Py()+bjets[1].p3().Py())**2)
#        print 'compare ',pTtest,' to ', pTges


#longitudinal moementum############################################
        pLges=0
        liz=[]
        for jet in bjets:
            liz.append(jet.p3().Pz())
        pLges=abs(liz[0]+liz[1])
        setattr(event, self.cfg_ana.pLges, abs(pLges))
        if abs(pLges)>=50.:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('Long momentum < 50 GeV')
#cross check: succeeded
#        pLtest=math.sqrt((bjets[0].p3().Pz()+bjets[1].p3().Pz())**2)
#        print 'compare ',pLtest,' to ',pLges

#alpha: angle between the 2 jets############################################
#       skalarp is the scalar product of bjet_1 and bjet_2; skalarpa(b) is the product of bjet_1(bjet_2)
#       with itself
        skalarp=bjets[1].p3().Px() *bjets[0].p3().Px() + bjets[0].p3().Py() * bjets[1].p3().Py() + bjets[0].p3().Pz() * bjets[1].p3().Pz() 
        skalarpa=bjets[0].p3().Px() *bjets[0].p3().Px() + bjets[0].p3().Py() * bjets[0].p3().Py() + bjets[0].p3().Pz() * bjets[0].p3().Pz()
        skalarpb=bjets[1].p3().Px() *bjets[1].p3().Px() + bjets[1].p3().Py() * bjets[1].p3().Py() + bjets[1].p3().Pz() * bjets[1].p3().Pz()

#        print bjets[0].scalarp(bjets[0])
        cosa=skalarp/(math.sqrt(skalarpa)*math.sqrt(skalarpb))
#          alpha is the angle between the two jets in degrees
	try:
            alpha=360*math.acos(cosa)/(2*math.pi)
	except ValueError:
#Very Rare...something like 1 of 100000 events in qqbar
#This ValueError is very weird and must come from some roudning problems in python. It happens very rarely. The particles are exactly back to back so cosa is -1 but the way cosa is calc it becomes just slightly smaller than -1 and math.acos(cosa) returns ValueError. Instead of returning False its prob better to set alpha to 180. But gonna check this in more detail
	    print "#################ValueError#################"
	    print "cosa= ",cosa  #this prints 1 or -1
	    print "skalarp= ",skalarp
	    print "skalarpa=",skalarpa
	    print "skalarpb=",skalarpb
	    return False
	setattr(event, self.cfg_ana.alpha, alpha)
        if alpha < 100:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('Angle between jets > 100 degrees')


#cross variable ################################################################
#       normal vector of the plane between the two vectors i.e. cross product
        normvec = TLorentzVector(0, 0, 0, 0)
        normvec.SetPx(bjets[0].p3().Py()*bjets[1].p3().Pz() - bjets[0].p3().Pz()*bjets[1].p3().Py())
        normvec.SetPy(bjets[0].p3().Pz()*bjets[1].p3().Px() - bjets[0].p3().Px()*bjets[1].p3().Pz())
        normvec.SetPz(bjets[0].p3().Px()*bjets[1].p3().Py() - bjets[0].p3().Py()*bjets[1].p3().Px())
       
        cross=abs(normvec.Pz()/(math.sqrt(skalarpa*skalarpb)))
        cross=math.asin(cross)*180./math.pi

        setattr(event, self.cfg_ana.cross, cross)

#cross check for cross variable (Patricks code): succeeded
#	p1=TVector3(bjets[0].p3().Px(),bjets[0].p3().Py(),bjets[0].p3().Pz())
#	p2=TVector3(bjets[1].p3().Px(),bjets[1].p3().Py(),bjets[1].p3().Pz())
#	cross2=p1.Unit().Cross(p2.Unit())
#	cross2=abs(cross2.Unit().z())
#	cross2=math.asin(cross2)*180./math.pi


#cross check: succeeded
#        print 'compare: ',bjets[0].norm(), 'to : ',math.sqrt(bjets[0].scalarp(bjets[0]))

# cross check: succeeded
#        print abs(normvec.Pz()),'-----',abs((bjets[0].cross(bjets[1])).Pz())
        
#       beta is the angle between the plane of the two jets and the beamaxis
    #ZeroDivisonError 
        if math.sqrt(normvec.Px()**2+normvec.Py()**2+normvec.Pz()**2)==0:
	    print "##########normvec has norm of 0!!!#########"
	    #A very rare case...about 1 in 1000000 qqbar events
	    #reason is the angle between the 2 jets is 0
	    print "Px= ",normvec.Px()
	    print "Py= ",normvec.Py()
	    print "Pz= ",normvec.Pz()
	    print "jet energies= ",bjets[0].e(),"_,",bjets[1].e()
	    print "angle betwee nthe jets= ",alpha #this returns 0
	    return False
	cosb=normvec.Pz()/(math.sqrt(normvec.Px()**2+normvec.Py()**2+normvec.Pz()**2))
	beta=360*math.acos(cosb)/(2*math.pi)
        beta1=180-beta

#cross check Colins acoplanarity code: succeeded
#	j1=bjets[0].p3()
#	j2=bjets[1].p3()
#	axis=TVector3(0,0,1)
#	normal = j1.Cross(j2).Unit()
#	angle=normal.Angle(axis)-math.pi/2.
#	print angle,angle*180./math.pi,90-min(beta,beta1),cross2 

# cross check: succeeded
#        sintest=abs(normvec.Pz())/(math.sqrt(normvec.Px()**2+normvec.Py()**2+normvec.Pz()**2))
#        betatest=360*math.asin(sintest)/(2*math.pi)
#        print 'compare ',betatest, ' to ',90-min(beta,beta1)
                
        setattr(event, self.cfg_ana.beta, 90-min(beta,beta1))
        if cross < 10:
            survival = 'dead'
        elif survival == 'alive':
            self.counters['cut_flow'].inc('cross > 10')

        if survival == 'alive':
            self.counters['cut_flow'].inc('Total # of events after cuts')
        setattr(event, self.cfg_ana.cutlife, survival)


#cross check:succeeded
#        ptcs = getattr(event, self.cfg_ana.particles)
#        pvis = TLorentzVector(0,0,0,0)
#        for ptc in ptcs:
#            pvis+=ptc.p4()
#        print pvis.M()
#        print mvis

#Total number of charged tracks
        nchargedtracks=bjets[0].constituents[211].num()+bjets[1].constituents[211].num()
        setattr(event, self.cfg_ana.ctracks, nchargedtracks)

