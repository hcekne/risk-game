FROM python:3.11-slim


RUN apt-get update && \
	apt-get install -y \
	nano \
	git

# Set the working directory
WORKDIR /app

# Create a temporary directory for requirements
RUN mkdir /tmp/requirements

COPY requirements.txt /tmp/requirements/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements/requirements.txt 

# Remove the temporary directory
RUN rm -rf /tmp/requirements

# Use build arguments for user details
ARG USER_NAME
ARG USER_ID
ARG GROUP_ID

# Create a non-root user with home directory
RUN groupadd -g $GROUP_ID $USER_NAME && \
	useradd -u $USER_ID -g $GROUP_ID -m -d /home/$USER_NAME -s /bin/bash $USER_NAME

# Set permissions for the working directory
RUN chown -R $USER_NAME:$USER_NAME /app

# Copy and set permissions for the/custom_startup script
COPY custom_startup.sh /usr/local/bin/custom_startup.sh
RUN chmod +x /usr/local/bin/custom_startup.sh

# Switch to the non-root user
USER $USER_NAME

# Make port 80 available to the world outside this container
EXPOSE 80

# Set the/custom_startup 
# ENTRYPOINT ["/usr/local/bin/custom_startup.sh"]

# set the default command to run when starting the container
#CMD ["tail", "-f", "/dev/null"]
