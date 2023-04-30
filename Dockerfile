FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt requirements.txt

RUN apt-get update && \
    apt-get install -y libopencv-dev python-opencv && \
    pip install Flask


# Install dependencies  
RUN pip3 install -r requirements.txt

# Copy all files to the container
COPY . .

# Expose the port that the app will run on
EXPOSE 5000

CMD ["python3", "app.py"]