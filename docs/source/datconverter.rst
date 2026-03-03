Using the cuddle dat converter at Diamond B07
==================================================


To run the converter simply open up a new terminal, and load the cuddle module

.. code-block:: bash

        module load cuddle


Then use the following command options to start converting nexus files


   * (optional) -out   -the path to the output folder, which will default to the experiment directory if no output path is given
   * (optional) -sl   - a list of scan numbers to be included in the sample log
   * (optional) -sr   - a range of scan number to be included in the sample log in the format [start,stop,step]

 examples of valid commands are:

.. code-block:: python
    
    #to convert files in /dls/b07/data/2025/si43348-1 and save output to same folder you do not need to include an output path
    cuddle /dls/b07/data/2025/si43348-1  
    
    #to convert files in /dls/b07/data/2025/si43348-1 and save output to home documents include the output path value
    cuddle /dls/b07/data/2025/si43348-1 -out /home/rpy65944/Documents

    #to only select scans 123 and 456
    cuddle /dls/b07/data/2025/si43348-1 -sl 123 456

    #to select scans 120 to 130
    cuddle /dls/b07/data/2025/si43348-1 -sr [120,130,1]