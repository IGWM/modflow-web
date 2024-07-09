FROM continuumio/miniconda3

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create conda environment
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "modflow_env", "/bin/bash", "-c"]

# Install MODFLOW6 and other Python dependencies
RUN conda install -c conda-forge modflow6

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set PATH to include the conda environment
ENV PATH /opt/conda/envs/modflow_env/bin:$PATH
ENV PYTHONPATH=/app
# Use bash as the default shell
SHELL ["/bin/bash", "-c"]

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]