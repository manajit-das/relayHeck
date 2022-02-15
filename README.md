# relayHeck: codes and data
How to use? 

(1)Take the experimental dataset i.e. only the features and label ('ee') from the 'relayHeckAllData.xlsx' file (sheet1, name-'real') and save it as a .csv file.

(2)Add synthetic data, for instance borderline-2 using the file-'smote.ipynb'. Save the experimental plus synthetic data into a single .csv file. e.g. Sheet2 (name-'realPlusSynBL2') in the 'relayHeckAllData.xlsx' file.

(3)To run a Random Forest model with synthetic data, use 'rf_pure_synthetic_data.py'. In this .py file replace the existing file names with your two file names i.e. experimental data set and mixed data set.

(4)To run a Random Forest model only with experimental data use 'RandomForestRealData.py'

Similar process is to be followed for k-Nearest Neighbour and Gradient Boosting with the relevent .py file as provided.

(5)For building Deep Neural Network model only with experimental data use 'dnnPureData.ipynb' file and 'dnn_pure_synthetic.ipynb' for experimental plus synthetic data.

The identity of the reaction entities are provided in the Supporting Information.
