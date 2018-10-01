from heppy.framework.analyzer import Analyzer
import copy
import math
from heppy.statistics.counter import Counter
from heppy.particles.tlv.particle import Particle as Recoil
from ROOT import TLorentzVector
import random

class Bjetscaling(Analyzer):
    '''Use the initial p4 to constrain the energy of the 4 jets,                                     
    in ee -> 4 jet final states.                                                                     
                                                                                                     
    from heppy.analyzers.examples.zh_had.JetEnergyComputer import JetEnergyComputer                  
    compute_jet_energy = cfg.Analyzer(                                                               
      JetEnergyComputer,                                                                             
      output_jets='rescaled_jets',                                                                   
      input_jets='jets',                                                                             
      sqrts=Collider.SQRTS                                                                           
    )                                                                                                
                                                                                                     
    * output_jets: output jets with a rescaled energy.                                               
    note that only the jet p4 is copied when creating a rescaled jet                                 
                                                                                                     
    * input_jets: collection of jets to be rescaled                                                  
                                                                                                     
    * sqrts: center-of-mass energy of the collision                                                  
                                                                                                     
    '''

    
    def process(self, event):
        #sqrts = self.cfg_ana.sqrts
	#sqrts=240.
	sqrts = random.gauss(240.,240.*0.0012)
	#sqrts = random.gauss(240.,10.)
        jets = getattr(event, self.cfg_ana.input_jets)
        misenergy = getattr(event, self.cfg_ana.misenergy)
#        solving the equation
        
        vis_p4 = TLorentzVector(0, 0, 0, 0)
        for jet in jets:
            vis_p4+=jet.p4()
        vis = Recoil(0,0,vis_p4,1)
#         m=m_Z constrain
        a = vis.e()*sqrts/(vis.m()**2)
        b = a**2 - (sqrts**2 - 91.**2)/(vis.m()**2)



#      sf stands for scaling factor

        if b<0:
            sf = 1
            setattr(event, self.cfg_ana.det, 1)
        else :
#sf2 corresponds to the solution where the missing energy is negative therefore sf is the scaling factor that makes sense from a physics pov.
            sf = a - math.sqrt(b)
	    sf2=a+math.sqrt(b)
            setattr(event, self.cfg_ana.det, 2)
           
     
######test
	#visscaled1=TLorentzVector(0,0,0,0)
	#visscaled2=TLorentzVector(0,0,0,0)
	#for jet in jets:
	#    visscaled1+=jet.p4()*sf
	#    visscaled2+=jet.p4()*sf2
	#cms=TLorentzVector(0,0,0,240)
	#v1=cms-visscaled1
	#v2=cms-visscaled2
	#print v1.E(),v2.E()
        
        setattr(event, self.cfg_ana.scalingfac, sf)
	
        setattr(event, self.cfg_ana.scalingfac2, sf2)
        

	scale_factors = [sf]*2
        output = []
        for jet, factor in zip(jets, scale_factors):
            # the jets should not be deepcopied                                                      
            # as they are heavy objects containing                                                   
            # in particular a list of consistuent particles                                          
            scaled_jet = copy.copy(jet)
            scaled_jet._tlv = copy.deepcopy(jet._tlv)
            scaled_jet._tlv *= factor
            output.append(scaled_jet)
        
        setattr(event, self.cfg_ana.output_jets, output)

