# Use an official Python runtime as a parent image
FROM python:3.11

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Set environment variables
ENV APP_HOME /app
WORKDIR $APP_HOME

# Copy the requirements file into the container at /app
COPY requirements.txt ./
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Copy your Streamlit app code into the container at /app
COPY . .

# Define the command to run your app
ENTRYPOINT ["streamlit", "run", "streamlit-app.py", "--server.port", "8080" ]
