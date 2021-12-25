# -*- coding: utf-8 -*-
"""

@author: P. Balamurugan, Sukriti Singh, Monika Pareek, Avtar Changotra
"""

#This code is suitable for multi-processing
#the following code is for K-NN regression with k-fold cv for 100 different seed values and reports the average rmse along with standard deviation
#This code works on only pure data (without synthetic data)  


import numpy as np
from sklearn.preprocessing import normalize #normalize is not used in the code, but can be tried
from sklearn.utils import shuffle 
import math 
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from numpy import inf

import concurrent.futures
import time

global num_features
global crossvalidate_k

global train_pure_synthetic_index_list
global test_sample_index_list 

global seeds
global num_estimators_values
global splitpoints

global seed_numest_pair_arr

global seed_start
global seed_step
global final_seed
global best_est 

global test_rmses
global train_rmses

test_sample_index_list = []
train_pure_synthetic_index_list = []
splitpoints = []

crossvalidate_k = 7 #number of folds for cross-validation

mydata=pd.read_csv('ExpDataMatrix.csv')
mydata=mydata.to_numpy()
#mydata = np.genfromtxt('regression_pure_data.csv', delimiter=',')
num_features = len(mydata[0])-1

features = mydata[:,0:num_features]
output = mydata[:,num_features:]

norm_features = features

#print(norm_features)
#print(mydata)

num_samples = len(mydata)
#print(num_samples)


seed_start = 0
seed_end = 10000 #this depends on number of seeds
seed_step = 100


seeds = np.arange(seed_start,seed_end,seed_step) 
final_seed = (seeds[len(seeds)-1])

test_rmses = np.zeros(len(seeds))
train_rmses = np.zeros(len(seeds))
 
best_est = 0*np.arange(0,len(seeds),1)

num_estimators_values = np.arange(3,101,1) 
seed_numest_pair = []

for seed in seeds:
    for num_est in num_estimators_values:
        seed_numest_pair.append([seed,num_est])

#print(seed_numest_pair)
seed_numest_pair_arr = np.array(seed_numest_pair)
#print(seed_numest_pair_arr[:,1])



estind_values = np.arange(len(num_estimators_values))

seed_indices = np.arange(len(seeds))

#print(num_estimators_values)
#print(estind_values)

#print(seeds)
#print(seed_indices)



def kfoldcv(seed,numest):
    start = time.time()
    
    np.random.seed(seed)
    
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
    
    
    #print ('starting kfoldcv')
    num_estimators_arg = numest

    
    fold_length = int(math.ceil((1.0*len(train_validate_index))/crossvalidate_k))
    splitpoints = np.arange(0,len(train_validate_index),fold_length)
    
    rmses = np.zeros(crossvalidate_k) 
    for i in np.arange(len(splitpoints)):
        #print(i)
        if i<len(splitpoints)-1:
            validate_index = train_validate_index[splitpoints[i]:splitpoints[i+1]]
        else:
            validate_index = train_validate_index[splitpoints[i]:]
        train_index = [x for x in train_validate_index if x not in validate_index]
        #print(validate_index)
        #print(len(validate_index))
        #print(train_index)
        #print(len(train_index))
        #print('**************************')


        train_feat = norm_features[train_index]
        train_feat = [np.reshape(x, (num_features, )) for x in train_feat]

        train_out = output[train_index]
        train_out = np.reshape(train_out, (len(train_out),))
        #print(train_data)

        #print('train')
        #print(i,np.shape(train_feat), np.shape(train_out))

        validate_feat = norm_features[validate_index]
        validate_feat = [np.reshape(x, (num_features, )) for x in validate_feat]

        validate_out = output[validate_index]
        validate_out = np.reshape(validate_out, (len(validate_out),))
        #print(train_data)

        #print('validate')
        #print(i,np.shape(validate_feat), np.shape(validate_out))

        #print(len(validate_samples))
        regr = KNeighborsRegressor(n_neighbors=num_estimators_arg)

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

        #if i==len(splitpoints)-1:
            #print(train_feat)
            #print(train_out)
            #print(validate_out)
        #print(rmses)
    avg_rmse = np.average(rmses)
        
    return seed,numest,time.time() - start,avg_rmse


def compute_testrmse(seed,best_numest):
    start = time.time()
    
    np.random.seed(seed)
    
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
    
    #training set 
    final_train_feat = norm_features[train_validate_index]
    final_train_feat = [np.reshape(x, (num_features, )) for x in final_train_feat]

    final_train_out = output[train_validate_index]
    final_train_out = np.reshape(final_train_out, (len(final_train_out),))

    #test set 
    final_test_feat = norm_features[test_sample_index]
    final_test_feat = [np.reshape(x, (num_features, )) for x in final_test_feat]

    final_test_out = output[test_sample_index]
    final_test_out = np.reshape(final_test_out, (len(final_test_out),))


    final_best_estimator = int(best_numest)
    final_regr = KNeighborsRegressor(n_neighbors=final_best_estimator)

    final_regr.fit(final_train_feat, final_train_out)
    #print(regr.feature_importances_)

    #pred = regr.predict(train_feat)
    #tmp = ((x,y) for x,y in zip(pred, train_out))
    #print(list(tmp))

    pred = final_regr.predict(final_test_feat)
    #tmp = ((x,y) for x,y in zip(pred, final_test_out))
    #print(list(tmp))

    final_mse = sum((x-y)*(x-y) for x,y in zip(pred,final_test_out))/len(final_test_feat)
    final_rmse = np.sqrt(final_mse)


    #train rmse computed below

    tr_pred = final_regr.predict(final_train_feat)
    tr_final_mse = sum((x-y)*(x-y) for x,y in zip(tr_pred,final_train_out))/len(final_train_feat)
    tr_final_rmse = np.sqrt(tr_final_mse)

    return seed,best_numest,time.time() - start, final_rmse, tr_final_rmse



def main():
    avg_rmse_ret = []
    numest_ret = [] 
    
    for seed in seeds: 
        avg_rmse_ret.append([])
        numest_ret.append([])    
    
    start = time.time()
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,numest,time_ret,avg_rmse in executor.map(kfoldcv, seed_numest_pair_arr[:,0],seed_numest_pair_arr[:,1]):
             seed_index = int((seed-seed_start)/seed_step)
             avg_rmse_ret[seed_index].append(avg_rmse)
             numest_ret[seed_index].append(numest)
             print('seed:%f numest: %f time: %f avg_rmse: %f' %(seed, numest,time_ret,avg_rmse), flush=True)
    print('k fold cv completed ! Time taken: %f seconds' %(time.time()-start) , flush=True)

    
    for seed in seeds: 
        seed_index = int((seed-seed_start)/seed_step)
        tmp = avg_rmse_ret[seed_index]
        #print(tmp)
        estlist = numest_ret[seed_index]
        #print(estlist)
        best_est[seed_index]= int(estlist[np.argmin(tmp)])
        
        print('seed:%d argmin numest: %d' %(seed,best_est[seed_index]), flush=True)

    #print(best_est)

    start = time.time()        
    with concurrent.futures.ProcessPoolExecutor() as executor:
         for seed,bestest,time_ret,test_rmse,train_rmse in executor.map(compute_testrmse, seeds, best_est):
             print('seed:%f bestest:%f time: %f test_rmse: %f train_rmse: %f' %(seed,bestest,time_ret,test_rmse,train_rmse),flush=True)
             seed_index = int((seed-seed_start)/seed_step)
             test_rmses[seed_index]=test_rmse

             train_rmses[seed_index]=train_rmse

    print('Test rmse computed ! Time taken: %f seconds' %(time.time()-start), flush=True)

    print('mean+/-std.dev of test rmse for %d runs: %f +/- %f' %(len(seeds),np.average(test_rmses), np.std(test_rmses)), flush= True)
    print('mean+/-std.dev of train rmse for %d runs: %f +/- %f' %(len(seeds),np.average(train_rmses), np.std(train_rmses)), flush= True)

if __name__ == '__main__':
    start = time.time()
    main()
    total_time = time.time() - start

    print('total time after completion: %f seconds' %(total_time), flush=True)

