# -*- coding: utf-8 -*-
"""
Created on Sun Jul 29 18:19:38 2018

@author: P. Balamurugan
"""

#This code is suitable for multi-processing
#the following code is for xgboost regression with k-fold cv for 100 different seed values and reports the average rmse along with standard deviation
#This code works on pure+synthetic data. User needs to provide both the pure data file and the file containing pure data+synthetic data 
#(Note: Pure data must always be found in the beginning of the file) 

import numpy as np
from sklearn.preprocessing import normalize#normalize is not used in the code, but can be tried
from sklearn.utils import shuffle 
import math 
from sklearn.ensemble import GradientBoostingRegressor
from numpy import inf
import pandas as pd
import csv
import itertools
import concurrent.futures
import time

global num_features
global crossvalidate_k 

global train_pure_synthetic_index_list 
global test_sample_index_list 

global seeds
global splitpoints

global seed_numest_pair_arr

global seed_start
global seed_step
global final_seed
global best_est 

global test_rmses
global train_rmses
global C_values

test_sample_index_list = []
train_pure_synthetic_index_list = []
splitpoints = []

crossvalidate_k = 7 #number of folds for cross-validation
mydata=pd.read_csv('ExpDataMatrix.csv') #add pure datafile name here
mydata=mydata.to_numpy()
#mydata = np.genfromtxt('regression_pure_data.csv', delimiter=',')
num_features = len(mydata[0])-1

features = mydata[:,0:num_features]
output = mydata[:,num_features:]

norm_features = features 

mydata_withsynthetic=pd.read_csv('realPlusSynthBL2.csv') #add (pure plus synthetic) datafile name here
mydata_withsynthetic=mydata_withsynthetic.to_numpy()
#mydata_withsynthetic = np.genfromtxt('regression_pure_synthetic_data.csv', delimiter=',')

pure_synthetic_features = mydata_withsynthetic[:,0:num_features]
pure_synthetic_output = mydata_withsynthetic[:,num_features:]

    


#print(norm_features)
#print(mydata)

num_samples = len(mydata)
#print(num_samples)

num_pure_synthetic_samples = len(mydata_withsynthetic)

seed_start = 0.0
seed_end = 10000.0 #please change it to 10000
seed_step = 100.0



seeds = np.arange(seed_start,seed_end,seed_step) 
final_seed = (seeds[len(seeds)-1])

test_rmses = np.zeros(len(seeds)) 
train_rmses = np.zeros(len(seeds))

best_est = 0*np.arange(0,len(seeds),1)

best_C_values = 1.0*np.arange(0,len(seeds),1)

best_alpha_values = 1.0*np.arange(0,len(seeds),1)
C_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] #, 0.5, 0.7] #[0.00001, 0.0001, 0.001, 0.01, 0.1, 1] 

alpha_values = [1E-5, 1E-4, 1E-3, 0.01, 0.1, 0.5, 0.9]


seed_numest_pair = []

for seed in seeds:
    for C_val in C_values:
        for alpha_val in alpha_values:
            seed_numest_pair.append([seed,C_val,alpha_val])

#print(seed_numest_pair)
seed_numest_pair_arr = np.array(seed_numest_pair)
#print(seed_numest_pair_arr[:,1])



estind_values = np.arange(len(C_values))



seed_indices = np.arange(len(seeds))

#print(num_estimators_values)
#print(estind_values)

#print(seeds)
#print(seed_indices)


def kfoldcv(seed,numest,alphav):
    start = time.time()
    
    np.random.seed(int(seed))
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)

    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)

    
    num_synthetic_samples = len(mydata_withsynthetic) - len(mydata) #note: the new file contains original data and synthetic data 
    new_synthetic_indices = np.arange(num_samples, num_samples+num_synthetic_samples,1)
    #print(new_synthetic_indices)
    
    train_validate_puresynthetic_index = np.concatenate( (train_validate_index, new_synthetic_indices) , axis=None)

    
    
    #print ('starting kfoldcv')
    #num_estimators_arg = num_estimators_values[estind]
    C_val_arg = numest
    alpha_val_arg = alphav
    
    #train_validate_puresynthetic_index = args[1]
    #test_sample_index = args[2]
    
    fold_length = int(math.ceil((1.0*len(train_validate_puresynthetic_index))/crossvalidate_k))
    splitpoints = np.arange(0,len(train_validate_puresynthetic_index),fold_length)
    
    rmses = np.zeros(crossvalidate_k) 
    for i in np.arange(len(splitpoints)):
        #print(i)
        if i<len(splitpoints)-1:
            validate_index = train_validate_puresynthetic_index[splitpoints[i]:splitpoints[i+1]]
        else:
            validate_index = train_validate_puresynthetic_index[splitpoints[i]:]
        train_index = [x for x in train_validate_puresynthetic_index if x not in validate_index]
        #print(validate_index)
        #print(len(validate_index))
        #print(train_index)
        #print(len(train_index))
        #print('**************************')


        train_feat = pure_synthetic_features[train_index]
        train_feat = [np.reshape(x, (num_features, )) for x in train_feat]

        train_out = pure_synthetic_output[train_index]
        train_out = np.reshape(train_out, (len(train_out),))
        #print(train_data)

        #print('train')
        #print(i,np.shape(train_feat), np.shape(train_out))

        validate_feat = pure_synthetic_features[validate_index]
        validate_feat = [np.reshape(x, (num_features, )) for x in validate_feat]

        validate_out = pure_synthetic_output[validate_index]
        validate_out = np.reshape(validate_out, (len(validate_out),))
        #print(train_data)

        #print('validate')
        #print(i,np.shape(validate_feat), np.shape(validate_out))

        #print(len(validate_samples))

        regr = GradientBoostingRegressor(loss='huber', learning_rate=0.1, n_estimators=800, subsample=C_val, 
                                         criterion='mse', min_samples_split=2, min_samples_leaf=1, 
                                         min_weight_fraction_leaf=0.0, max_depth=1, min_impurity_decrease=0.0, 
                                         min_impurity_split=None, init=None, random_state=None, max_features=None, 
                                         alpha=alpha_val_arg, verbose=0, max_leaf_nodes=None, warm_start=False, presort='auto')
        regr.fit(train_feat, train_out)
        #print(regr.feature_importances_)

        #pred = regr.predict(train_feat)
        #tmp = ((x,y) for x,y in zip(pred, train_out))
        #print(list(tmp))


        pred = regr.predict(validate_feat)
        #tmp = ((x,y) for x,y in zip(pred, validate_out))
        #print(list(tmp))

        mse = sum((x-y)*(x-y) for x,y in zip(pred,validate_out))/len(validate_feat)
        rmse = np.sqrt(mse)

        #print(i,rmse)
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

        rmses[i] = rmse

    avg_rmse = np.average(rmses)
        
    return seed,C_val_arg,alpha_val_arg,time.time() - start,avg_rmse




def compute_testrmse(seed,best_C_val, best_alpha_val):
    start = time.time()
    
    np.random.seed(int(seed))
    
    sample_index = np.arange(num_samples)
    #print(sampleindex)

    shuffled_indices = shuffle(sample_index)
    #print(shuffled_indices)

    
    test_proportion = 0.2  #set the proportion of test samples 
    num_test = int(test_proportion * num_samples) 
    #print(num_test)

    test_sample_index = shuffled_indices[:num_test]
    
    test_sample_index_list.append(test_sample_index)
    #print(test_sample_index)
    #print(len(test_sample_index))

    #split the remaining part into ten folds 
    train_validate_index = shuffled_indices[num_test:]
    #num_train_validate_samples = len(train_validate_index)
    #print(num_train_validate_samples)

    
    num_synthetic_samples = len(mydata_withsynthetic) - len(mydata) #note: the new file contains original data and synthetic data 
    new_synthetic_indices = np.arange(num_samples, num_samples+num_synthetic_samples,1)
    #print(new_synthetic_indices)
    
    train_validate_puresynthetic_index = np.concatenate( (train_validate_index, new_synthetic_indices) , axis=None)
    
    #print('run:%d num estimators: %d avg. rmse: %f' %(run,num_estimators_arg, avg_rmse))
    
    #training set 
    final_train_feat = pure_synthetic_features[train_validate_puresynthetic_index]
    final_train_feat = [np.reshape(x, (num_features, )) for x in final_train_feat]

    final_train_out = pure_synthetic_output[train_validate_puresynthetic_index]
    final_train_out = np.reshape(final_train_out, (len(final_train_out),))

    #test set 
    final_test_feat = norm_features[test_sample_index]
    final_test_feat = [np.reshape(x, (num_features, )) for x in final_test_feat]

    final_test_out = output[test_sample_index]
    final_test_out = np.reshape(final_test_out, (len(final_test_out),))


    final_best_C_val = best_C_val
    final_best_alpha_val = best_alpha_val
    final_regr = GradientBoostingRegressor(loss='huber', learning_rate=0.1, n_estimators=800, subsample=final_best_C_val, 
                                         criterion='mse', min_samples_split=2, min_samples_leaf=1, 
                                         min_weight_fraction_leaf=0.0, max_depth=1, min_impurity_decrease=0.0, 
                                         min_impurity_split=None, init=None, random_state=None, max_features=None, 
                                         alpha=final_best_alpha_val, verbose=0, max_leaf_nodes=None, warm_start=False, presort='auto')
    final_regr.fit(final_train_feat, final_train_out)
    #print(regr.feature_importances_)

    #pred = regr.predict(train_feat)
    #tmp = ((x,y) for x,y in zip(pred, train_out))
    #print(list(tmp))

    pred = final_regr.predict(final_test_feat)
    #tmp = ((x,y) for x,y in zip(pred, final_test_out))
    #print(list(tmp))
    absError = abs(pred-final_test_out)
    final_mse = sum((x-y)*(x-y) for x,y in zip(pred,final_test_out))/len(final_test_feat)
    final_rmse = np.sqrt(final_mse)




    #train rmse computed below
    tr_pred = final_regr.predict(final_train_feat)
    tr_final_mse = sum((x-y)*(x-y) for x,y in zip(tr_pred,final_train_out))/len(final_train_feat)
    tr_final_rmse = np.sqrt(tr_final_mse)

    with open('gradientBoostBL2Prediction-out.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(zip(itertools.repeat(seed),test_sample_index, pred, final_test_out, absError))
    csvFile.close()


    return seed,best_C_val,best_alpha_val,time.time() - start, final_rmse, tr_final_rmse


def main():
    avg_rmse_ret = []
    C_val_ret = [] 
    alpha_val_ret = []
    
    
    
    for seed in seeds: 
        avg_rmse_ret.append([])
        C_val_ret.append([])    
        alpha_val_ret.append([])  
    
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,C_val,alpha_val,time_ret,avg_rmse in executor.map(kfoldcv, seed_numest_pair_arr[:,0], seed_numest_pair_arr[:,1], seed_numest_pair_arr[:,2]):
             seed_index = int((seed-seed_start)/seed_step)
             avg_rmse_ret[seed_index].append(avg_rmse)
             C_val_ret[seed_index].append(C_val)
             alpha_val_ret[seed_index].append(alpha_val)
             print('seed:%f numest: %f alpha val:%f time: %f avg_rmse: %f' %(seed, C_val, alpha_val, time_ret,avg_rmse), flush=True)
    print('k fold cv completed ! Time taken: %f seconds' %(time.time()-start) , flush=True)
    #print(C_val_ret)
    #print(alpha_val_ret)

    
    for seed in seeds: 
        seed_index = int((seed-seed_start)/seed_step)
        tmp = avg_rmse_ret[seed_index]
        #print(tmp)
        argminind=np.argmin(tmp)
        #print(argminind)
        #print(tmp)
        estlist = C_val_ret[seed_index]
        alphaestlist = alpha_val_ret[seed_index]
        #print(estlist)
        best_C_values[seed_index]= (estlist[np.argmin(tmp)])
        best_alpha_values[seed_index] = (alphaestlist[np.argmin(tmp)])
        print('seed:%d argmin numest: %f argmin alpha est: %f' %(seed,best_C_values[seed_index], best_alpha_values[seed_index]), flush=True)

    #print(best_est)

    start = time.time()        
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,best_C_val,best_alpha_val,time_ret,test_rmse,train_rmse in executor.map(compute_testrmse, seeds, best_C_values, best_alpha_values):
             print('seed:%f best C val:%f best alpha val:%f time: %f test_rmse: %f train rmse: %f' %(seed,best_C_val,best_alpha_val,time_ret,test_rmse, train_rmse),flush=True)
             seed_index = int((seed-seed_start)/seed_step)
             test_rmses[seed_index]=test_rmse

             train_rmses[seed_index]=train_rmse
	
    print('Test rmse computed ! Time taken: %f seconds' %(time.time()-start) , flush=True)

    print('mean+/-std.dev of test rmse for %d runs: %f +/- %f' %(len(seeds),np.average(test_rmses), np.std(test_rmses)), flush= True)
        
    print('mean+/-std.dev of train rmse for %d runs: %f +/- %f' %(len(seeds),np.average(train_rmses), np.std(train_rmses)), flush= True)

if __name__ == '__main__':
    start = time.time()
    main()
    total_time = time.time() - start
    
    print('total time after completion: %f seconds' %(total_time), flush=True)




