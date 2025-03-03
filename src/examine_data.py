import h5py
import numpy as np
import json
import os

def examine_mat_file(filename):
    """Examine and print contents of a MAT file"""
    print(f"Examining file: {filename}")
    
    f = h5py.File(filename, 'r')
    sentence_data = f['sentenceData']
    
    # Print available fields
    print('\nAvailable fields in sentenceData:')
    print(list(sentence_data.keys()))
    
    # Get first sentence content as example
    content_ref = sentence_data['content'][0][0]
    sentence = ''.join(chr(c[0]) for c in f[content_ref][:])
    print('\nExample sentence:')
    print(sentence)
    
    # Get eye tracking data structure
    et_ref = sentence_data['rawET'][0][0]
    et_data = f[et_ref][:]
    print('\nEye tracking data shape:', et_data.shape)
    print('Eye tracking data first few rows:', et_data[:2])
    
    # Get fixation data
    fix_ref = sentence_data['allFixations'][0][0]
    fix_data = f[fix_ref][:]
    print('\nFixation data shape:', fix_data.shape)
    print('Fixation data first few values:', fix_data[:2])
    
    # Save example data as JSON
    example_data = {
        'sentence': sentence,
        'eye_tracking': et_data[:2].tolist(),
        'fixations': fix_data[:2].tolist()
    }
    
    with open('example_data.json', 'w') as f:
        json.dump(example_data, f, indent=2)
    print('\nSaved example data to example_data.json')

if __name__ == "__main__":
    # Use YAC's normal reading data as example
    filename = "../data/train/resultsYAC_NR.mat"
    examine_mat_file(filename) 