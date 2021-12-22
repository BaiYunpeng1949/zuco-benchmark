from sklearn.svm import SVC
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import precision_recall_fscore_support
from sklearn.utils import resample

import numpy as np
import config

def build_data(data, labels):
    """
    Builds the data for the classification task.
    TODO vectorize
    """
    X, y = [],[]
    for subj in data:
        for it in data[subj]:
            X.append(it)
        for label in labels[subj]:
            if label == "NR":
                y.append(1)
            else:
                y.append(0)
    return X, y


def bootstrap_confidence(clf, test_X, test_y, index, subj):
    """Bootrap metrics"""

    accs, ps, rs, f1s, b_preds = [], [], [], [], []
    resampled_Xs, resampled_ys = [resample(test_X[index], test_y[index], replace=True, \
        n_samples=len(test_X),random_state=config.seed+i) \
            for i in range(config.n_bootstraps)]
    return zip(*[predict_subject(clf, resampled_Xs,resampled_ys,data_index, subj)\
             for data_index in range(config.n_bootstraps)])

def predict_subject(clf, test_X, test_y, index, subj):
    """Predict on a single subject"""

    print("\nPredicting on subject ", subj)
    prediction = clf.predict(test_X[index])
    if config.randomized: 
        prop = 390/739
        prediction = np.random.choice([0,1], len(prediction), p=[prop, 1-prop]) 
    accuracy = len([i for i, j in zip(prediction, test_y[index]) if i == j]) / len(test_y[index])
    print('Accuracy ', accuracy)
    p,r,f1,_ = precision_recall_fscore_support(test_y[index], prediction, average='macro')
    print('F1 ', f1)
    return prediction, accuracy, f1, p,r

def benchmark(X, y, test_X, test_y): 
    """Classification for the benchmark task."""

    np.random.seed(config.seed)
    #preprocess data
    print("\nPre-processing ")
    train_X, train_y = build_data(X, y)
    builded= zip(*[build_data({subj:test_X[subj]}, {subj:test_y[subj]}) \
        for subj in test_X])
    test_X, test_y = builded
    train_X, train_y = shuffle(train_X, train_y)

    # scale feature values
    scaling = MinMaxScaler(feature_range=(0, 1)).fit(train_X)
    train_X = scaling.transform(train_X)
    test_X = [scaling.transform(subj) for subj in test_X]
    
    print("\nTraining on all subjects in the train split ")
    # train SVM classifier
    clf = SVC(random_state=config.seed, kernel=config.kernel, \
        gamma='scale', cache_size=1000)

    clf.fit(train_X, train_y)
    train_acc = len([i for i, j in zip(clf.predict(train_X), train_y) if i == j]) / len(train_y)
    print("Train accuracy ", train_acc)

    # predict on all subjects
    results = list(zip(*[predict_subject(clf,test_X,test_y,index, subj)\
             for index, subj in enumerate(config.heldout_subjects)]))
    results.append(train_acc)
    bootstrap_results = []
    if config.bootstrap:
         bootstrap_results = list(zip(*[bootstrap_confidence(clf,test_X,test_y,index, subj)\
             for index, subj in enumerate(config.heldout_subjects)]))

    return results+bootstrap_results
        