#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
features_list = ['poi','deferred_income', 'total_stock_value', 
                 'exercised_stock_options']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers

data_dict.pop('TOTAL',0)

### Task 3: Create new feature(s)

for i in data_dict:
    if data_dict[i]['salary'] == 'NaN':
        if data_dict[i]['restricted_stock'] == 'NaN':
            data_dict[i]['comp_sal_restr_stock'] = 0
        else:
            data_dict[i]['comp_sal_restr_stock'] = int(data_dict[i]['restricted_stock'])
    elif data_dict[i]['restricted_stock'] == 'NaN':
        data_dict[i]['comp_sal_restr_stock'] = int(data_dict[i]['salary'])
    else:
        data_dict[i]['comp_sal_restr_stock'] = int(data_dict[i]['salary']) + int(data_dict[i]['restricted_stock'])
    
### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()

#from sklearn.tree import DecisionTreeClassifier
#clf = DecisionTreeClassifier(max_depth=2, min_samples_split=2, 
                             #min_samples_leaf=4)

#from sklearn.ensemble import RandomForestClassifier
#clf = RandomForestClassifier(max_depth=8, min_samples_split=4, 
                             #min_samples_leaf=1)

#from sklearn.model_selection import GridSearchCV

#parameters = {'max_depth':[2, 4, 6, 8, 10, 12],
              #'min_samples_split':[2, 4, 6, 8, 10], 
              #'min_samples_leaf':[1, 2, 3, 4, 5, 6]}

#grid = GridSearchCV(clf, parameters)

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!
from sklearn.model_selection import train_test_split
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

#grid.fit(features_train, labels_train)

#print(grid.best_score_, grid.best_params_)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)