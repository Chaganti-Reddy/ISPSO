import cv2
import numpy as np
from sklearn.cluster import KMeans
from pyswarm import pso

# Load the image
image = cv2.imread('tst.jpg')
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Flatten the image to a 2D array of pixels
pixels = image.reshape(-1, 3)

# Define the objective function for PSO


def objective_function(positions):
    # Reshape the positions to cluster centroids
    centroids = positions.reshape(-1, 3)
    # Assign each pixel to the closest centroid
    labels = KMeans(n_clusters=len(centroids), init=centroids,
                    n_init=1).fit_predict(pixels)
    # Calculate the mean squared error between the original pixels and the centroids
    mse = np.mean((pixels - centroids[labels]) ** 2)
    return mse


# Define the bounds for the PSO optimization
# The bounds represent the possible values for each channel of a pixel (0 to 255)
num_centroids = 5  # Number of clusters/centroids
num_particles = num_centroids * 3  # Number of particles in PSO
lower_bound = np.zeros(3 * num_centroids)
upper_bound = np.ones(3 * num_centroids) * 255

# Perform PSO optimization
num_centroids = 5  # Number of clusters/centroids
num_particles = num_centroids * 3  # Number of particles in PSO
result, _ = pso(objective_function, lower_bound,
                upper_bound, swarmsize=num_particles)

# Reshape the optimized result to get the final centroids
centroids = result.reshape(-1, 3)

# Assign each pixel to the closest centroid
labels = KMeans(n_clusters=len(centroids), init=centroids,
                n_init=1).fit_predict(pixels)

# Replace the pixels with the centroid values
segmented_image = centroids[labels].reshape(image.shape)

# Convert back to BGR color space for display
segmented_image = cv2.cvtColor(
    segmented_image.astype(np.uint8), cv2.COLOR_RGB2BGR)

# Display the original and segmented images
cv2.imshow('Original Image', image)
cv2.imshow('Segmented Image', segmented_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
