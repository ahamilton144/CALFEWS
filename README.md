**Note: This is a fork associated with the two papers below. If you are interested in using the CALFEWS model more generally, please refer to the original repository, https://github.com/hbz5000/CALFEWS.**

First, you can find code and instructions for producing the analysis for the following paper on the **"FKC_experiment_longleaf" branch**. 

Hamilton, A.L., Zeff, H.B., Characklis, G.W., & P.M. Reed. (2022). Resilient California water portfolios require infrastructure investment partnerships that are viable for all partners. *Earth's Future, 10*(4), e2021EF002573. [https://doi.org/10.1029/2021EF002573](https://doi.org/10.1029/2021EF002573).

Second, you can find code and instructions for producing the analysis for the following paper on the **"MORDM_experiment_paper1" branch**. 

Hamilton, A.L.,  Reed, P.M., Gupta, R.S., Zeff, H.B., Characklis, G.W., & (2023). Resilient water infrastructure partnerships in institutionally complex systems face challenging supply and financial risk tradeoffs. *(In review)*.

# California Food-Energy-Water System (CALFEWS)

This repository contains all code and data for the California Food-Energy-Water System (CALFEWS), an open-sourced, Python/Cython-based model for simulating the integrated, multi-sector dynamics of water supply in the Central Valley of California.  CALFEWS captures system dynamics across multiple scales, from coordinated management of inter-basin water supply projects at the state and regional scale, to agent-based representation of conjunctive surface water and groundwater supplies at the scale of irrigation and water storage districts. Its flexible, adaptive, rules-based representation allows CALFEWS to explore alternative climate, infrastructure, and regulation scenarios, and it is also interoperable with power dispatch and agricultural production models. This tool can provide decision-makers and analysts with a platform to generate a wide range of internally consistent scenarios for the integrated management of water supply, energy generation, and food production.

More information on the CALFEWS model, and comparison of model output to historical data, can be found in the following manuscript:

Zeff, H.B., Hamilton, A.L., Malek, K., Herman, J.D., Cohen, J.S., Medellin-Azuara, J., Reed, P.M., and G.W. Characklis. (2021). California's Food-Energy-Water System: An Open Source Simulation Model of Adaptive Surface and Groundwater Management in the Central Valley. *Environmental Modelling & Software, 141*: 105052. [https://doi.org/10.1016/j.envsoft.2021.105052](https://doi.org/10.1016/j.envsoft.2021.105052) 

Download the exact version used to produce the paper at [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4091708.svg)](https://doi.org/10.5281/zenodo.4091708).

Licensed under the MIT License, 2017.

## Installation and setup
1. Clone this repository to your local machine.
1. If you use Anaconda:
    1. Create a new environment using the yml file: ``conda env create -f environment.yml``
    1. Activate environment: ``conda activate .venv_conda_calfews``
1. If you don't use Anaconda:
    1. Manually install the packages listed in ``environment.yml`` into a new virtual environment named ``.venv_conda_calfews``, and activate the environment.
1. From the base CALFEWS directory, run model with ``python -W ignore run_main_cy.py <results_folder>``, where ``<results_folder>`` is the location you would like to store the results, relative to base directory. (Note: the command for Python 3 may be python3, not python, depending on your machine).
1. If this doesn't work (or you want to make any changes to source files), you will need to recreate the C files & binaries from Cython. 
    1. If you are running on Linux or MacOS, you should already have gcc installed. If you are running on Windows, you will need to install Visual Studio 2019 Community Edition. When it asks which programs to install, choose "Desktop development with C++".
    1. Cythonize and recompile with the command: ``python setup_cy.py build_ext --inplace``.
1. Three different Jupyter notebooks are available to improve usability. To use them, you will need to run the following commands in the terminal or Anaconda Prompt.
    1. Add your virtual environment to Jupyter: ``python -m ipykernel install --user --name=.venv_conda_calfews``
    1. Tell Jupyter to allow ipywidgets: ``jupyter nbextension enable --py widgetsnbextension`` (this step may or may not be necessary depending on your Jupyter version)
    1. Tell Jupyter to allow bqplot: ``jupyter nbextension enable --py bqplot``
1. The three helper notebooks are:
    1. ``CALFEWS_GUI.ipynb``: This graphical user interface (GUI) allows the user to run different inflow scenarios and visualize results interactively (run the notebook and scroll down to the bottom for the GUI.
    1. ``CALFEWS_intro_tutorial.ipynb``: This notebook gives more details on model parameters, input files, and output files, for users who want to go deeper than the GUI.
    1. ``modeling_paper_notebook.ipynb``: This notebook can be run to automatically run run all simulations and reproduce all figures from Zeff et al. 2020 (see citation above).
