# Use official Odoo 17 image
FROM odoo:17

USER root

# Copy your Python package requirements
COPY ./etc/requirements.txt /tmp/requirements.txt

# Install required Python libraries
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Clean up
RUN rm /tmp/requirements.txt

# Switch back to odoo user for safety
USER odoo
