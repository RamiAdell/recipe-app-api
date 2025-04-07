#!/bin/sh

# Create directories if they don't exist
mkdir -p /vol/web/media/uploads
mkdir -p /vol/web/static

# Set proper ownership and permissions
chmod -R 775 /vol/web/media/uploads

# Execute the command passed to the script
exec "$@"