import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
from astroquery import xmm_newton
import tarfile
import subprocess

# Function to download and extract xmm observations
def download_and_extract_xmm_observation(observation_id, save_path):
    """
    Download and extract an XMM observation given its observation ID.
    
    Parameters:
    -----------
    observation_id : str
        The observation ID of the XMM observation to download (e.g., '0087940101').
    save_path : str
        The path to save the downloaded data to (e.g., '/path/to/save').
    """
    # Set up the XMMNewton object to access the archive.
    xmm = XMMNewton()
    
    # Download the observation data.
    xmm.download_data(observation_id, filename=f"{save_path}/{observation_id}")
    
    # Extract the downloaded tar.gz file.
    tar = tarfile.open(f"{save_path}/{observation_id}.tar")
    tar.extractall(f"{save_path}/{observation_id}")
    tar.close()

def create_xmm_ccf(observation_id, odf_directory, ccf_directory):
    """
    Generate the CCF file for an XMM-Newton observation and update the CCF system variable.

    Parameters:
    -----------
    observation_id : str
        The ID of the XMM-Newton observation.
    odf_directory : str
        The path to the directory containing the ODFs for the observation.
    ccf_directory : str
        The path to the directory where the CCF file will be saved.
    """

    # Set up the command to run cifbuild
    command = ['cifbuild', 'obsid={}'.format(observation_id), 'odfdir={}'.format(odf_directory)]

    # Run the command using subprocess
    subprocess.run(command, cwd=ccf_directory, check=True)

    # Update the CCF system variable
    ccf_file_path = '{}/ccf.cif'.format(ccf_directory)
    command = ['export', 'SAS_CCF={}'.format(ccf_file_path)]
    subprocess.run(command, shell=True, check=True)

def run_odfingest(odf_directory, cif_directory):
    """
    Run the odfingest command on the specified ODF directory and CCF directory, and update the ODF system variable.

    Parameters:
    -----------
    odf_directory : str
        The path to the directory containing the ODF files to be ingested.
    cif_directory : str
        The path to the directory containing the CCF file to use for ingestion.
    """

    # Set up the command to run odfingest
    command = ['odfingest', odf_directory]

    # Add the CCF directory as an argument
    command += ['-p{}'.format(cif_directory)]

    # Run the command using subprocess
    subprocess.run(command, check=True)

    # Update the ODF system variable
    command = ['export', 'SAS_ODF={}'.format(odf_directory)]
    subprocess.run(command, shell=True, check=True)