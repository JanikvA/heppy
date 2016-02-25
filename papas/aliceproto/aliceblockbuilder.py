import itertools

from DAG import Node, BreadthFirstSearchIterative,DAGFloodfill
from heppy.papas.aliceproto.Identifier import Identifier

  
class PFBlock(object):
    ''' A Particle Flow Block stores a set of node ids that are connected to each other
     together with the edge data (distances) for each possible edge combination
     '''
 
    def __init__(self, elements,alledges):
        
        self.uniqueid=Identifier.makeID(self,Identifier.PFOBJECTTYPE.BLOCK) 
        self.element_unique_ids = sorted(elements, key=lambda x: Identifier.type_short_code(x) + str(x))
        self.size = len(elements)
        
        #extract the relevant parts of the edges and store this within the block
        self.edges = dict()       
        for id1, id2 in itertools.combinations(self.element_unique_ids,2):
            key=Edge.make_key(id1,id2)
            self.edges[key] =alledges[key]
        print("finished block")    
        
    
   
   
    def count_ecal(self):
        ''' Counts how many ecal cluster ids are in the block '''
        count=0
        for elem in self.element_unique_ids:
            count+=Identifier.is_ecal(elem)
        return count
    
    def count_tracks(self):
        ''' Counts how many track ids are in the block '''
        count=0
        for elem in self.element_unique_ids:
            count+=Identifier.is_track(elem)
        return count    
        
    def count_hcal(self):
        ''' Counts how many hcal cluster  ids are in the block '''
        count=0
        for elem in self.element_unique_ids:
            count+=Identifier.is_hcal(elem)
        return count  
    
    def edge_matrix_string(self) :
        #produces the lower part of the matrix of distances between elements
        #and at the same time construct a string of the corresponding edges
        #with additional edge details
        #elements are ordered as ECAL(E), HCAL(H), Track(T) and by edgekey
        
        # make the header line for the matrix       
        count=0
        matrixstr="      Edge Distance Matrix:\n           "
        for e1 in sorted(self.element_unique_ids) :
            elemstr=Identifier.type_short_code(e1) +str(count)
            matrixstr +=  "{:>9}".format(elemstr)
            count += 1
        matrixstr +=  "\n"
        
        #for each element find distances to all other items that are in the lower part of the matrix
        #at the same time collect up the corresponding edge details
        edgedetails="      Edge details: {\n"        
        countrow=0
        for e1 in sorted(self.element_unique_ids) : # this will be the rows
            countcol=0
            rowstr=""
            #make short name for the row element eg E3, H5 etc
            rowname=Identifier.type_short_code(e1) +str(countrow)
            for e2 in sorted(self.element_unique_ids) :  # these will be the columns
                #make short name for the col element eg E3, H5                
                colname=Identifier.type_short_code(e1) +str(countcol) 
                countcol += 1
                if (e1==e2) :
                    rowstr+="       . "
                    break
                edge=self.edges[Edge.make_key(e1,e2)]
                rowstr   += "{:8.4f}".format(edge.distance) + " "
                edgedetails += "      " + rowname + colname + edge.__str__() + "\n"
            matrixstr += "{:>11}".format(rowname) + rowstr + "\n"
            countrow += 1        
    
        return matrixstr  + edgedetails +"      }\n"
    
    def __str__(self):
        descrip = str('\n      ecals={count_ecal} hcals={count_hcal} tracks={count_tracks}'.format(
            count_ecal=self.count_ecal(),
            count_hcal=self.count_hcal(),
            count_tracks=self.count_tracks() )
        ) 
                
        descrip += "\n" + self.edge_matrix_string()     
        return descrip
    
    def __repr__(self):
            return self.__str__()    

'''
COLIN: how to represent a block? 

block : block id 

elements: 
  T1: track1 printout 
  E1: ecal1 printout 
  ..

links: 
       T1    E1 
  T1   x     dist
  E2         x
  ..

'''

    
      
class Edge(object): #edge information 
    # end nodes, distance and whether they are linked
    ruler = None
    
    def __init__(self, id1, id2,  link_type, is_linked, distance, descrip =""): 
        ''' The edge knows the ids of its ends, the distance between the two ends and whether or not they are linked '''
        self.id1=id1
        self.id2=id2
        self.distance=distance
        self.link_type=link_type
        self.linked= is_linked
        self.key=Edge.make_key(id1,id2) 
        self.descrip=descrip
    
    def short_link_type(self) :
        ''' for example  
            ee for ecal to ecal
            ht for hcal to track
        '''
        return self.link_type[0][0] + self.link_type[1][0]
        
  
    def __str__(self):
        descrip =str(self.link_type) + "=" + str(self.distance)+  " ("+ str( self.linked) + " ) :" + self.descrip
        return descrip
    
    def __repr__(self):
        return self.__str__()      
    

    @staticmethod    
    def make_key(id1,id2):
        return hash(tuple(sorted([id1,id2])))

        
class BlockBuilder(object):
    '''What is the purpose of the class? 
    describe interface, and in particular what are the 
    important attributes that the user can find in this class
    give a usage example.

    builder = BlockBuilder(tracks, ecal, hcal)
    tell how to use the blocks (code fragment)

    review all methods : pythonic name e.g. make_history_node 
    think about what has to be private or exposed to the user
    same for attributes
    '''
    def __init__(self, tracks, ecal, hcal, histNodes=None, ruler=None):
        '''describe what the method is doing.. here ok because constructor
        describe what is expected for parameters, e.g. dictionary for tracks, ecal
        hcal.
        say also what method is returning.

        tracks is a dictionary : {id1:track1, id2:track2, ...}
        '''

        self.ruler=ruler
        self.tracks=tracks
        self.ecal=ecal
        self.hcal=hcal

        # if the user does not specify an existing history tree,
        # start the tree with the identifiers of the provided tracks,
        # ecal and hcal clusters
        self.historyNodes = histNodes
        if self.historyNodes is None:
            self.historyNodes = dict(
                self._make_dict(tracks).items() + 
                self._make_dict(ecal).items() +
                self._make_dict(hcal).items() )

        # build the block nodes (separate graph which will use distances between items)
        self.nodes = dict(
             self._make_dict(tracks).items() + 
             self._make_dict(ecal).items() +
             self._make_dict(hcal).items() )
        
        # compute link properties between each pair of nodes
        self.edges = dict()
        
        for e1, e2 in itertools.combinations({'a','b','c','d','e'},2) :
                    print e1,e2         

        for e1, e2 in itertools.combinations(self.nodes,2) :
            self.add_edge(e1,e2)        

        # build blocks
        self.blocks=dict()
        self.make_blocks()

        


        
    def _make_dict(self, elems):  # this method is made private by the start _
        '''for a list of identifiers, return a dictionary
        {identifier: Node(identifier)}
        '''
        return dict( (idt, Node(idt)) for idt in elems )
    
   
    
    def add_edge(self,id1,id2) :
        obj1=self.get_object(id1)
        obj2=self.get_object(id2)
        link_type, is_linked, distance = self.ruler(obj1,obj2)
        edge_descrip = obj1.__str__() + " to " + obj2.__str__()
        
        edge=Edge(id1,id2, link_type,is_linked, distance,edge_descrip) #this is a bit clunky and can likely be improved
        self.edges[edge.key] = edge
        if  edge.linked: #this is actually an undirected link - will work fine for undirected searches 
            self.nodes[id1].add_child(self.nodes[id2])


    
        
    def make_blocks (self) :
        
        for b in DAGFloodfill(self.nodes).blocks :
            recHistoryUIDs= [] 
            #NB the nodes that are found by FloodFill are the edgeNodes
            # we acually want the blocks to contain the History nodes (the ones with matching uniqueid)
            #So, find the corresponding history nodes
            for e in b :
                recHistoryUIDs.append(e.getValue())         

            #now we can make the block
            block=PFBlock(recHistoryUIDs,  self.edges) #pass the edgedata and extract the needed edge links for this block          
            
            #put the block in the dict of blocks            
            self.blocks[block.uniqueid] =  block        
            
            #Link the block into the historyNodes
            self.set_block_links(block)
                     
    
    def get_object(self, e1) :
        type= Identifier.gettype(e1)
        if type==Identifier.PFOBJECTTYPE.TRACK :
            return self.tracks[e1]       
        elif type==Identifier.PFOBJECTTYPE.ECALCLUSTER :
            return self.ecal[e1] 
        elif type==Identifier.PFOBJECTTYPE.HCALCLUSTER :
            return self.hcal[e1]            
        else :
            assert(False)    
    
    def set_block_links(self,block):
        #make a node for the block and add into the history Node
        blocknode=Node(block.uniqueid)
        self.historyNodes[block.uniqueid]=blocknode
        
        #now add in the links between the block elements and the block into the historyNodes
        for elemid in block.element_unique_ids :
            self.historyNodes[elemid].add_child(blocknode)
            
    def __str__(self):
        descrip= "{ " 
        for block in self.blocks.iteritems() :
            #print "block " , block  , "endblock"
            descrip = descrip + block.__str__()
        descrip= descrip + "}\n"
        return descrip  
    
    def __repr__(self):
        return self.__str__()      
  
#alice todo improve?
#ruler = Distance()
 
