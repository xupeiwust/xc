# -*- coding: utf-8 -*-
''' Verify shear limit state checking using reinforcement placement routines
    (element-based reinforcement definition).'''

from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AOO)"
__copyright__= "Copyright 2015, LCPT and AOO"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import yaml
import math
import geom
import xc
from model import predefined_spaces
from materials.ec2 import EC2_materials
from materials.ec2 import EC2_limit_state_checking
from materials.sections.fiber_section import def_simple_RC_section
from actions import load_cases
from actions import combinations as combs
from postprocess import limit_state_data as lsd
from postprocess.config import default_config
from postprocess import RC_material_distribution

# Read reference values.
import os
pth= os.path.dirname(__file__)
#print("pth= ", pth)
if(not pth):
    pth= "."
fName= pth+"/../../../aux/common_values/shear_tests_5_and_6_ec2.yaml"
with open(fName) as file:
    try:
        valueData= yaml.safe_load(file)
    except yaml.YAMLError as exception:
        print(exception)
refMeanFC0= float(valueData['refMeanFC0'])
refMeanFC1= float(valueData['refMeanFC1'])

# Problem type
feProblem= xc.FEProblem()
preprocessor=  feProblem.getPreprocessor
nodes= preprocessor.getNodeHandler

modelSpace= predefined_spaces.StructuralMechanics3D(nodes)

# Define materials
## Materials.
concrete= EC2_materials.C30
steel= EC2_materials.S500B
## Geometry
b= 1.42
h= 0.20
## RC section.
rcSection= def_simple_RC_section.RCRectangularSection(name='BeamSection', width= 1.0, depth= h, concrType= concrete, reinfSteelType= steel)
dummySection= rcSection.defElasticMembranePlateSection(preprocessor) # Elastic membrane plate section.


# Problem geometry.
span= 5

## K-points.
points= preprocessor.getMultiBlockTopology.getPoints
pt1= points.newPoint(geom.Pos3d(0.0,0.0,0.0))
pt2= points.newPoint(geom.Pos3d(span,0.0,0.0))
pt3= points.newPoint(geom.Pos3d(span,b,0.0))
pt4= points.newPoint(geom.Pos3d(0.0,b,0.0))
## Surface.
surfaces= preprocessor.getMultiBlockTopology.getSurfaces
s= surfaces.newQuadSurfacePts(pt1.tag,pt2.tag,pt3.tag,pt4.tag)
s.nDivI= 10
s.nDivJ= 3

# Generate mesh.
seedElemHandler= preprocessor.getElementHandler.seedElemHandler
seedElemHandler.defaultMaterial= rcSection.name
elem= seedElemHandler.newElement("ShellMITC4",xc.ID([0,0,0,0]))
s.genMesh(xc.meshDir.I)

# Constraints.
fixedNodes= list()
for n in s.nodes:
    pos= n.getInitialPos3d
    if(abs(pos.x)<1e-3):
        fixedNodes.append(n)
    if(abs(pos.x-span)<1e-3):
        fixedNodes.append(n)
for n in fixedNodes:
    modelSpace.fixNode000_FFF(n.tag)

# Actions
loadCaseManager= load_cases.LoadCaseManager(preprocessor)
loadCaseNames= ['load']
loadCaseManager.defineSimpleLoadCases(loadCaseNames)

## load pattern.
load= xc.Vector([0.0,0.0,-80e3])  # No "in-plane" loads (see example 06 in the same folder).
cLC= loadCaseManager.setCurrentLoadCase('load')
for e in s.elements:
    e.vector3dUniformLoadGlobal(load)

## Load combinations
combContainer= combs.CombContainer()
### ULS combination.
combContainer.ULS.perm.add('combULS01','1.6*load')
xcTotalSet= preprocessor.getSets.getSet('total')
cfg= default_config.get_temporary_env_config()
lsd.LimitStateData.envConfig= cfg
### Save internal forces.
lsd.shearResistance.saveAll(combContainer,xcTotalSet) 

# Define reinforcement.
# Reinforcement row scheme:
#
#    |  o    o    o    o    o    o    o    o    o    o  |
#    <->           <-->                               <-> 
#    lateral      spacing                           lateral
#     cover                                          cover
#

# Geometry of the reinforcement.
nBarsA= 7 # number of bars.
cover= 0.035 # concrete cover.
lateralCover= cover # concrete cover for the bars at the extremities of the row.
spacing= (rcSection.b-2.0*lateralCover)/(nBarsA-1)

## First row.
mainBarDiameter= 25e-3 # Diameter of the reinforcement bar.
mainBarArea= math.pi*(mainBarDiameter/2.0)**2 # Area of the reinforcement bar.
rowA= def_simple_RC_section.ReinfRow(rebarsDiam= mainBarDiameter, areaRebar= mainBarArea, rebarsSpacing= spacing, width= rcSection.b, nominalCover= cover, nominalLatCover= lateralCover)

## Second row.
rowB= def_simple_RC_section.ReinfRow(rebarsDiam= mainBarDiameter, areaRebar= mainBarArea, rebarsSpacing= spacing, width= rcSection.b-spacing, nominalCover= cover, nominalLatCover= lateralCover+spacing/2.0)

## Third row.
smallBarDiameter= 4e-3
smallBarArea= math.pi*(smallBarDiameter/2.0)**2 # Area of the reinforcement bar.
rowC= def_simple_RC_section.ReinfRow(rebarsDiam= smallBarDiameter, areaRebar= smallBarArea, rebarsSpacing= spacing, width= rcSection.b, nominalCover= cover, nominalLatCover= lateralCover+spacing/2.0)

# Shear reinforcement at both ends.
fi8Area= EC2_materials.rebars['fi08']['area']
shearReinf= def_simple_RC_section.ShearReinforcement(familyName= "shearReinf",nShReinfBranches= 2, areaShReinfBranch= fi8Area, shReinfSpacing= 0.15, angAlphaShReinf= math.pi/2.0)

## Store element reinforcement.
for e in s.elements:
    e.setProp("baseSection", rcSection)
    e.setProp("reinforcementUpVector", geom.Vector3d(0,0,1)) # Z+
    e.setProp("reinforcementIVector", geom.Vector3d(1,0,0)) # X+
    e.setProp("bottomReinforcementI", def_simple_RC_section.LongReinfLayers([rowA]))
    e.setProp("topReinforcementI", def_simple_RC_section.LongReinfLayers([rowC]))
    e.setProp("bottomReinforcementII", def_simple_RC_section.LongReinfLayers([rowC]))
    e.setProp("topReinforcementII", def_simple_RC_section.LongReinfLayers([rowC]))
    x= e.getPosCentroid(True).x
    if(x>1.5 and x<3.5): # more bending reinforcement.
        bottomReinforcementI= e.getProp("bottomReinforcementI")
        bottomReinforcementI.append(rowB)
        e.setProp("bottomReinforcementI", bottomReinforcementI)
    else: # shear reinforcement.
        e.setProp("shearReinforcementI", shearReinf)
        
#### Define sections.

# Define spatial distribution of reinforced concrete sections.
reinfConcreteSectionDistribution= RC_material_distribution.RCMaterialDistribution()
reinfConcreteSectionDistribution.assignFromElementProperties(elemSet= xcTotalSet.getElements)
#reinfConcreteSectionDistribution.report()

# Checking shear stresses.
outCfg= lsd.VerifOutVars(listFile='N',calcMeanCF='Y')
outCfg.controller= EC2_limit_state_checking.ShearController(limitStateLabel= lsd.shearResistance.label)
outCfg.controller.verbose= False # Don't display log messages.

feProblem.logFileName= "/tmp/erase.log" # Ignore warning messagess about computation of the interaction diagram.
feProblem.errFileName= "/tmp/erase.err" # Ignore warning messagess about maximum error in computation of the interaction diagram.
(FEcheckedModel,meanFCs)= reinfConcreteSectionDistribution.runChecking(lsd.shearResistance, matDiagType="d",threeDim= True,outputCfg=outCfg)  
feProblem.errFileName= "cerr" # From now on display errors if any.
feProblem.logFileName= "clog" # From now on display warnings if any.

ratio1= abs(meanFCs[0]-refMeanFC0)/refMeanFC0
ratio2= abs(meanFCs[1]-refMeanFC1)/refMeanFC1

'''
print('meanFCs= ',meanFCs)
print('reference values: ', refMeanFC0, refMeanFC1)
print("ratio1= ",ratio1)
print("ratio2= ",ratio2)
'''

import os
from misc_utils import log_messages as lmsg
fname= os.path.basename(__file__)
if (ratio1<1e-4) and (ratio2<1e-4):
    print('test '+fname+': ok.')
else:
    lmsg.error(fname+' ERROR.')
    
# # #########################################################
# # # Graphic stuff.
# from postprocess import output_handler
# oh= output_handler.OutputHandler(modelSpace)

# # oh.displayFEMesh()
# #Load properties to display:
# from postprocess.control_vars import *
# exec(open(cfg.projectDirTree.getVerifShearFile()).read())
# argument= 'CF' #Possible arguments: 'CF','Vy','Vz'
# oh.displayFieldDirs1and2(limitStateLabel=lsd.shearResistance.label, argument=argument, setToDisplay= xcTotalSet, component=None, fileName=None, defFScale=0.0,rgMinMax= None)

cfg.cleandirs()  # Clean after yourself.