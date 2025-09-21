# app/core/logging.py

import logging

# Configure global logging format and level
logging.basicConfig(
    level=logging.INFO,  # Log level set to INFO
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
