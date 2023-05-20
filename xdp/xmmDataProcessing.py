# processing.py
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
from astroquery.esa.xmm_newton import XMMNewton
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

def run_emchain(odf_directory, em_directory):
    """
    Run the emchain command on the specified ODF directory and EM directory, and update the EM system variable.

    Parameters:
    -----------
    odf_directory : str
        The path to the directory containing the ODF files to be processed.
    em_directory : str
        The path to the directory where the EM files will be saved.
    """

    # Set up the command to run emchain
    command = ['emchain', 'odfdir={}'.format(odf_directory), 'outdir={}'.format(em_directory)]

    # Run the command using subprocess
    subprocess.run(command, check=True)

    # Update the EM system variable
    command = ['export', 'SAS_ODF={}'.format(em_directory)]
    subprocess.run(command, shell=True, check=True)
    
def run_epchain(odf_directory, ep_directory, oot=True):
    """
    Run the epchain command on the specified ODF directory and EP directory, and update the EP system variable.

    Parameters:
    -----------
    odf_directory : str
        The path to the directory containing the ODF files to be processed.
    ep_directory : str
        The path to the directory where the EP files will be saved.
    oot : bool, optional
        Whether or not to run the out-of-time (OOT) correction (default is True).
    """

    # Set up the command to run epchain
    command = ['epchain', 'pnimage=yes', 'pnspec=yes', 'pntrailla=yes', 'pntraillae=yes', 'odfdir={}'.format(odf_directory), 'outdir={}'.format(ep_directory)]

    # Add the OOT argument if required
    if oot:
        command += ['ootcorr=yes']

    # Run the command using subprocess
    subprocess.run(command, check=True)

    # Update the EP system variable
    command = ['export', 'SAS_ODF={}'.format(ep_directory)]
    subprocess.run(command, shell=True, check=True)

def create_good_time_intervals(observation_id, odf_directory, gtis_directory, event_file, expression, gtiset_name='gti'):
    """
    Create a good time intervals file for an XMM-Newton observation.

    Parameters:
    -----------
    observation_id : str
        The ID of the XMM-Newton observation.
    odf_directory : str
        The path to the directory containing the ODFs for the observation.
    gtis_directory : str
        The path to the directory where the GTI file will be saved.
    event_file : str
        The name of the event file to use for the GTI creation.
    expression : str
        The expression to use for the GTI creation.
    gtiset_name : str, optional
        The name of the GTI set to create (default is 'gti').
    """
    # Create binned photon counts over observation time
    command = ['eveselect', 'table={}'.format(event_file), 'withrateset=yes', 'rateset={}/rate'.format(gtis_directory), 'maketimecolumn=yes', 'makeratecolumn=yes', 'timebinsize=50']

    # Run the command using subprocess

    subprocess.run(command, cwd=odf_directory, check=True)  

    # Carry out three sigma clipping on the binned photon counts
    command = ['tabgtigen', 'table={}/rate'.format(gtis_directory), 'gtiset={}/{}'.format(gtis_directory, gtiset_name), 'sigma=3']

    # Set up the command to run evselect
    command = ['evselect', 'table={}'.format(event_file), 'withfilteredset=yes', 'expression={}'.format(expression), 'filteredset={}/{}'.format(gtis_directory, gtiset_name)]

    # Run the command using subprocess
    subprocess.run(command, cwd=odf_directory, check=True)

def create_mos_images(observation_id, odf_directory, images_directory, event_file, expression, image_name='image', imageset_name='imageset'):
    """
    Create MOS images for an XMM-Newton observation.

    Parameters:
    -----------
    observation_id : str
        The ID of the XMM-Newton observation.
    odf_directory : str
        The path to the directory containing the ODFs for the observation.
    images_directory : str
        The path to the directory where the images will be saved.
    event_file : str
        The name of the event file to use for the image creation.
    expression : str
        The expression to use for the image creation.
    image_name : str, optional
        The name of the image to create (default is 'image').
    imageset_name : str, optional
        The name of the image set to create (default is 'imageset').
    """

    # Set up the command to run evselect
    command = ['evselect', 'table={}'.format(event_file), 'withimageset=yes', 'imageset={}/{}'.format(images_directory, imageset_name), 'xcolumn=X', 'ycolumn=Y', 'imagebinning=imageSize', 'ximagebinsize=80', 'yimagebinsize=80', 'expression={}'.format(expression)]

    # Run the command using subprocess
    subprocess.run(command, cwd=odf_directory, check=True)

    # Set up the command to run evselect
    command = ['evselect', 'table={}'.format(event_file), 'withimageset=yes', 'imageset={}/{}'.format(images_directory, image_name), 'xcolumn=X', 'ycolumn=Y', 'imagebinning=imageSize', 'ximagebinsize=80', 'yimagebinsize=80', 'expression={}'.format(expression)]

    # Run the command using subprocess
    subprocess.run(command, cwd=odf_directory, check=True)

def create_pn_images(observation_id, odf_directory, images_directory, event_file, expression, image_name='image', imageset_name='imageset', oot_image_name='oot_image', oot_imageset_name='oot_imageset', oot_flag=False):
    """
    Create PN images for an XMM-Newton observation.

    Parameters:
    -----------
    observation_id : str
        The ID of the XMM-Newton observation.
    odf_directory : str
        The path to the directory containing the ODFs for the observation.
    images_directory : str
        The path to the directory where the images will be saved.
    event_file : str
        The name of the event file to use for the image creation.
    expression : str
        The expression to use for the image creation.
    image_name : str, optional
        The name of the image to create (default is 'image').
    imageset_name : str, optional
        The name of the image set to create (default is 'imageset').
    """

    # Set up the command to run evselect
    command = ['evselect', 'table={}'.format(event_file), 'withimageset=yes', 'imageset={}/{}'.format(images_directory, imageset_name), 'xcolumn=X', 'ycolumn=Y', 'imagebinning=imageSize', 'ximagebinsize=40', 'yimagebinsize=40', 'expression={}'.format(expression)]

    # Run the command using subprocess
    subprocess.run(command, cwd=odf_directory, check=True)

    # Set up the command to run evselect
    command = ['evselect', 'table={}'.format(event_file), 'withimageset=yes', 'imageset={}/{}'.format(images_directory, image_name), 'xcolumn=X', 'ycolumn=Y', 'imagebinning=imageSize', 'ximagebinsize=40', 'yimagebinsize=40', 'expression={}'.format(expression)]

    # Run the command using subprocess
    subprocess.run(command, cwd=odf_directory, check=True)

    if oot_flag:
        # Create OOT images
        # Set up the command to run evselect
        command = ['evselect', 'table={}'.format(event_file), 'withimageset=yes', 'imageset={}/{}'.format(images_directory, oot_imageset_name), 'xcolumn=X', 'ycolumn=Y', 'imagebinning=imageSize', 'ximagebinsize=40', 'yimagebinsize=40', 'expression=FLAG==0']

        # Subtract the OOT image from the main image
        farith_command = f"farith", "{}/{}".format(images_directory, oot_imageset_name), "0.063 PN_OoT_image_rescaled.fits MUL"
        # Run the command using subprocess
        subprocess.run(farith_command, cwd=odf_directory, check=True)

        farith_command = f"farith", '{}/{}'.format(images_directory, oot_imageset_name), "PN_OoT_image_rescaled image_ot_sub.fits SUB"
        # Run the command using subprocess
        subprocess.run(farith_command, cwd=odf_directory, check=True)

#def create_spectra(observation_id, odf_directory, spectra_directory, event_file, expression, spectrum_name='spectrum', spectrumset_name='spectrumset'):