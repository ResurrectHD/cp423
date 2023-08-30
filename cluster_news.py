"""
CP 423
Assignment 3 - Q 2

 Authors:
 Josh Degazio - 190560510
 Adrian Alting-Mees - 190743560
 Robert Mazza - 190778040

 Date: 02-04-2023 (DD-MM-YYYY)

 FILE INFO
 This program clusters textual data from the 20-newsgroups dataset using various clustering algorithms, 
 such as KMeans, Ward Hierarchical Clustering, Agglomerative Clustering, and DBSCAN. 
 It reports clustering performance and saves the models.
"""

#Imports
import argparse
import pickle
import numpy as np
from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import adjusted_mutual_info_score, adjusted_rand_score, completeness_score
from sklearn.datasets import fetch_20newsgroups

def load_data():
    try:
        newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
    except Exception as e:
        print(f"Error loading data: {e}")
        raise
    return newsgroups

def preprocess_data(data):
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(data.data)
    except Exception as e:
        print(f"Error preprocessing data: {e}")
        raise
    return X

def cluster_data(X, n_clusters, method):
    #Go through methods and run them
    if method == 'kmeans':
        model = KMeans(n_clusters=n_clusters, n_init=10)
    elif method == 'whc':
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    elif method == 'ac':
        model = AgglomerativeClustering(n_clusters=n_clusters, linkage='average')
    elif method == 'dbscan':
        model = DBSCAN(eps=0.5, min_samples=5)
    else:
        raise ValueError(f"Invalid clustering method selected: {method}")

    try:
        labels = model.fit_predict(X.toarray())
    except Exception as e:
        print(f"Error clustering data: {e}")
        raise

    if method == 'dbscan':
        labels[labels == -1] = n_clusters

    return labels

def evaluate_performance(labels, target):
    try:
        #Use sklearn functions
        ami = adjusted_mutual_info_score(target, labels)
        ars = adjusted_rand_score(target, labels)
        cs = completeness_score(target, labels)
    except Exception as e:
        print(f"Error evaluating performance: {e}")
        raise
    return ami, ars, cs

def save_model(model, filename):
    try:
        #Save the model using Pickle
        with open(filename, 'wb') as f:
            pickle.dump(model, f)
    except Exception as e:
        print(f"Error saving model: {e}")
        raise

def main(args, method):
    try:
        data = load_data()
        X = preprocess_data(data)

        #Sets the clusters to 20 if there was no specified number
        n_clusters = [20] if not args.ncluster else list(map(int, args.ncluster.split(',')))

        for n in n_clusters:
            labels = cluster_data(X, n, method)

            #Set variables
            target = data.target
            ami, ars, cs = evaluate_performance(labels, target)

            #Print performance and method
            print(f'Number of clusters: {n}')
            print(f'Clustering method: {method}')
            print(f'Adjusted Mutual Information: {ami:.4f}')
            print(f'Adjusted Random Score: {ars:.4f}')
            print(f'Completeness Score: {cs:.4f}')
            print("----------------------------------------------")

            save_model(labels, f'clustering_model_{n}_{method}.pkl')
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == '__main__':
    #Add cmd line args
    parser = argparse.ArgumentParser()
    parser.add_argument('--ncluster', type=str, help='Number of clusters')
    parser.add_argument('--kmeans', action='store_true', help='Use KMeans clustering')
    parser.add_argument('--whc', action='store_true', help='Use Ward Hierarchical Clustering')
    parser.add_argument('--ac', action='store_true', help='Use Agglomerative Clustering')
    parser.add_argument('--dbscan', action='store_true', help='Use DBSCAN clustering')

    args = parser.parse_args()
    #Check which cluster method is present in the args
    if args.kmeans:
        main(args, "kmeans")
    if args.whc:
        main(args, "whc")
    if args.ac:
        main(args, "ac")
    if args.dbscan:
        main(args, "dbscan")
    if not any([args.kmeans, args.whc, args.ac, args.dbscan]):
        parser.error("At least one clustering method must be specified.")
        
    #Finito
    print("Program Ended.")