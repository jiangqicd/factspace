from sklearn import datasets
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
iris = datasets.load_iris()
print(iris)
X_reduced = PCA(n_components=2).fit_transform(iris.data,iris.target)
print(X_reduced)
kmeans = KMeans(n_clusters=3).fit(X_reduced)
plt.scatter(X_reduced[:, 0], X_reduced[:, 1], c=kmeans.labels_, cmap=plt.cm.Set1)
plt.show()
