# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 16:20:35 2021

@author: nvdve
"""

import numpy as np;
import matplotlib.pyplot as plt;
from SALib.analyze import sobol;
from SALib.sample import saltelli;
from math import isclose;
import pandas as pd;
import openturns as ot;
from collections import OrderedDict
from sklearn import svm
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
from numpy import array;
import numpy as np;
import scipy.stats as sc;
import seaborn as sns;
from sklearn.model_selection import GridSearchCV
import openturns as ot;

import warnings
warnings.filterwarnings("ignore")

sns.set_theme(style="whitegrid")


problem2 = {
    'num_vars': 3,
    'names': ['Dimensionless Loading', 'Offshore Wave Steepness', 'Dimensionless Leakage Length'],
    'bounds': [[2.0, 8.0], [0.01, 0.05], [0.5, 2.5]],
    'dists': ['unif', 'unif', 'unif']
}
problem3 = {
    'num_vars': 6,
    'names': ['Dimensionless Loading', 'Offshore Wave Steepness', 'Dimensionless Leakage Length', 'Uncertainty Location', 'Uncertainty Width', 'Dimensionless Amplitude'],
    'bounds': [[2.0, 8.0], [0.01, 0.05], [0.5, 2.5], [0.05, 0.95], [0.05, 0.95], [0.05, 0.95]],
    'dists': ['unif', 'unif', 'unif', 'unif', 'unif', 'unif']
}
problem4 = {
    'num_vars': 4,
    'names': ['Dimensionless Loading', 'Offshore Wave Steepness', 'Dimensionless Leakage Length', 'Friction Coefficient'],
    'bounds': [[2.0, 8.0], [0.01, 0.05], [0.5, 2.5], [0.60, 0.85]],
    'dists': ['unif', 'unif', 'unif', 'unif']
}
problem5 = {
    'num_vars': 5,
    'names': ['Dimensionless Loading', 'Offshore Wave Steepness', 'Dimensionless Leakage Length', 'zgat', 'xgat'],
    'bounds': [[2.0, 8.0], [0.01, 0.05], [0.5, 2.5], [2.5, 5.0], [-1.3, 1.3]],
    'dists': ['unif', 'unif', 'unif', 'unif', 'unif']
}

folders = ['Group1_NoDamage', 'Group2_Deformation', 'Group3_ReducedClamping', 'Group4_MissingElement']
qq = ['No Damage', 'Deformation', 'Reduced Clamping', 'Missing Element']
colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']

inn2 = []
inn3 = []
inn4 = []
inn5 = []
out2 = []
out3 = []
out4 = []
out5 = []

for serie in [2,3,4,5]:
    # Which problem
    n = 16
    problem = problem2
    if(serie == 3):
        problem = problem3
    elif(serie == 4):
        problem = problem4
    elif(serie == 5):
        problem = problem5
    s = serie - 2;
    
    samp = pd.read_excel(io=str(folders[s]) + "/sample.xlsx", index_col=0);
    
    para = [];
    param_values = saltelli.sample(problem, n, calc_second_order=True)
    
    
    # Make sure each sampel is only taken into account once
    if(serie == 2):
        for i in param_values:
            add = True;
            for j in para:
                if(i[0] == j[0] and i[1] == j[1] and i[2] == j[2]):
                    add = False;
            if(add == True):
                para.append(i)
    elif(serie == 3):
        for i in param_values:
            add = True;
            for j in para:
                if(i[0] == j[0] and i[1] == j[1] and i[2] == j[2] and i[3] == j[3] and i[4] == j[4] and i[5] == j[5]):
                    add = False;
            if(add == True):
                para.append(i)
    elif(serie == 4):
        for i in param_values:
            add = True;
            for j in para:
                if(i[0] == j[0] and i[1] == j[1] and i[2] == j[2] and i[3] == j[3]):
                    add = False;
            if(add == True):
                para.append(i)
    elif(serie == 5):
        for i in param_values:
            add = True;
            for j in para:
                if(i[0] == j[0] and i[1] == j[1] and i[2] == j[2] and i[3] == j[3] and i[4] == j[4]):
                    add = False;
            if(add == True):
                para.append(i)
    
    
    
    X = np.zeros((len(para), 9))
    Y = np.zeros((len(para), 6))
    
    for i in range(len(para)):
        prow = para[i]
        found = 0;
        usemodel = -1;
        for model, data in samp.iterrows():
            HsDD = data['Hs'] / ((data['ρs'] / data['ρw'] - 1) * data['D'])
            s0p = data['S0p']
            iri = (1/3)/np.sqrt(data['S0p'])
            DLL = data['Λ'] / data['D']
            ue = data['μe']
            smid = ot.Normal(0.358, 0.157).computeCDF(data['Smid coef'])
            sb = ot.Normal(12.43, 2.65).computeCDF(data['Sb coef'])
            sa = data['S amp']
            gz = data['Gz']
            gx = data['Gx']
            
            if(serie == 2):
                if(isclose(prow[0], HsDD, abs_tol=1e-4) and isclose(prow[1], s0p, abs_tol=1e-4) and isclose(prow[2], DLL, abs_tol=1e-4)):
                    found = found + 1;
                    usemodel = model;
            elif(serie == 3):
                if(isclose(prow[0], HsDD, abs_tol=1e-4) and isclose(prow[1], s0p, abs_tol=1e-4) and isclose(prow[2], DLL, abs_tol=1e-4) and isclose(prow[3], smid, abs_tol=1e-4) and isclose(prow[4], sb, abs_tol=1e-4) and isclose(prow[5], sa, abs_tol=1e-4)):
                    found = found + 1;
                    usemodel = model;
            elif(serie == 4):
                if(isclose(prow[0], HsDD, abs_tol=1e-4) and isclose(prow[1], s0p, abs_tol=1e-4) and isclose(prow[2], DLL, abs_tol=1e-4) and isclose(prow[3], ue, abs_tol=1e-4)):
                    found = found + 1;
                    usemodel = model;
            elif(serie == 5):
                if(isclose(prow[0], HsDD, abs_tol=1e-4) and isclose(prow[1], s0p, abs_tol=1e-4) and isclose(prow[2], DLL, abs_tol=1e-4) and isclose(prow[3], gz, abs_tol=1e-4) and isclose(prow[4], gx, abs_tol=1e-4)):
                    found = found + 1;
                    usemodel = model;
            if(found == 1):
                data = np.loadtxt(str(folders[s]) +  "/Job-" + usemodel + ".txt", delimiter=";")
                data = data.transpose()
                elm = np.sum(data[3]) / (3 * 1.09)
                maxdefm = np.sum(data[4]) / (3 * 1.09)
                enddefm = np.sum(data[5]) / (3 * 1.09)
                maxelement = np.max(data[4])
                maxdefc = maxdefm - (elm * 0.3) / (3 * 1.09)
                enddefc = enddefm - (elm * 0.3) / (3 * 1.09)
                if(enddefm > 4 and serie == 3):
                    enddefm = 1.0
                    maxdefm = 1
                if(enddefm > 1.5 and serie == 3):
                    #print(model, serie)
                    enddefm = 1.5
                X[i,:] = [HsDD, iri, DLL, ue, smid, sb, sa, gz, gx]
                Y[i,:] = [elm, maxdefm, enddefm, maxelement, maxdefc, enddefc]
                break;
        if(found == 0):
            print("No model found", model, serie)
    
    if(serie == 2):
        out2 = Y;
        inn2 = X;
    elif(serie == 3):
        out3 = Y;
        inn3 = X;
    elif(serie == 4):
        out4 = Y;
        inn4 = X;
    elif(serie == 5):
        out5 = Y;
        inn5 = X;
        

mod2 = linear_model.LinearRegression()
mod3 = linear_model.LinearRegression()
mod4 = linear_model.LinearRegression()
mod5 = linear_model.LinearRegression()


dam = 2
draw3D = True;
ress = [];
xaxis = np.linspace(0, 2, 101)


#fig = plt.figure()
for serie in [2,3,4,5]:
    from sklearn.svm import SVR
    
    if(serie == 2):
        p1 = inn2[:, 0]
        p2 = inn2[:, 1]
        p3 = inn2[:, 2]
        vector = out2[:, dam]
        X = np.c_[p1, p2, p3]
    elif(serie == 3):
        p1 = inn3[:, 0]
        p2 = inn3[:, 1]
        p3 = inn3[:, 2]
        p4 = inn3[:, 4]
        p5 = inn3[:, 5]
        p6 = inn3[:, 6]
        vector = out3[:, dam]
        X = np.c_[p1, p2, p3, p6]
    elif(serie == 4):
        p1 = inn4[:, 0]
        p2 = inn4[:, 1]
        p3 = inn4[:, 2]
        p4 = inn4[:, 3]
        vector = out4[:, dam]
        X = np.c_[p1, p2, p3, p4]
    elif(serie == 5):
        p1 = inn5[:, 0]
        p2 = inn5[:, 1]
        p3 = inn5[:, 2]
        p4 = inn5[:, 7]
        p5 = inn5[:, 8]
        vector = out5[:, dam]
        X = np.c_[p1, p2, p3, p4]

    clf = svm.SVR(C=2.5, kernel='poly', degree=2, tol=10e-5, epsilon=0.01)
    fitter = clf.fit(X, vector)
    
    if(serie == 2):
        mod2 = fitter;
    elif(serie == 3):
        mod3 = fitter;
    elif(serie == 4):
        mod4 = fitter;
    elif(serie == 5):
        mod5 = fitter;
    
    if(draw3D == True):
        sx = []
        sy = []
        
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.scatter(p1, p3, vector, c='r', s=50)
        plt.xlabel(r'$H_{s}/\Delta D$ [-]')
        plt.ylabel(r'$\Lambda/D$ [-]')
        ax.set_zlim(0,1.5)
        ax.set_zlabel('Final Deformation [m/m]')
        ax.view_init(30, 45+270-22.5)
        
        for _x in np.linspace(2, 8, 20):
            for _y in np.linspace(0.5, 2.5, 20):
                sx.append(_x);
                sy.append(_y);
        if(serie == 2):
            predict = np.array([sx, np.ones(len(sx)) * (5/3), sy]).transpose()
        elif(serie == 3):
            predict = np.array([sx, np.ones(len(sx)) * (5/3), sy, np.ones(len(sx)) * 0.5]).transpose()
        elif(serie == 4):
            predict = np.array([sx, np.ones(len(sx)) * (5/3), sy, np.ones(len(sx)) * 0.725]).transpose()
        elif(serie == 5):
            predict = np.array([sx, np.ones(len(sx)) * (5/3), sy, np.ones(len(sx)) * 3.75]).transpose()
        sz = fitter.predict(predict)
        sz[sz < 0] = 0;
        ax.plot_trisurf(np.array(sx), np.array(sy), np.array(sz), linewidth=0, antialiased=False, alpha=0.5)
        plt.title("Group " + str(serie-1) + " (" + qq[serie-2] + ")")
        plt.savefig('ch6_pf_3dplot' + str(serie) + '.png', dpi=200, bbox_inches='tight')
        plt.show()
        
# No Damage
# mod2.predict([HsDD, iribarren, lambda/D])

# S-profile
# mod3.predict([HsDD, iribarren, lambda/D, amplitude/filter])

# Reduced clamping
# mod4.predict([HsDD, iribarren, lambda/D, mu_e])

# Missing element
# mod5.predict([HsDD, iribarren, lambda/D, z])