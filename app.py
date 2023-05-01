from flask import Flask, request, render_template
import cv2
import numpy as np
from sklearn.cluster import KMeans
from pyswarm import pso

app = Flask(__name__)

# Load the image as a color or gray-scale image


def load_image(image_path, color=True):
    if color:
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    else:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    return image

# Flatten the image to a 2D array of pixels or a 1D array of gray-scale pixels


def flatten_image(image):
    if len(image.shape) == 3:
        pixels = image.reshape(-1, 3)
    else:
        pixels = image.reshape(-1, 1)
    return pixels

# Define the objective function for PSO


def objective_function(positions, pixels):
    # Reshape the positions to cluster centroids
    if len(pixels[0]) == 3:
        centroids = positions.reshape(-1, 3)
    else:
        centroids = positions.reshape(-1, 1)
    # Assign each pixel to the closest centroid
    labels = KMeans(n_clusters=len(centroids), init=centroids,
                    n_init=1).fit_predict(pixels)
    # Calculate the mean squared error between the original pixels and the centroids
    mse = np.mean((pixels - centroids[labels]) ** 2)
    return mse

# Perform PSO optimization


def perform_pso_optimization(pixels, num_centroids, num_particles):
    lower_bound = np.zeros(pixels.shape[1] * num_centroids)
    upper_bound = np.ones(pixels.shape[1] * num_centroids) * 255
    result, _ = pso(objective_function, lower_bound,
                    upper_bound, args=(pixels,), swarmsize=num_particles, maxiter=200, debug=True)
    # Reshape the optimized result to get the final centroids
    if pixels.shape[1] == 3:
        centroids = result.reshape(-1, 3)
    else:
        centroids = result.reshape(-1, 1)
    return centroids

# Perform image segmentation and return segmented image


def perform_image_segmentation(image_path, num_centroids, num_particles, color=True):
    image = load_image(image_path, color)
    pixels = flatten_image(image)
    centroids = perform_pso_optimization(pixels, num_centroids, num_particles)
    labels = KMeans(n_clusters=len(centroids), init=centroids,
                    n_init=1).fit_predict(pixels)
    if len(image.shape) == 3:
        segmented_image = centroids[labels].reshape(image.shape)
        segmented_image = cv2.cvtColor(
            segmented_image.astype(np.uint8), cv2.COLOR_RGB2BGR)
    else:
        segmented_image = centroids[labels].reshape(image.shape)
        segmented_image = segmented_image.astype(np.uint8)
    return segmented_image


@app.route('/', methods=['GET', 'POST'])
def image_segmentation():
    if request.method == 'POST':
        # Get uploaded file
        image_file = request.files['image']
        # Save the uploaded file to a temporary location
        image_path = 'static/temp.jpg'
        image_file.save(image_path)
        # Get form values
        num_centroids = int(request.form['num_centroids'])
        num_particles = num_centroids * 3
        color = True if request.form.get('color') == 'color' else False
        # Perform image segmentation
        # Example values for num_centroids and num_particles
        segmented_image = perform_image_segmentation(
            image_path, num_centroids, num_particles, color)
        # write segmented image to a file and send it to result.html
        cv2.imwrite('static/segmented_image.jpg', segmented_image)
        segmented_image = 'static/segmented_image.jpg'
        # Render the segmented image in HTML
        return render_template('result.html', segmented_image_path=segmented_image, original_image_path=image_path)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
