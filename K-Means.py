# Calculate return
import pandas as pd
combined_etf_data = pd.DataFrame()
redf = combined_etf_data.shift(-1) / combined_etf_data - 1

#correlation matrix
correlation_matrix = redf.corr()

#set the threshold
threshold = 0.8
clusters = []

#traverse through correlation matrix
for i in range(correlation_matrix.shape[0]):
    for j in range(i+1, correlation_matrix.shape[1]):
        if correlation_matrix.iloc[i,j] >= threshold:
            cluster_found = False # select those whose correlation is greater than 0.8
            for cluster in clusters:
                if correlation_matrix.columns[i] in cluster or correlation_matrix.columns[j] in cluster:
                    cluster.add(correlation_matrix.columns[i])
                    cluster.add(correlation_matrix.columns[j])
                    cluster_found = True
                    break
            if not cluster_found:
                clusters.append(set([correlation_matrix.columns[i], correlation_matrix.columns[j]]))

for idx, cluster in enumerate(clusters):
    print(f"Cluster {idx + 1}: {cluster}")

cluster_centers = []
for cluster in clusters:
    valid_cols = [col for col in cluster if col in redf.columns]
    cluster_data = redf[list(cluster)]

    cluster_center = cluster_data.mean(axis = 1)
    cluster_centers.append(cluster_center)

cluster_centers_df = pd.concat(cluster_centers, axis = 1)
cluster_centers_df.columns = [f'Cluster_{i + 1}' for i in range(len(cluster_centers))]

cluster_scores = cluster_centers_df.mean(axis = 0)

if cluster_centers:
    cluster_centers_df = pd.concat(cluster_centers, axis = 1)
    cluster_centers_df.columns = [f'Cluster_{i+1}' for i in range(len(cluster_centers))]
