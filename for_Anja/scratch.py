import numpy
import math

data = [1721.454438703735, 1801.1008305014761, 1916.6162908425467, 2063.0323760623987, 2236.54944535438, 2400.1241323784852, 2545.928308762618, 2668.375871408156, 2768.887309313186, 2853.728323918648, 2932.816356006221, 3007.1911908111815, 3075.2183457509163, 3135.4958132225597, 3194.4924650658663, 3244.5387997098055, 3290.6313040430787, 3329.607289936189, 3359.2859278806523, 3381.836916756462, 3385.9808595283234, 3365.0360187454817, 3306.9422358403003, 3217.723250656997, 3100.49641219742, 2990.8803975468472, 2903.8745056307635, 2839.740037154466, 2794.745844605816, 2766.083723758363, 2743.3108788658587, 2728.1172742930316, 2721.032656817785, 2722.493581479963, 2726.3286307566127, 2740.17321101927, 2764.691079349912, 2805.5595469125665, 2872.903297355204, 2955.012426542958]

print data

def smoothed(list,degree=5):  
    window=degree*2-1  
    weight=numpy.array([1.0]*window)  
    weightGauss=[]  
    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss=1/(numpy.exp((4*(frac))**2))  
        weightGauss.append(gauss)  
    weight=numpy.array(weightGauss)*weight  
    smoothed=[0.0]*(len(list)-window)  
    for i in range(len(smoothed)):  
        smoothed[i]=sum(numpy.array(list[i:i+window])*weight)/sum(weight)  
    return smoothed  

def smoothed2(list,degree=5):  
    window=degree*2-1  
    weight=[1.0]*window  
    weightGauss=[]  
    for i in range(window):  
        i=i-degree+1  
        frac=i/float(window)  
        gauss=1/(math.exp((4*(frac))**2))  
        weightGauss.append(gauss)  
    print range(window)
    weight= [weightGauss[i]*weight[i] for i in range(window)]
    smoothed=[0.0]*(len(list)-window)  
    for i in range(len(smoothed)):  
        smoothed[i]=sum((list[i:i+window])*weight)/sum(weight)  
    return smoothed  

print smoothed(data)
print smoothed2(data)