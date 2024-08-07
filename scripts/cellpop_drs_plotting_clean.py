# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 22:58:16 2023

@author: Arnab
"""
# import required libraries

import pickle
import re

import itertools
import math

import os
import sys

import libsbml
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore
import copy

from Bio import Phylo

from io import StringIO

from scipy.interpolate import interp1d
from scipy.stats import percentileofscore
from scipy.stats import gaussian_kde
import math
import seaborn as sns
import itertools
import plotly.figure_factory as ff
import plotly.io as pio


import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['figure.dpi'] = 300
mpl.rcParams['font.sans-serif'] = ['Arial']


#%%
cd = os.getcwd()
wd = os.path.dirname(cd)
sys.path.append(os.path.join(wd,'bin'))

sbml_file = "SPARCED.xml"


sbml_reader = libsbml.SBMLReader()
sbml_doc = sbml_reader.readSBML(os.path.join(wd,sbml_file))
sbml_model = sbml_doc.getModel()

species_all = [str(x.getId()) for x in list(sbml_model.getListOfSpecies())]





#%%
output_dir_main = os.path.join(wd,'output')

exp_title = 'in_silico_drs'
output_main = os.path.join(wd,'output',exp_title)



dir_doses_all = os.listdir(os.path.join(output_main,'drs_alpel','drs_alpel_rep1'))

doses_all = [float(x.split('_')[-1]) for x in dir_doses_all]

doses_all.sort()


#%%

# import class for reading dose response outputs

from modules.drsPlotting import drs_dict




    
#%%
exp_title = 'in_silico_drs'
output_main = os.path.join(wd,'output',exp_title)
# output_main = os.path.join("E:\\",exp_title)

output_noegf = os.path.join(wd,'output','mcf10a_noegf')
output_nostim = os.path.join(wd,'output','mcf10a_nostim')

dict_noegf = drs_dict(output_noegf,'nerat',1,0)
dict_nostim = drs_dict(output_nostim,'nerat',1,0)

exp_drs2 = 'in_silico_drs2'
output_drs2 = os.path.join(wd,'output',exp_drs2)

exp_drs3 = 'in_silico_drs3'
output_drs3 = os.path.join(wd,'output',exp_drs3)

#%% test - load data

trame1_7 = drs_dict(output_main,'trame',1,7)

trame1_7.get_desc(4)

trame1_7.get_g1desc()



#%% count g1 descendents for all control conditions

drugs_all = ['alpel','lapat','nerat','palbo','trame']

g1desc_all = []

for drug in drugs_all:
    for rep in range(10):
        print(drug+'.....'+str(rep+1))
        control_dict = drs_dict(output_main,drug,rep+1,0)
        g1desc_all.append(control_dict.get_g1desc())

np.savetxt(os.path.join(wd,'output','in_silico_drs_summary','g1_desc_control.tsv'),np.array(g1desc_all),delimiter='\t')

plt.figure()

plt.hist(np.array(g1desc_all).flatten())
plt.show()

# fast > 25, 0 < moderate <25 



#%% split lineage for cell groups, find terminal lineages

    # for g1cx in grp2:
        
# g1cx = 39

trame2_5 = drs_dict(output_main,'trame',2,5)

drs_dict_test = trame2_5
        
# tout = drs_dict_test.results['output_g1'][str(g1cx)]['output']['tout']/3600
# obs = np.array(obs_grp2[str(g1cx)])[:,obs_idx]
# plt.plot(tout,obs,color='blue',label='grp2')

term_lins = []

for g1cx in trame2_5.grp2:

    desc_all = drs_dict_test.get_desc(g1cx)
    
    n_desc_all = len([item for sublist in desc_all.values() for item in sublist])
    
    
    
    
    
    if n_desc_all > 0:
        
        for gn in range(len(desc_all.keys())):
            gen = gn+2
            gncxs = desc_all['g'+str(gen)]
            if len(gncxs)>0:
                for cx in range(len(gncxs)):
                    gncx = gncxs[cx]
                    desc_gncx = drs_dict_test.get_desc_gc(gen,gncx)
                    if len(desc_gncx) == 0:
                        lin_gncx = drs_dict_test.results['output_g'+str(gen)][str(gncx)]['output']['lin']
                        lin_gncx = lin_gncx+'c'+str(gncx)
                        term_lins.append(lin_gncx)
 
term_lins_outputs = {}

for term_lin in term_lins:
    
    outputs_lin = {}
    
    lin_cells = term_lin.split('c')[1:]
    
    gn = 1
    
    xout_lin = []
    tout_lin = []
    
    for gncx in lin_cells:
        
        output_gncx = drs_dict_test.results['output_g'+str(gn)][str(gncx)]['output']
        xout_gncx = output_gncx['xoutS']
        tout_gncx = output_gncx['tout']
        
        xout_lin.append(xout_gncx)
        tout_lin.append(tout_gncx)
        
        gn+= 1
        
    xout_lin = np.concatenate(xout_lin,axis=0)
    tout_lin = np.concatenate(tout_lin,axis=0)
    
    outputs_lin['xoutS'] = xout_lin
    outputs_lin['tout'] = tout_lin
    
    term_lins_outputs[term_lin] = outputs_lin
    
#%%

term_lin  = list(term_lins_outputs.keys())[7]
    
xout_lin = term_lins_outputs[term_lin]['xoutS']

tout_lin = term_lins_outputs[term_lin]['tout']

touts_lin = [term_lins_outputs[term_lin_key]['tout'] for term_lin_key in term_lins_outputs.keys()]

touts_lin = [item for sublist in touts_lin for item in sublist]

touts_lin = np.unique(np.array(touts_lin))

touts_lin = touts_lin[:-200]

interpolated_values = interp1d(tout_lin, xout_lin, axis=0)(touts_lin)


# xx = trame2_5.term_lins(grp2)

#%% example species trajectory for terminal lineages

# all

sp_lin = 'ppAKT'

for term_lin in list(term_lins_outputs.keys()):
    
    xout_lin = term_lins_outputs[term_lin]['xoutS']
    tout_lin = term_lins_outputs[term_lin]['tout']
    sp_traj = xout_lin[:,list(species_all).index(sp_lin)]
    
    plt.plot(tout_lin/3600,sp_traj)
    
plt.show()
    
#% single lineage

term_lins_test = term_lins_outputs

sp_lin = 'Mb'

term_lin  = list(term_lins_test.keys())[9]
    
xout_lin = term_lins_test[term_lin]['xoutS']
tout_lin = term_lins_test[term_lin]['tout']
sp_traj = xout_lin[:,list(species_all).index(sp_lin)]

plt.figure()

plt.plot(tout_lin/3600,sp_traj)
plt.title(str(term_lin))
    
plt.show()



#%% compare grp2/grp0

xx = trame2_5.term_lins(trame2_5.grp2)

term_lin = list(xx.keys())[0]

g1cx_grp0 = 3

output_g0 = drs_dict_test.results['output_g1'][str(g1cx_grp0)]['output']

xout_g0 = output_g0['xoutS']
tout_g0 = output_g0['tout']

xout_g2 = xx[term_lin]['xoutS']
tout_g2 = xx[term_lin]['tout']

tout_compare = np.unique(np.concatenate((tout_g0,tout_g2)))

tp_final = min(max(tout_g0),max(tout_g2))

tout_compare = tout_compare[:np.where(tout_compare >= tp_final)[0][0]]

xout_g0_new = interp1d(tout_g0,xout_g0,axis=0)(tout_compare)
xout_g2_new = interp1d(tout_g2,xout_g2,axis=0)(tout_compare)

xout_diff = (xout_g2_new - xout_g0_new)/xout_g0_new


#%%

sp_compare = 'ppAKT'

y0 = xout_g0_new[:,list(species_all).index(sp_compare)]
y2 = xout_g2_new[:,list(species_all).index(sp_compare)]

plt.plot(tout_compare/3600,y0,label='x_group0')
plt.plot(tout_compare/3600,y2,label='x_group2')



ymax = max(max(y0),max(y2))

plt.ylim(0,ymax*1.25)

plt.xlabel('Time (hours)')
plt.ylabel('Species concentration (nM)')
plt.legend()

plt.show()






#%%


def normalized_me(array1, array2, epsilon=1e-10):
    """
    Calculate the normalized mean squared error between two arrays.
    """
    numerator = array1 - array2
    denominator = array2 + epsilon  # Avoid division by zero
    return np.square(numerator) / np.square(denominator)

#%%


xout_error = normalized_me(xout_g2_new, xout_g0_new)




sp_auc = pd.Series(np.array([np.trapz(xout_error[:,sp_idx],tout_compare) for sp_idx in range(np.shape(xout_error)[1])]),index=species_all)

#%%

plt.plot(tout_compare/3600,xout_error[:,list(species_all).index(sp_compare)])
plt.ylabel('Squared normalized error')
plt.xlabel('Time (hours)')

plt.show()


#%%


plt.hist(sp_auc.values,bins=np.logspace(-8,18,27))

plt.xscale('log')

plt.show()

#%% compare grp0/grp2 for all combinations

term_lins_test = drs_dict_test.term_lins(drs_dict_test.grp2)

# for term_lin in list(term_lins_test.keys()):
    
term_lin = list(term_lins_test.keys())[0]

sp_ranks_all = []
sp_auc_all = []


for term_lin in term_lins_test:

    
    for g1cx_grp0 in trame2_5.grp0:
        output_g0 = trame2_5.results['output_g1'][str(g1cx_grp0)]['output']
        xout_g0 = output_g0['xoutS']
        tout_g0 = output_g0['tout']
        
        traj_g0_parp = xout_g0[:,list(species_all).index('PARP')]
        traj_g0_cparp = xout_g0[:,list(species_all).index('cPARP')]
        
        traj_g0_ratio = traj_g0_cparp/traj_g0_parp
        
        traj_flagA = np.where(traj_g0_ratio>1)[0]
        
        if len(traj_flagA)>0:
            td_idx = traj_flagA[0]
            
            tout_g0 = tout_g0[:td_idx]
            xout_g0 = xout_g0[:td_idx,:]
        
        
        if len(tout_g0)>0:
        
            xout_g2 = term_lins_test[term_lin]['xoutS']
            tout_g2 = term_lins_test[term_lin]['tout']
            
            tout_compare = np.unique(np.concatenate((tout_g0,tout_g2)))
        
            tp_final = min(max(tout_g0),max(tout_g2))
            
            tout_compare = tout_compare[:np.where(tout_compare >= tp_final)[0][0]]
            
            xout_g0_new = interp1d(tout_g0,xout_g0,axis=0)(tout_compare)
            xout_g2_new = interp1d(tout_g2,xout_g2,axis=0)(tout_compare)
            
            epsilon=1e-10
            
            numerator = xout_g2_new - xout_g0_new
            denominator = xout_g2_new + epsilon
            
            xout_error = np.square(numerator) / np.square(denominator)
            
            sp_auc = pd.Series(np.array([np.trapz(xout_error[:,sp_idx],tout_compare) for sp_idx in range(np.shape(xout_error)[1])]),index=species_all)
            
            # sp_auc_sorted = sp_auc.sort_values()
            
            sp_ranked = pd.Series(np.array([percentileofscore(sp_auc.values,x) for x in sp_auc.values]),index=species_all)
            
            sp_ranks_all.append(sp_ranked.values)
            sp_auc_all.append(sp_auc.values)
        
    # rank species by error auc
    # aggregate for all pairs



# sp_ranks_final = pd.Series(sum(np.array(sp_ranks_all)),index=species_all)

sp_ranks_final = pd.DataFrame(index=species_all)
sp_ranks_final['score'] = sum(np.array(sp_ranks_all))
sp_ranks_final['auc'] = sum(np.array(sp_auc_all))


# sp_ranks_final = sp_ranks_final.sort_values()

#%%



# plt.hist(sp_ranks_final.values,bins=np.logspace(-8,18,27))

plt.hist(sp_ranks_final.values)


plt.xscale('log')

plt.show()

#%% oop ranking code test

dict1 = drs_dict(output_main,'trame',1,0)

srf001 = dict1.rank_sp()

dict2 = drs_dict(output_main,'trame',5,0)

srf002 = dict2.rank_sp()


#%% generate species ranks for all dose levels of Trametinib



for dl in range(10):
    dict_0 = drs_dict(output_main,'trame',1,dl)
    
    srf = dict_0.rank_sp()
    
    for rep in range(1,10):
        
        dict_current = drs_dict(output_main,'trame',rep+1,dl)
        
        srf_n = dict_current.rank_sp()
        
        srf = srf + srf_n
        
    
    srf.to_csv(os.path.join(wd,'output','in_silico_drs_summary','trame_rank_sp_'+str(dl)+'.tsv'),sep='\t')

#%% species ranks heatmaps / mRNA

srf_trame = {}

for dl in range(10):
    srf_read = pd.read_csv(os.path.join(wd,'output','in_silico_drs_summary','trame_rank_sp_'+str(dl)+'.tsv'),sep='\t',index_col=0,header=0)
    srf_trame[str(dl)] = srf_read


#%

model_genes = list(pd.read_csv(os.path.join(wd,'input_files','OmicsData.txt'),sep='\t',index_col=0).index)

srf_heatmap = pd.DataFrame(index=['dl_'+str(dl) for dl in range(10)],columns = ['m_'+str(gene) for gene in model_genes],dtype='float')

for dl in range(10):
    
    srf_mrna = np.array([srf_trame[str(dl)].loc[spc,'score'] for spc in srf_heatmap.columns])
    
    srf_heatmap_dl = [percentileofscore(srf_trame[str(dl)].loc[:,'score'].values,x) for x in srf_mrna]
    
    srf_heatmap.loc['dl_'+str(dl),:] = srf_heatmap_dl


#%

plt.figure(figsize=(24,32))

sns.heatmap(srf_heatmap.iloc[:,:141].transpose())

# plt.show()

plt.savefig(os.path.join(wd,'output','in_silico_drs_summary','mRNA_heatmap.png'))

plt.figure(figsize=(12,16))

sns.clustermap(srf_heatmap.transpose())

plt.show()

#%% 

genes_top = []

pm = 90 # percentile margin

for gene in model_genes:
    
    vals = srf_heatmap.loc[:,'m_'+str(gene)].values
    
    vals_check = vals>pm
    
    if vals_check.all():
        genes_top.append(gene)


#%

srf_heatmap_top = pd.DataFrame(index=['dl_'+str(dl) for dl in range(10)],columns = ['m_'+str(gene) for gene in genes_top],dtype='float')

for gene in genes_top:
        
    srf_heatmap_top.loc[:,'m_'+str(gene)] = srf_heatmap.loc[:,'m_'+str(gene)]
    
plt.figure(figsize=(12,16))

sns.heatmap(srf_heatmap_top.transpose())

plt.show()



plt.figure(figsize=(12,16))

sns.clustermap(srf_heatmap_top.transpose())

plt.show()

# plt.savefig(os.path.join(wd,'output','in_silico_drs_summary','mRNA_heatmap.png'))

#%% plot log10 transformed AUC sum for all species (from pairwise comparisons)

x1= srf_trame['0']['auc'].values

x2 = np.log10(x1)

x3= x2[~np.isinf(x2)]

x4 = x3[x3>0]

plt.hist(x4)
plt.show()


# plt.hist(x4,bins=10)
# plt.show()






#%% 




#%% define formula for plotting obs


ObsMat = pd.read_csv(os.path.join(wd,'input_files','Observables.txt'),sep='\t',header=0,index_col=0)
Species_doc = pd.read_csv(os.path.join(wd,'input_files','Species.txt'),sep='\t',header=0,index_col=0)
Compartment_vol = pd.read_csv(os.path.join(wd,'input_files','Compartments.txt'),sep='\t',header=0,index_col=0)

# ppERK/total ERK

sp_erk = list(np.array(species_all)[np.where(ObsMat.loc[:,'ERK'].values)[0]])

sp_pperk = list(np.array(sp_erk)[np.where(['ppERK' in sp_erk[k] for k in range(len(sp_erk))])[0]])

formula_num = ''

for sp in sp_pperk:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'ERK'])*float(Compartment_vol.loc[sp_comp,'volume'])
    num_item = str(sp)+'*'+str(multiplier)
    formula_num = formula_num+'+'+num_item

formula_num = formula_num[1:]

formula_den = ''

for sp in sp_erk:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'ERK'])*float(Compartment_vol.loc[sp_comp,'volume'])
    den_item = str(sp)+'*'+str(multiplier)
    formula_den = formula_den+'+'+den_item

formula_den = formula_den[1:]

formula_ppERK = '(' + formula_num + ')/(' + formula_den + ')'


## ppAKT/total AKT

sp_akt = list(np.array(species_all)[np.where(ObsMat.loc[:,'AKT'].values)[0]])

sp_ppakt = list(np.array(sp_akt)[np.where(['ppAKT' in sp_akt[k] for k in range(len(sp_akt))])[0]])

formula_num = ''

for sp in sp_ppakt:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'AKT'])*float(Compartment_vol.loc[sp_comp,'volume'])
    num_item = str(sp)+'*'+str(multiplier)
    formula_num = formula_num+'+'+num_item

formula_num = formula_num[1:]

formula_den = ''

for sp in sp_akt:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'AKT'])*float(Compartment_vol.loc[sp_comp,'volume'])
    den_item = str(sp)+'*'+str(multiplier)
    formula_den = formula_den+'+'+den_item

formula_den = formula_den[1:]

formula_ppAKT = '(' + formula_num + ')/(' + formula_den + ')'

#% fractional EGFR inhibition

sp_EGFR = list(np.array(species_all)[np.where(ObsMat.loc[:,'E1'].values)[0]])

sp_EGFR_nerat = list(np.array(sp_EGFR)[np.where(['nerat' in sp_EGFR[k] for k in range(len(sp_EGFR))])[0]])


formula_num_egfr = ''

for sp in sp_EGFR_nerat:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'E1'])*float(Compartment_vol.loc[sp_comp,'volume'])
    num_item = str(sp)+'*'+str(multiplier)
    formula_num_egfr = formula_num_egfr +'+'+num_item

formula_num_egfr = formula_num_egfr[1:]

formula_den_egfr = ''

for sp in sp_EGFR:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'E1'])*float(Compartment_vol.loc[sp_comp,'volume'])
    den_item = str(sp)+'*'+str(multiplier)
    formula_den_egfr = formula_den_egfr+'+'+den_item

formula_den_egfr = formula_den_egfr[1:]

formula_egfr = '(' + formula_num_egfr + ')/(' + formula_den_egfr + ')'

#% palbociclib target engagement

sp_Md = list(np.array(species_all)[np.where(ObsMat.loc[:,'Cd'].values)[0]])

sp_Md.remove('Cd')

sp_Md_drug = list(np.array(sp_Md)[np.where(['palbo' in sp_Md[k] for k in range(len(sp_Md))])])

formula_num_palbo_target = ''

for sp in sp_Md_drug:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'Cd'])*float(Compartment_vol.loc[sp_comp,'volume'])
    num_item = str(sp)+'*'+str(multiplier)
    formula_num_palbo_target = formula_num_palbo_target +'+'+num_item
    
formula_num_palbo_target = formula_num_palbo_target[1:]
    
formula_den_palbo_target = ''

for sp in sp_Md:
    sp_comp = Species_doc.loc[sp,'compartment']
    multiplier = float(ObsMat.loc[sp,'Cd'])*float(Compartment_vol.loc[sp_comp,'volume'])
    den_item = str(sp)+'*'+str(multiplier)
    formula_den_palbo_target = formula_den_palbo_target +'+'+den_item

formula_den_palbo_target = formula_den_palbo_target[1:]

formula_palbo_target = '(' + formula_num_palbo_target + ')/(' + formula_den_palbo_target + ')'





#%%

def pop_obs_plot(obs_array,timepoints):
    obs_mean = np.array([np.nanmean(obs_array[:,tp]) for tp in range(len(timepoints))])
    obs_sd = np.array([np.nanstd(obs_array[:,tp]) for tp in range(len(timepoints))])


    for cell in range(np.shape(obs_array)[0]):
        plt.plot(timepoints/3600,obs_array[cell,:],linewidth=0.5,color='grey')
    
    plt.plot(timepoints/3600,obs_mean,linewidth=2.0,color='red',label='Mean')
    plt.plot(timepoints/3600,obs_mean+obs_sd,linewidth=2.0,color='blue',label='+SD')
    plt.plot(timepoints/3600,obs_mean-obs_sd,linewidth=2.0,color='blue',label='-SD')
    
    
    ymax = np.nanmax(obs_array)*1.25
    
    plt.ylim(0,ymax)
    plt.xlim(0,74)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(bbox_to_anchor=(1.2,1.2),fontsize=20)
    
    plt.show()
    
#%% dose specific neratinib target engagement - Figure 4B

for dl in range(len(doses_all)):
    dose_dict = drs_dict(output_main,'nerat',1,dl)
    cells,tps,tout_deaths,obs_array = dose_dict.pop_dyn_obs(formula_egfr)
    obs_median = np.array([np.nanmedian(obs_array[:,tp]) for tp in range(len(tps))])
    plt.plot(tps/3600,obs_median,label=f"{doses_all[dl]:.3f}")
    
plt.ylim(0,1.2)
plt.xlim(0,74)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.legend(bbox_to_anchor=(1.05,1.1),title='Doses (\u03BCM)',fontsize=15,title_fontsize=15)
plt.show()        

#%% dose specific erk activity (old figure 5 C-E)

for dl in range(len(doses_all)):
    dose_dict = drs_dict(output_main,'nerat',1,dl)
    cells,tps,tout_deaths,obs_array = dose_dict.pop_dyn_obs(formula_ppERK)
    pop_obs_plot(obs_array,tps)

#%% dose specific palbociclib target engagement - Figure 3A

for dl in range(len(doses_all)):
    dose_dict = drs_dict(output_main,'palbo',1,dl)
    cells,tps,tout_deaths,obs_array = dose_dict.pop_dyn_obs(formula_palbo_target)
    obs_median = np.array([np.nanmedian(obs_array[:,tp]) for tp in range(len(tps))])
    plt.plot(tps/3600,obs_median,label=f"{doses_all[dl]:.3f}")
    
# plt.ylim(0,1.2)
plt.xlim(0,74)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.legend(bbox_to_anchor=(1.05,1.1),title='Doses (\u03BCM)',fontsize=15,title_fontsize=15)
plt.show()   





#%% dose response population dynamics

# drug = 'alpel'

# drs_drug = {}

def drs_summarize(drug,dose_lvl,output_dir=output_main): # measures alive cell count from each simulation
    
    drs_dose = {}
    for rep in range(10):
        print('now running...'+str(drug)+'...'+str(dose_lvl)+'...'+str(rep+1))
        drs_dict0 = drs_dict(output_dir,drug,rep+1,dose_lvl)
        pd,tp,td = drs_dict0.pop_dyn()
        drs_rep = {}
        drs_rep['cellpop'] = pd
        drs_rep['tout'] = tp
        drs_rep['t_death'] = td
        drs_dose['r'+str(rep+1)] = drs_rep
    return drs_dose

#%%
drugs_exp = ['Alpelisib','Neratinib','Trametinib','Palbociclib']

drs_all = {}

#%

for dr_idx in range(len(drugs_exp)):
    
    drug = drugs_exp[dr_idx][:5].lower()
    
    
    drs_drug = {}
    
    for d in range(10):
        
        drs_dose = drs_summarize(drug, d)
        drs_drug['d'+str(d)] = drs_dose
        
    drs_all[drug] = drs_drug

#%

pickle.dump(drs_all, open(os.path.join(wd,'output','in_silico_drs_summary','drs_summary.pkl'),'wb'))

#%% replicate median dose respnose population dynamics


drs_median = {}

drugs = list(drs_all.keys())

for dr in drugs:
    
    drs_median_drug = {}
    
    for dl in range(10):
        
        drs_median_dose = {}
        
        tp_drs = [drs_all[dr]['d'+str(dl)]['r'+str(rep+1)]['tout'] for rep in range(10)]
        popdyn_reps0 = [drs_all[dr]['d'+str(dl)]['r'+str(rep+1)]['cellpop'] for rep in range(10)]
        tp_all = np.array(list(itertools.chain(*tp_drs)))
        tp_all = np.unique(tp_all)
        tp_max = min([tp_drs[x][-1] for x in range(len(tp_drs))])
        tp_max_idx = np.where(tp_all == tp_max)[0][0]
        tp_all = tp_all[:tp_max_idx+1]
        popdyn_reps = []
        for rep in range(10):
            interpolator = interp1d(tp_drs[rep],popdyn_reps0[rep])
            y_new = interpolator(tp_all)
            popdyn_reps.append(y_new)
            
        popdyn_med = np.median(popdyn_reps,axis=0)
        
        drs_median_dose['cellpop'] = popdyn_med
        drs_median_dose['tout'] = tp_all
        
        drs_median_drug['d'+str(dl)] = drs_median_dose
        
    drs_median[dr] = drs_median_drug

#%

pickle.dump(drs_median, open(os.path.join(wd,'output','in_silico_drs_summary','drs_median.pkl'),'wb'))

#%%

with open(os.path.join(wd,'output','in_silico_drs_summary','drs_summary.pkl'),'rb') as f:
    drs_summary_full = pickle.load(f)

with open(os.path.join(wd,'output','in_silico_drs_summary','drs_median.pkl'),'rb') as f:
    drs_summary_median = pickle.load(f)



#%% drs_plots % median population dynamics

drugs_exp = ['Alpelisib','Neratinib','Trametinib','Palbociclib']

drug_idx = 2

drug = drugs_exp[drug_idx][:5].lower()

for dl in range(10):
    
    dose = doses_all[dl]
    
    x_dl = drs_median[drug]['d'+str(dl)]['tout']/3600
    y_dl = drs_median[drug]['d'+str(dl)]['cellpop']
    
    plt.plot(x_dl,y_dl,label=f"{doses_all[dl]:.3f}")
    

plt.legend(bbox_to_anchor=(1.05,1.05),title='Doses (\u03BCM)',fontsize=15,title_fontsize=15)
plt.ylim(0,550)
plt.xlim(0,72)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
# plt.xlabel('Time (h)')
# plt.ylabel('# of cells')
# plt.title(drugs_exp[2])
plt.show()

#%%

with open(os.path.join(wd,'output','in_silico_drs_summary','drs_summary.pkl'),'rb') as f:
    drs_summary_full = pickle.load(f)





#%%


def gr_calc_row3 (drug,time_h,dl,rep,drs_summary_dict,cell_line='mcf10a_sim'):
    
    dose = doses_all[dl]
    
    dose_dict = drs_summary_dict[str(drug)]['d'+str(dl)]['r'+str(rep+1)]
    cellpop = dose_dict['cellpop']
    tout = dose_dict['tout']
 
    interpolator = interp1d(tout,cellpop)
    cell_count = interpolator(time_h*3600)
    cell_count_time0 = dose_dict['cellpop'][0]
    
    drugs_all = list(drs_summary_dict.keys())
 
    
    ctrl_pool = []
    
    for dr in drugs_all:
        for rp in range(1,len(drs_summary_dict[dr]['d0'].keys())+1):
            rp_dict = drs_summary_dict[dr]['d0']['r'+str(rp)]
            rp_cellpop = np.array(rp_dict['cellpop'])
            rp_tout = np.array(rp_dict['tout'])
            
            rp_interp = interp1d(rp_tout,rp_cellpop)
            rp_cellcount = float(rp_interp(time_h*3600))
            ctrl_pool.append(rp_cellcount)
            
    dose_pool = []
    
    for rp in range(1,len(drs_summary_dict[drug]['d'+str(dl)].keys())+1):
        rp_dose_dict = drs_summary_dict[drug]['d'+str(dl)]['r'+str(rp)]
        rp_dose_cellpop = np.array(rp_dose_dict['cellpop'])
        rp_dose_tout = np.array(rp_dose_dict['tout'])
        
        rp_dose_interp = interp1d(rp_dose_tout,rp_dose_cellpop)
        rp_dose_cellcount = float(rp_dose_interp(time_h*3600))
        dose_pool.append(rp_dose_cellcount)    
 
    cell_count_percentile = percentileofscore(dose_pool, cell_count)
    cell_count_ctrl = np.percentile(ctrl_pool,cell_count_percentile)


    new_row = {}
    new_row['cell_line'] = cell_line
    new_row['agent'] = str(drug)
    new_row['timepoint'] = time_h
    new_row['concentration'] = dose
    new_row['cell_count'] = cell_count
    new_row['cell_count__ctrl'] = cell_count_ctrl
    new_row['cell_count__time0'] = cell_count_time0 
    
    
    return new_row




#%%

time_h = [48,72]

drs_grcalc3 = pd.DataFrame(data=None,columns=['cell_line','agent','timepoint','concentration','cell_count','cell_count__ctrl','cell_count__time0'])



for drug in drs_summary_full.keys():
    for dl in range(1,len(drs_summary_full[str(drug)].keys())):
        for rep in range(len(drs_summary_full[str(drug)]['d'+str(dl)].keys())):
            for t in time_h:
                new_row = gr_calc_row3(drug,t,dl,rep,drs_summary_full)
                drs_grcalc3 = drs_grcalc3.append(new_row, ignore_index=True)


drs_grcalc3.to_csv(os.path.join(wd,'output','in_silico_drs_summary','drs_grcalc3.tsv'),sep='\t',index=False)


#%%

drs_all_gr = pd.read_csv(os.path.join(wd,'output','in_silico_drs_summary','drs_grcalc3_grc.tsv'),sep='\t')



#%% load exp data

# drs_gr_exp = pd.read_csv(os.path.join(wd,'output','in_silico_drs_summary','grvalues_merged.csv'),sep=',')

dir_exp = os.path.join(wd,'output','in_silico_drs_summary','mcf10a_drs_exp')

drs_gr_exp = {}

grv_c1a1_data = pd.read_csv(os.path.join(dir_exp,'GRvalues_center1_scientistA_2017.csv'),sep=',')

grv_c1a1 = pd.DataFrame()

grv_c1a1['cell_line'] = grv_c1a1_data['cell_line']
grv_c1a1['agent'] = grv_c1a1_data['agent']
grv_c1a1['concentration'] = grv_c1a1_data['concentration']
grv_c1a1['cell_count'] = grv_c1a1_data['cell_count']
grv_c1a1['cell_count__ctrl'] = grv_c1a1_data['cell_count__ctrl']
grv_c1a1['cell_count__time0'] = grv_c1a1_data['cell_count__time0']
grv_c1a1['GRvalue'] = grv_c1a1_data['GRvalue']


#
grv_c1a2_data = pd.read_csv(os.path.join(dir_exp,'GRvalues_center1_scientistA_2019.csv'),sep=',')
grv_c1a2 = pd.DataFrame()
grv_c1a2['cell_line'] = grv_c1a2_data['cell_line']
grv_c1a2['agent'] = grv_c1a2_data['agent']
grv_c1a2['timepoint'] = grv_c1a2_data['timepoint']
grv_c1a2['cell_count'] = grv_c1a2_data['cell_count']
grv_c1a2['cell_count__ctrl'] = grv_c1a2_data['cell_count__ctrl']
grv_c1a2['cell_count__time0'] = grv_c1a2_data['cell_count__time0']
grv_c1a2['GRvalue'] = grv_c1a2_data['GRvalue']

#
#%%

def read_exp_data(file_name):
    dir_exp = os.path.join(wd,'output','in_silico_drs_summary','mcf10a_drs_exp')
    exp_data = pd.read_csv(os.path.join(dir_exp,file_name),sep=',')
    grv_df = pd.DataFrame()
    grv_df['cell_line'] = exp_data['cell_line']
    
    drugs = exp_data['agent'].values
    
    for d in range(len(drugs)):
        if '/' in drugs[d]:
            drug = str(drugs[d]).split('/')[0]
            drugs[d] = drug
    
    # grv_df['agent'] = exp_data['agent']
    grv_df['agent'] = drugs
    grv_df['concentration'] = exp_data['concentration']
    try:
        grv_df['timepoint'] = exp_data['timepoint']
    except:
        grv_df['timepoint'] = np.ones(len(exp_data['cell_line'].values))*np.nan
    grv_df['cell_count'] = exp_data['cell_count']
    grv_df['cell_count__ctrl'] = exp_data['cell_count__ctrl']
    grv_df['cell_count__time0'] = exp_data['cell_count__time0']
    grv_df['GRvalue'] = exp_data['GRvalue']
    
    return grv_df

#%%
grv_c1a1 = read_exp_data('GRvalues_center1_scientistA_2017.csv')
grv_c1a2 = read_exp_data('GRvalues_center1_scientistA_2019.csv')
grv_c1b = read_exp_data('GRvalues_center1_scientistB.csv')
grv_c1c = read_exp_data('GRvalues_center1_scientistC.csv')
grv_c2 = read_exp_data('GRvalues_center2.csv')
grv_c3 = read_exp_data('GRvalues_center3.csv')
grv_c4 = read_exp_data('GRvalues_center4.csv')
grv_c5 = read_exp_data('GRvalues_center5.csv')

#%% plot exp data
drugs_exp = ['Alpelisib','Neratinib','Trametinib','Palbociclib']
grv_df = grv_c1a1
drug = drugs_exp[3]

grv_drug = grv_df[grv_df['agent']==drug]

doses_drug = np.unique(grv_drug['concentration'].values)

# dose_lvl_count = [sum(grv_drug['concentration'].values==d) for d in dose_lvls]
x_values = doses_drug

y_values_all = [grv_drug[grv_drug['concentration']==xval]['GRvalue'].values for xval in x_values]

y_values_median = [np.median(ys) for ys in y_values_all]

y_min = [np.min(ys) for ys in y_values_all]

y_max = [np.max(ys) for ys in y_values_all]

y_err_min = [y_values_median[dl] - y_min[dl] for dl in range(len(y_values_median))]

y_err_max = [y_max[dl] - y_values_median[dl] for dl in range(len(y_values_median))]

yerror = [y_err_min,y_err_max]

plt.errorbar(x_values,y_values_median,yerr=yerror,fmt='o-',capsize=5)
plt.xscale('log')
# plt.ylim(min(y_min)*.5,max(y_max)*1.25)
plt.ylim(0,max(y_max)*1.25)
plt.title(str(drug))
plt.ylabel('GR value')
plt.xlabel('Concentration (uM)')
plt.show()

#%% combine and map exp doses to sim

drugs_exp = ['Alpelisib','Neratinib','Trametinib','Palbociclib']
grv_exp = {'grv_c1a1':grv_c1a1,'grv_c1a2':grv_c1a2,'grv_c1b':grv_c1b,'grv_c1c':grv_c1c,'grv_c2':grv_c2,'grv_c3':grv_c3,'grv_c4':grv_c4,'grv_c5':grv_c5}


grv_exp_df = pd.DataFrame()

for key in grv_exp.keys():
    grv_df = grv_exp[key]
    grv_df['source'] = np.ones(np.shape(grv_df)[0])*np.nan
    grv_df['source'] = key
    grv_exp_df = grv_exp_df.append(grv_df, ignore_index=True)
    

grv_exp_compare = pd.DataFrame()

# grv_c2[math.isclose(grv_c2['concentration'],doses_all[3],abs_tol=1e-4)]

for dose_sim in doses_all[1:]:
    for row_n in range(np.shape(grv_exp_df)[0]):
        grv_exp_row = grv_exp_df.iloc[row_n,:].copy()
        if grv_exp_row['agent'] in drugs_exp:
            if math.isclose(float(grv_exp_row['concentration']),dose_sim,abs_tol=1e-4):
                grv_exp_row['dose_sim'] = dose_sim
                grv_exp_compare = grv_exp_compare.append(grv_exp_row,ignore_index=True)

#%% gr compare

drug_compare = drugs_exp[3]

drug_sim = drug_compare.lower()[:5]

grv_exp_drug = grv_exp_compare[grv_exp_compare['agent']==drug_compare]

x_values = doses_all[1:]

y_values_all_exp = [grv_exp_drug[grv_exp_drug['dose_sim']==xval]['GRvalue'].values for xval in x_values]

y_values_median_exp = [np.median(ys) for ys in y_values_all_exp]

if sum(np.isnan(y_values_median_exp))>0:
    
    nan_idx = np.where(np.isnan(y_values_median_exp))[0][0]
    
    x_values_actual = x_values[:nan_idx]
    x_values = x_values_actual
    
    y_values_all_exp = [grv_exp_drug[grv_exp_drug['dose_sim']==xval]['GRvalue'].values for xval in x_values]

    y_values_median_exp = [np.median(ys) for ys in y_values_all_exp]
    
    


y_min_exp = [np.min(ys) for ys in y_values_all_exp]

y_max_exp = [np.max(ys) for ys in y_values_all_exp]

y_err_min_exp = [y_values_median_exp[dl] - y_min_exp[dl] for dl in range(len(y_values_median_exp))]

y_err_max_exp = [y_max_exp[dl] - y_values_median_exp[dl] for dl in range(len(y_values_median_exp))]

yerror_exp = [y_err_min_exp,y_err_max_exp]


#%

tp = 72

drs_filtered = drs_all_gr[drs_all_gr['agent']==drug_sim]
drs_filtered = drs_filtered[drs_filtered['timepoint']==tp]

y_values_all_sim = [drs_filtered[drs_filtered['concentration']==xval]['GRvalue'].values for xval in x_values]

y_values_median_sim = [np.median(ys) for ys in y_values_all_sim]

y_min_sim = [np.min(ys) for ys in y_values_all_sim]

y_max_sim = [np.max(ys) for ys in y_values_all_sim]

y_err_min_sim = [y_values_median_sim[dl] - y_min_sim[dl] for dl in range(len(y_values_median_sim))]

y_err_max_sim = [y_max_sim[dl] - y_values_median_sim[dl] for dl in range(len(y_values_median_sim))]

yerror_sim = [y_err_min_sim,y_err_max_sim]



#%

plt.errorbar(x_values,y_values_median_exp,yerr=yerror_exp,fmt='o-',capsize=5,label='Experiment')
plt.errorbar(x_values,y_values_median_sim,yerr=yerror_sim,fmt='o-',capsize=5,label='Simulation')

plt.xscale('log')
# plt.ylim(min(y_min)*.5,max(y_max)*1.25)
plt.ylim(-0.5,1.3)
plt.title(str(drug_compare),font='Arial')
plt.ylabel('GR value',font='Arial')
plt.xlabel('Concentration (uM)',font='Arial')
plt.legend(loc='lower left')
plt.show()



#%%




#%% drs2 test

nerat1_0 = drs_dict(output_drs2,'nerat',1,0)

nerat1_9 = drs_dict(output_drs2,'nerat',1,9)

#%% drs2 plot

pd1, tp1, td1 = nerat1_0.pop_dyn()
pd9, tp9, td9 = nerat1_9.pop_dyn()

plt.plot(tp1/3600,pd1)
plt.plot(tp9/3600,pd9)

#%%
rep = 9
drug = 'nerat'

for dl in range(10):
    drs_dict0 = drs_dict(output_drs2,drug,rep,dl)
    pd,tp,td = drs_dict0.pop_dyn()
    plt.plot(tp/3600,pd,label=str(doses_all[dl]))
    
plt.ylim(0,200)
plt.xlim(0,72)
plt.xlabel('Time(h)')
plt.ylabel('Cell #')
plt.legend(bbox_to_anchor=(1.05,1.0))
plt.show()

#%% summarize drs2
drs2_all = {}

#%%

drug = 'trame'

#%%

drs_drug = {}

for d in range(10):
    
    drs_dose = drs_summarize(drug, d,output_drs2)
    drs_drug['d'+str(d)] = drs_dose
    
drs2_all[drug] = drs_drug

#%%

pickle.dump(drs2_all, open(os.path.join(wd,'output','in_silico_drs2_summary','drs_summary.pkl'),'wb'))

#%% gr-calc/drs2/nerat

drs_summary= drs2_all


#%%



time_h = [48,72]
drs_summary_full = drs_summary

drs2_grcalc3 = pd.DataFrame(data=None,columns=['cell_line','agent','timepoint','concentration','cell_count','cell_count__ctrl','cell_count__time0'])



for drug in drs_summary_full.keys():
    for dl in range(1,len(drs_summary_full[str(drug)].keys())):
        for rep in range(len(drs_summary_full[str(drug)]['d'+str(dl)].keys())):
            for t in time_h:
                new_row = gr_calc_row3(drug,t,dl,rep,drs_summary_full)
                drs2_grcalc3 = drs2_grcalc3.append(new_row, ignore_index=True)


drs2_grcalc3.to_csv(os.path.join(wd,'output','in_silico_drs2_summary','drs2_grcalc3.tsv'),sep='\t',index=False)

#%% drs2/nerat/gr-plot

drs2_nerat_gr = pd.read_csv(os.path.join(wd,'output','in_silico_drs2_summary','drs2_grcalc3_nerat_grc.tsv'),sep='\t')

drug = 'nerat'
tp = 72


x_values = doses_all[1:]

drs_filtered = drs2_nerat_gr[drs2_nerat_gr['agent']==drug]
drs_filtered = drs_filtered[drs_filtered['timepoint']==tp]

y_values_all = [drs_filtered[drs_filtered['concentration']==xval]['GRvalue'].values for xval in x_values]

y_values_median = [np.median(ys) for ys in y_values_all]

y_min = [np.min(ys) for ys in y_values_all]

y_max = [np.max(ys) for ys in y_values_all]

y_err_min = [y_values_median[dl] - y_min[dl] for dl in range(len(y_values_median))]

y_err_max = [y_max[dl] - y_values_median[dl] for dl in range(len(y_values_median))]

yerror = [y_err_min,y_err_max]

plt.errorbar(x_values,y_values_median,yerr=yerror,fmt='o-',capsize=5)
plt.xscale('log')
# plt.ylim(min(y_min)*.5,max(y_max)*1.25)
plt.ylim(min(y_min)*1.1,max(y_max)*1.25)
plt.title(str(drug))
plt.ylabel('GR value')
plt.xlabel('Concentration (uM)')
plt.show()

#%% drs2 gr plot vs exp

drugs_exp = ['Alpelisib','Neratinib','Trametinib','Palbociclib']
grv_exp = {'grv_c1a1':grv_c1a1,'grv_c1a2':grv_c1a2,'grv_c1b':grv_c1b,'grv_c1c':grv_c1c,'grv_c2':grv_c2,'grv_c3':grv_c3,'grv_c4':grv_c4,'grv_c5':grv_c5}


grv_exp_df = pd.DataFrame()

for key in grv_exp.keys():
    grv_df = grv_exp[key]
    grv_df['source'] = np.ones(np.shape(grv_df)[0])*np.nan
    grv_df['source'] = key
    grv_exp_df = grv_exp_df.append(grv_df, ignore_index=True)
    

grv_exp_compare = pd.DataFrame()

# grv_c2[math.isclose(grv_c2['concentration'],doses_all[3],abs_tol=1e-4)]

for dose_sim in doses_all[1:]:
    for row_n in range(np.shape(grv_exp_df)[0]):
        grv_exp_row = grv_exp_df.iloc[row_n,:].copy()
        if grv_exp_row['agent'] in drugs_exp:
            if math.isclose(float(grv_exp_row['concentration']),dose_sim,abs_tol=1e-4):
                grv_exp_row['dose_sim'] = dose_sim
                grv_exp_compare = grv_exp_compare.append(grv_exp_row,ignore_index=True)


#%% gr compare/drs2
drs_all_gr = pd.read_csv(os.path.join(wd,'output','in_silico_drs2_summary','drs2_grcalc3_grc.tsv'),sep='\t')

plt.rcParams["lines.linewidth"] = 2

drug_compare = drugs_exp[3]

drug_sim = drug_compare.lower()[:5]

grv_exp_drug = grv_exp_compare[grv_exp_compare['agent']==drug_compare]

x_values = doses_all[1:]

y_values_all_exp = [grv_exp_drug[grv_exp_drug['dose_sim']==xval]['GRvalue'].values for xval in x_values]

y_values_median_exp = [np.median(ys) for ys in y_values_all_exp]

if sum(np.isnan(y_values_median_exp))>0:
    
    nan_idx = np.where(np.isnan(y_values_median_exp))[0][0]
    
    x_values_actual = x_values[:nan_idx]
    x_values = x_values_actual
    
    y_values_all_exp = [grv_exp_drug[grv_exp_drug['dose_sim']==xval]['GRvalue'].values for xval in x_values]

    y_values_median_exp = [np.median(ys) for ys in y_values_all_exp]
    
    


y_min_exp = [np.min(ys) for ys in y_values_all_exp]

y_max_exp = [np.max(ys) for ys in y_values_all_exp]

y_err_min_exp = [y_values_median_exp[dl] - y_min_exp[dl] for dl in range(len(y_values_median_exp))]

y_err_max_exp = [y_max_exp[dl] - y_values_median_exp[dl] for dl in range(len(y_values_median_exp))]

yerror_exp = [y_err_min_exp,y_err_max_exp]


#%

tp = 72

drs_filtered = drs_all_gr[drs_all_gr['agent']==drug_sim]
drs_filtered = drs_filtered[drs_filtered['timepoint']==tp]

y_values_all_sim = [drs_filtered[drs_filtered['concentration']==xval]['GRvalue'].values for xval in x_values]

y_values_median_sim = [np.median(ys) for ys in y_values_all_sim]

y_min_sim = [np.min(ys) for ys in y_values_all_sim]

y_max_sim = [np.max(ys) for ys in y_values_all_sim]

y_err_min_sim = [y_values_median_sim[dl] - y_min_sim[dl] for dl in range(len(y_values_median_sim))]

y_err_max_sim = [y_max_sim[dl] - y_values_median_sim[dl] for dl in range(len(y_values_median_sim))]

yerror_sim = [y_err_min_sim,y_err_max_sim]

y_min = min(min(y_min_exp),min(y_min_sim))
y_max = max(max(y_max_exp),max(y_max_sim))

#%

plt.errorbar(x_values,y_values_median_exp,yerr=yerror_exp,fmt='o-',capsize=5,label='Experiment')
plt.errorbar(x_values,y_values_median_sim,yerr=yerror_sim,fmt='o-',capsize=5,label='Simulation')

plt.xscale('log')
plt.ylim(y_min*1.25,y_max*1.25)
# plt.ylim(-1,1.8)
plt.title(str(drug_compare),font='Arial')
plt.ylabel('GR value',font='Arial')
plt.xlabel('Concentration (uM)',font='Arial')
plt.legend(loc='lower left')
plt.show()

#%% drs2/rep-median

drs_all = drs2_all


drs_median = {}

# drugs = list(drs_all.keys())

drugs = ['nerat']

for dr in drugs:
    
    drs_median_drug = {}
    
    for dl in range(10):
        
        drs_median_dose = {}
        
        tp_drs = [drs_all[dr]['d'+str(dl)]['r'+str(rep+1)]['tout'] for rep in range(10)]
        popdyn_reps0 = [drs_all[dr]['d'+str(dl)]['r'+str(rep+1)]['cellpop'] for rep in range(10)]
        tp_all = np.array(list(itertools.chain(*tp_drs)))
        tp_all = np.unique(tp_all)
        tp_max = min([tp_drs[x][-1] for x in range(len(tp_drs))])
        tp_max_idx = np.where(tp_all == tp_max)[0][0]
        tp_all = tp_all[:tp_max_idx+1]
        popdyn_reps = []
        for rep in range(10):
            interpolator = interp1d(tp_drs[rep],popdyn_reps0[rep])
            y_new = interpolator(tp_all)
            popdyn_reps.append(y_new)
            
        popdyn_med = np.median(popdyn_reps,axis=0)
        
        drs_median_dose['cellpop'] = popdyn_med
        drs_median_dose['tout'] = tp_all
        
        drs_median_drug['d'+str(dl)] = drs_median_dose
        
    drs_median[dr] = drs_median_drug


#%%

drug = 'nerat'

for dl in range(10):
    data = drs_median[drug]['d'+str(dl)]
    xvals = data['tout']
    yvals = data['cellpop']
    plt.plot(xvals/3600,yvals,label=str(doses_all[dl]))
    
plt.xlim(0,72)
plt.ylim(0,200)
plt.legend(bbox_to_anchor=(1.05,1.0))
plt.show()






#%%
lapat1_0 = drs_dict(output_main,'lapat',1,0)
lapat1_1 = drs_dict(output_main,'lapat',1,1)
lapat2_3 = drs_dict(output_main,'lapat',2,3)
lapat3_5 = drs_dict(output_main,'lapat',3,5)

palbo1_5 = drs_dict(output_main,'palbo',1,5)
#%% rep average population dynamics

lapat1_4 = drs_dict(output_main,'lapat',1,4)
lapat2_4 = drs_dict(output_main,'lapat',2,4)
lapat3_4 = drs_dict(output_main,'lapat',3,4)

trame1_0 = drs_dict(output_main,'trame',1,0)
trame1_1 = drs_dict(output_main,'trame',1,1)
trame1_5 = drs_dict(output_main,'trame',1,5)
trame1_9 = drs_dict(output_main,'trame',1,9)

#%%


#%% multi-rep/average

lapat1_4 = drs_dict(output_main,'lapat',1,4)
lapat2_4 = drs_dict(output_main,'lapat',2,4)
lapat3_4 = drs_dict(output_main,'lapat',3,4)
lapat4_4 = drs_dict(output_main,'lapat',4,4)
lapat5_4 = drs_dict(output_main,'lapat',5,4)

#%% investigate nerat

nerat1_0 = drs_dict(output_main,'nerat',1,0)
nerat1_5 = drs_dict(output_main,'nerat',1,5)
nerat1_9 = drs_dict(output_main,'nerat',1,9)

#%% drs2

drs2_nerat1_0 = drs_dict(output_drs2,'nerat',1,0)
drs2_nerat1_5 = drs_dict(output_drs2,'nerat',1,5)
drs2_nerat1_8 = drs_dict(output_drs2,'nerat',1,8)



  
#%% control spread

popdyn_drs = []
tp_drs = []

drugs_all = ['alpel','lapat','nerat','palbo','trame']

for drug in drugs_all:
    for rep in range(5):
        dict0 = drs_dict(output_main,drug,rep+1,0)
        a,b,c = dict0.pop_dyn()
        popdyn_drs.append(a)
        tp_drs.append(b)


#%%

tp_drs_all = [item for sublist in tp_drs for item in sublist]

tp_drs_all = np.unique(tp_drs_all)

tp_max = min([max(tp) for tp in tp_drs])

tp_drs_all = tp_drs_all[tp_drs_all<=tp_max]

popdyn_drs_uniform = []

for d in range(len(tp_drs)):
    
    popdyn_intp = interp1d(tp_drs[d],popdyn_drs[d])
    
    popdyn_new = popdyn_intp(tp_drs_all)
    
    popdyn_drs_uniform.append(popdyn_new)
    

popdyn_drs_uniform = np.array(popdyn_drs_uniform)

popdyn_median = [np.median(popdyn_drs_uniform[:,tp]) for tp in range(np.shape(popdyn_drs_uniform)[1])]
popdyn_std = [np.std(popdyn_drs_uniform[:,tp]) for tp in range(np.shape(popdyn_drs_uniform)[1])]

popdyn_median_intp = interp1d(popdyn_median,tp_drs_all)


for p in range(len(popdyn_drs_uniform)):
    
    plt.plot(tp_drs_all/3600,popdyn_drs_uniform[p,:],linewidth=0.5,color='grey')

plt.plot(tp_drs_all/3600,popdyn_median,linewidth=2.0,color='red',label='Median')
plt.axhline(y=200,xmin=0,xmax=48.47/73,linestyle='--')
plt.axvline(x=48.47,ymin=0,ymax=200/500,linestyle='--')

plt.xlabel('Time (hours)',fontsize=15)
plt.ylabel('Number of cells',fontsize=15)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlim(0,73)
plt.ylim(0,500)
plt.legend(fontsize=15)
plt.show()








#%%

for d in range(len(cellpop_sim)):
    plt.plot(timepoints_sim[d]/3600,cellpop_sim[d],label=str(doses_all[d]))


plt.ylim(0,550)
plt.xlim(0,72)
plt.xlabel('Time (h)')
plt.ylabel('Cell population')
plt.legend(bbox_to_anchor=(1.05,1.0))
plt.show()

#%%

dir1 = os.path.join(output_dir_sim,drug+'_'+str(doses_all[4]))

output1 = load_outputs(dir1)

timecourse_lin(3,drug)



#%% obs parsing






#%% Figure - stochastic parameter perturbation

#k1813

# k1813_vals = [0.004,0.0004,0.0003,0.0002]
# fracs_div = [0.125,0.01525,0.0078125,0]

k1813_vals = [0.0004,0.004,0.0003,0.0002]
fracs_div = [0.01525,0.125,0.0078125,0]

plt.scatter(k1813_vals[0],fracs_div[0],c='red',marker='D',s=50,label='Default')
plt.scatter(k1813_vals[1:],fracs_div[1:],c='blue')

plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.xlabel('Parameter value (basal RasGTP formation)',fontsize=15)
plt.ylabel('Probability of cell division without EGF',fontsize=15)
plt.xscale('log')
plt.xlim(1e-4,1e-2)
plt.legend(bbox_to_anchor=(0.9,0.2))
plt.show()

#%%

#mek activation

multiplier_vals = [1,2,3,5]
frac_div_egf = [0.2734,0.5781,0.65625,0.84375]
frac_div_noegf = [0.0,0.0234,0.039,0.03125]

plt.scatter(multiplier_vals,frac_div_egf,c='red',marker='D',s=50,label='+EGF')
plt.scatter(multiplier_vals,frac_div_noegf,c='blue',label='-EGF')
plt.legend()
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
# plt.yscale('log')
plt.xlabel('Rate multiplier',fontsize=15)
plt.ylabel('Probability of cell division',fontsize=15)
plt.show()







#%%