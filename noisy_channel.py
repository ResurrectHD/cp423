"""
CP 423
Assignment 2 - Q 4

 Authors:
 Josh Degazio - 190560510
 Adrian Alting-Mees - 190743560
 Robert Mazza - 190778040

 Date: 13-03-2023

 FILE INFO
 Depending on user input, uses wikipedia dataset to get the probability of a list of words, 
 or the correct spellings of incorrect words using the Noisy Channel Model.
"""
import argparse
import json
import os
import nltk
from nltk.corpus import stopwords
from nltk import FreqDist
import re
from collections import Counter

try:
    #Download appropriate NLTK packages
    print('')
    print('Downloading packages...')
    nltk.download('stopwords')
    nltk.download('punkt')

    # Load and preprocess the corpus
    stop_words = set(stopwords.words('english'))
    corpus = []
    total_words = 0
    try:
        print('')
        print('Opening Wikipedia pages...')
        for filename in os.listdir('enwiki20201020'):
            with open(os.path.join('enwiki20201020', filename), 'r', encoding='utf-8') as f:
                doc = json.load(f)
                i=0
                total_words = 0
                #In the JSON files, go through and get each webpages text
                for page in doc:
                    text = page['text']
                    tokens = nltk.word_tokenize(text)
                    tokens = [word.lower() for word in tokens if word.lower() not in stop_words and re.match("^[a-zA-Z0-9]*$", word)]
                    total_words += len(tokens)
                    corpus += tokens
                    i+=1
    except:
        print('Error opening files')
        print('Closing Program.')
        exit(0)

    # Build a language model from the preprocessed corpus
    lm = FreqDist(corpus)

    # Define the edit distance function
    def edit_distance(word1, word2):
        #Check which word is longer
        if len(word1) > len(word2):
            word1, word2 = word2, word1
        distances = range(len(word1) + 1)
        for index2, char2 in enumerate(word2):
            new_distances = [index2 + 1]
            for index1, char1 in enumerate(word1):
                if char1 == char2:
                    new_distances.append(distances[index1])
                else:
                    new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))
            distances = new_distances
        return distances[-1]

    # Define the Noisy Channel Model function
    def noisy_channel_model(word, candidates):
        channel_probs = {}
        
        # Iterate over each candidate word in the list
        for candidate in candidates:
            # Calculate the edit distance between the original word and the candidate
            edit_dist = edit_distance(word, candidate)
            
            # Update the channel_probs dictionary
            if edit_dist in channel_probs:
                # If there are already candidates with the same edit distance, append the new candidate to the list
                channel_probs[edit_dist].append(candidate)
            else:
                # If it's a new edit distance, create a new list with the candidate
                channel_probs[edit_dist] = [candidate]
            
        # Initialize an empty dictionary to store candidate probabilities
        probs = {}
        
        # Iterate over each candidate word in the list
        for candidate in candidates:
            # Calculate the edit distance between the original word and the candidate
            edit_dist = edit_distance(word, candidate)
            
            # Calculate the probability of the candidate
            prob = (1 / (edit_dist + 1)) * lm[candidate]
            
            # Add the candidate
            probs[candidate] = prob
        return probs

    # Implement the command-line options
    parser = argparse.ArgumentParser()
    parser.add_argument('--correct', nargs='+', help='Correct misspelled words')
    parser.add_argument('--proba', nargs='+', help='Get the probability of words')
    args = parser.parse_args()

    #Create empty candidate set
    candidates = set()

    #If user selected correct instead of proba
    if args.correct:
        print('')
        print('Calculating candidates...')
        print('')
        for word in args.correct:
            candidates = set()
            #Get all candidates with edit distance one
            for i in range(len(word)):
                # deletion
                candidate = word[:i] + word[i+1:]
                candidates.add(candidate)
                # transposition
                if i < len(word)-1:
                    candidate = word[:i] + word[i+1] + word[i] + word[i+2:]
                    candidates.add(candidate)
                # substitution
                for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
                    candidate = word[:i] + char + word[i+1:]
                    candidates.add(candidate)
                # insertion
                for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
                    candidate = word[:i] + char + word[i:]
                    candidates.add(candidate)
            #Get all candidates with edit distance two
            temp_candidates = candidates.copy()
            for word2 in temp_candidates:
                for i in range(len(word2)):
                    # deletion
                    candidate = word2[:i] + word2[i+1:]
                    candidates.add(candidate)
                    # transposition
                    if i < len(word2)-1:
                        candidate = word2[:i] + word2[i+1] + word2[i] + word2[i+2:]
                        candidates.add(candidate)
                    # substitution
                    for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
                        candidate = word2[:i] + char + word2[i+1:]
                        candidates.add(candidate)
                    # insertion
                    for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
                        candidate = word2[:i] + char + word2[i:]
                        candidates.add(candidate)
            probs = noisy_channel_model(word, candidates)
            best_candidate = max(probs, key=probs.get)
            #best_candidate = (list(probs.keys())[list(probs.values()).index((sorted(probs.values())[-1]))])
            print(f"{word} -> {best_candidate}")

    #If user selected proba instead of correct
    if args.proba:
        print('')
        print('Calculating word probability...')
        print('')
        for word in args.proba:
            probability = round((lm[word]/total_words), 4)
            print(word)
            print('- probability up to 4 decimals: ' + str(probability) + '%')
            print('- probability * 10000: ' + str(round(((lm[word]/total_words) * 10000),4)))
            print('- total occurrences: ' + str(lm[word]))
            print('')

    '''for keys, value in probs.items():
    print(keys + ',' + str(probs[keys]))

    print(lm)
    print('\n\n\n' + str(lm['university']) + ', ' + str(lm['improve']) + ', ' + str(lm['games']))'''
    print('Program Ended.')
except:
    print("Error.")
    print("Closing Program.")
    exit(0)