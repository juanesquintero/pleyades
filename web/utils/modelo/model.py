import os
import pickle

modelos_folder = os.getcwd()+'/uploads/modelos'


def save_classifirer(mejor_clasificador, conjunto=''):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'wb') as file:
        pickle.dump(mejor_clasificador, file)
    pickle.dump(
        mejor_clasificador, 
        open(f'{modelos_folder}/{conjunto}.sav', 'wb')
    )


def load_classifer(conjunto):
    clf_file = f'{modelos_folder}/{conjunto}.pkl'
    with open(clf_file, 'rb') as file:
        clf = pickle.load(file)
    clf = pickle.load(open(clf_file, 'rb'))
    return clf
