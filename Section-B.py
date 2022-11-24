#%% Info
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 13:04:05 2022

@author: lukas
"""

#%% Import
import numpy as np
import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format
import seaborn as sn
import matplotlib.pyplot as plt
import matplotlib

#%% Plotting options
#Set up plot parameters
color_bg      = "0.99"          #Choose background color
color_gridaxe = "0.85"          #Choose grid and spine color
rc = {"axes.edgecolor":color_gridaxe} 
plt.style.use(('ggplot', rc))           #Set style with extra spines
plt.rcParams['figure.dpi'] = 300        #Set resolution
matplotlib.rcParams['font.family'] = ['cmss10']     #Change font to Computer Modern Sans Serif
plt.rcParams['axes.unicode_minus'] = False          #Re-enable minus signs on axes))
plt.rcParams['axes.facecolor']= "0.99"              #Set plot background color
plt.rcParams.update({"axes.grid" : True, "grid.color": color_gridaxe}) #Set grid color
plt.rcParams['axes.grid'] = True

#%% 4 - Create list of nodes and links
# Create countries array and convert to nodes dataframe
countries = np.array(['DE', 'DK1', 'DK2', 'NO', 'SE'])
nodes = pd.DataFrame(data = countries,
                     columns = ['Country'])

#Create links dictionary and convert to dataframe
links = {
         'Link':['0-1', '1-2', '1-3', '1-4', '2-4'],
         'Connection':['DE-DK1', 'DK1-DK2', 'DK1-NO', 'DK1-SE', 'DK2-SE'],
         'From':[0, 1, 1, 1, 2],
         'To':[1, 2, 3, 4, 4]}
links = pd.DataFrame(data = links)

#%% 5 - Degree of nodes and network

# Calculate degree of each country by counting how many links the country 
# abbreviation is in
degrees_data = np.array([len(links[links['Connection'].str.contains('DE')]),
                    len(links[links['Connection'].str.contains('DK1')]),
                    len(links[links['Connection'].str.contains('DK2')]),
                    len(links[links['Connection'].str.contains('NO')]),
                    len(links[links['Connection'].str.contains('SE')]),
                          ])

#Convert to Dataframe
degrees = pd.DataFrame(data = {'Entity':countries, 
                               'Degree':degrees_data})

#Add row with average degree
degrees.loc[len(degrees.index)] = ['Average', degrees["Degree"].mean()]

#%% 6 - Degree matrix (D) and Adjacency matrix (A)

#Degree matrix (D)
D = np.zeros( (len(degrees[:len(countries)]), len(degrees[:len(countries)])) )
np.fill_diagonal(D, degrees['Degree'].values) # Fill diagonal with number of links
D = pd.DataFrame(data = D,
                 index = countries,
                 columns = countries)

#Initialize adjacency matrix (A)
A = np.zeros((len(countries),len(countries)))
A = pd.DataFrame(data = A,
                   index = countries,
                   columns = countries)

#Loop through all links and add them to adjacency matrix
for i in range(len(links)):
    A.iloc[links['From'][i], links['To'][i]] = 1
    A.iloc[links['To'][i], links['From'][i]] = 1

#%% 7 - Create the Incidence Matrix K

#Initialize K matrix
K = np.zeros( (len(nodes), len(links)) )
K = pd.DataFrame(data = K,
                 columns = links['Connection'],
                 index = countries)

# Loop through links in K and set start and stop nodes
for i in range(0, len(K.columns)):
    start  = links.iloc[i,:]['From']
    stop   = links.iloc[i,:]['To']
    
    K.iloc[:,i][start] = 1
    K.iloc[:,i][stop]  = -1
    

#%% 8 - Create the Laplacian Matrix L

# Laplacian using A and D
L1 = D - A

#Laplacian using K
L2 = np.dot(K, np.transpose(K))
L2 = pd.DataFrame(data = L2,
                  columns = countries,
                  index = countries)














