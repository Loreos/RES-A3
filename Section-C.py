#%% Info
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 21:39:37 2022

@author: lukas
"""
#%% Import
import pypsa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pypsa.linopt import get_dual, get_var

#%% Plotting options
#Set up plot parameters
color_bg      = "0.99"          #Choose background color
color_gridaxe = "0.85"          #Choose grid and spine color
rc = {"axes.edgecolor":color_gridaxe} 
plt.style.use(('ggplot', rc))           #Set style with extra spines
plt.rcParams['figure.dpi'] = 300        #Set resolution
plt.rcParams["figure.figsize"] = (10, 5) #Set figure size
matplotlib.rcParams['font.family'] = ['cmss10']     #Change font to Computer Modern Sans Serif
plt.rcParams['axes.unicode_minus'] = False          #Re-enable minus signs on axes))
plt.rcParams['axes.facecolor']= "0.99"              #Set plot background color
plt.rcParams.update({"axes.grid" : True, "grid.color": color_gridaxe}) #Set grid color
plt.rcParams['axes.grid'] = True

#%% Functions

def annuity(n,r):
    """Calculate the annuity factor for an asset with lifetime n years and
    discount rate of r, e.g. annuity(20,0.05)*20 = 1.6"""

    if r > 0:
        return r/(1. - 1./(1.+r)**n)
    else:
        return 1/n

#%% Control

run_model1  = True
run_model2  = True
run_model3  = True

#%% Data
Wind_CF     = [1.0, 0.8, 0.5, 0.25, 0.8]
PV_CF       = [0.5, 0.4, 0.3, 0.20, 0.1]

link_length = 58 #km

ccost_wind  = annuity(30, 0.07) * 910000  * 5/8760
ccost_PV    = annuity(30, 0.07) * 425000 * 5/8760
ccost_link  = annuity(30, 0.07) * 400*link_length * 5/8760

#%% 1 - DK1 Model

if run_model1:
    n1 = pypsa.Network() #Create Network
    t1 = pd.date_range('2022-01-01 00:00', '2022-01-01 04:00', freq = 'H')
    n1.set_snapshots(t1)
    
    n1.add("Bus",  "DK1") #Add DK1 bus
    
    #Add 2GW constant load
    n1.add("Load", 
           "DK1_Load",
           bus   = "DK1",
           p_set = 2000,)
    
    #Add wind generator capacity
    n1.add("Generator",
           "DK1_wind",
           bus              = "DK1",
           p_nom_extendable = True,
           p_max_pu         = Wind_CF,
           capital_cost     = ccost_wind,
           )
    
    n1.lopf(pyomo             = False,    #Disable Pyomo
            solver_name       = 'gurobi', #Choose Solver
            keep_shadowprices = True,     #Keep prices form Lagrange Multipliers
            )
    
    # ##### ----- Results ----- ##### -----------------------
    
    #Optimal Capacity
    n1.generators.p_nom_opt
    
    #Electricity price
    price1 = get_dual(n1, 'Bus', 'marginal_price').DK1.mean() #Get price in €/MWh
    
    #Alternative ways to get electricity prices:
    price1_0 = n1.buses_t.marginal_price.DK1.mean()
    
    price1_1 = n1.objective/n1.loads_t.p.DK1_Load.sum()

#%% 2 - DK2 Model

if run_model2:
    n2 = pypsa.Network()
    t2 = pd.date_range('2022-01-01 00:00', '2022-01-01 04:00', freq = 'H')
    n2.set_snapshots(t1)
    
    n2.add("Bus",  "DK2") #Add DK1 bus
    
    #Add 2GW constant load
    n2.add("Load", 
           "DK2_Load",
           bus = "DK2",
           p_set = 2000,)
    
    #Add solar generator capacity
    n2.add("Generator",
           "DK2_PV",
           bus              = "DK2",
           p_nom_extendable = True,
           p_max_pu         = PV_CF,
           capital_cost     = ccost_PV,
           )
    
    n2.lopf(pyomo             = False,    #Disable Pyomo
            solver_name       = 'gurobi', #Choose Solver
            keep_shadowprices = True,     #Keep prices form Lagrange Multipliers
            )
    
    # ##### ----- Results ----- ##### -----------------------
    
    #Optimal capacity
    n2.generators.p_nom_opt  #Optimal generator capacity
    
    #Electricity price
    price2 = get_dual(n2, 'Bus', 'marginal_price').DK2.mean() #Get price in €/MWh
    
    #Alternative ways to get electricity prices:
    price2_0 = n2.buses_t.marginal_price.DK2.mean()
    
    price2_1 = n2.objective/n2.loads_t.p.DK2_Load.sum()
    

#%% 3 - DK1 + DK2 Model

if run_model3:
    n3 = pypsa.Network()
    t3 = pd.date_range('2022-01-01 00:00', '2022-01-01 04:00', freq = 'H')
    n3.set_snapshots(t1)
    
    n3.madd("Bus",   ["DK1", "DK2"]) #Add DK1 and DK2 buses
    
    #Add constant loads of 2GW on each bus ----------------
    n3.madd("Load", 
           ["DK1_Load", "DK2_Load"],
           bus = ["DK1", "DK2"],
           p_set = 2000,)
    
    #Add link----------------------------------------------
    n3.add("Link",
           "DK1-DK2_link",
           bus0 = "DK1",
           bus1 = "DK2",
           capital_cost = ccost_link,
           p_nom_extendable = True,
           p_min_pu =  -1,              #Make link bidirectional
           )

    #Add wind generator capacity ---------------------------
    n3.add("Generator",
           "DK1_wind",
           bus              = "DK1",
           p_nom_extendable = True,
           p_max_pu         = Wind_CF,
           capital_cost     = ccost_wind,
           )
    
    #Add solar generator capacity --------------------------
    n3.add("Generator",
           "DK2_PV",
           bus              = "DK2",
           p_nom_extendable = True,
           p_max_pu         = PV_CF,
           capital_cost     = ccost_PV,
           )

    n3.lopf(pyomo             = False,    #Disable Pyomo
            solver_name       = 'gurobi', #Choose Solver
            keep_shadowprices = True,     #Keep prices form Lagrange Multipliers
            )
    
    # ##### ----- Results ----- ##### -----------------------
    
    #Optimal capacity
    n3.generators.p_nom_opt  #Optimal generator capacity
    n3.links.p_nom_opt       #Optimal link capacity
    
    #Get elecyticity
    price3_DK1  = get_dual(n3, 'Bus', 'marginal_price').DK1.mean() #Get price in €/MWh
    price3_DK2  = get_dual(n3, 'Bus', 'marginal_price').DK2.mean() #Get price in €/MWh
    
    #Alternative ways to get electricity prices:
    price3_0_DK1 = n3.buses_t.marginal_price.DK1.mean()
    price3_0_DK2 = n3.buses_t.marginal_price.DK2.mean()






