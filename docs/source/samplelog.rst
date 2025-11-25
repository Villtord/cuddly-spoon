Creating a sample log file
==============================


There is now a create_log command to parse all .nxs files in a directory, and export details to a .csv log file. Currently the default columns in the sample log file are:
['Scan_type','datetime','E_start', 'E_end', 'Endstation','X','Y','Z','Rot','Slits']

.. code-block:: bash

        module load cuddle/dev

The inputs needed for the command are as follows:



   * -dir -  the path to the experiment directory
   * (optional) -out   -the path to the output folder, which will default to the experiment directory if no output path is given 

two examples of valid commands are:

.. code-block:: python
    
    #to save output to /dls/b07/data/2025/si43348-1 do not include an output path
    create_log -dir /dls/b07/data/2025/si43348-1  
    
    #to save output to home documents include the output path value
    create_log -dir /dls/b07/data/2025/si43348-1 -out /home/rpy65944/Documents


this start processing showing a progress bar, and then give an output like this

.. code-block:: bash

    Processing |################################| 134/134

    WARNING: 54 files were found to have scan_types not implemented in the log creator

    saved sample log to :  /home/rpy65944/Documents/si43348-1_sample_log.csv

if a scan_type has not yet been implemented in the log creator, it will fill the column values with 'Not implemented'



viewing a sample log file
--------------------------

once the log file is created you can view it in multiple ways. 


* simply opening in excel/libre office

make sure the cuddle module is loaded, and use the view_log command to open the file in libreoffice. This is in the format view_log <logfile_path>

.. code-block:: bash

    module load cuddle/dev
    view_log /home/rpy65944/Documents/si43348-1_sample_log.csv

* search the log for a specific value

make sure the cuddle module is loaded, and use the search_log command using the format  search_log <logfile_path> <search_string>  

Note that this is only a simple string matching function, so cannot accept complex filtering arguments.

.. code-block:: bash

    module load cuddle/dev
    search_log /home/rpy65944/Documents/si43348-1_sample_log.csv  12299

this will print to the terminal all lines which contain the search string e.g. 

.. code-block:: bash

    (python3.10) [rpy65944@ws583 ~]$ search_log /home/rpy65944/Documents/si43348-1_sample_log.csv 12299
    b07-122990  dummy_a 2025-10-15 06:10:31 Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented
    b07-122991  dummy_a 2025-10-15 07:50:35 Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented
    b07-122992  pgm_energy  2025-10-15 07:54:30 282.0   297.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122993  pgm_energy  2025-10-15 07:58:32 282.0   297.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122994  pgm_energy  2025-10-15 08:02:13 282.0   297.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122995  pgm_energy  2025-10-15 08:07:50 525.0   565.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122996  pgm_energy  2025-10-15 08:15:45 845.0   920.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122997  dummy_a 2025-10-15 08:27:18 Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented
    b07-122998  pgm_energy  2025-10-15 08:50:19 845.0   920.0   1   sm21b_x: -0.8708    sm21b_y: -2.054 sm21b_z: 9.969  N/A s4b_ygapsize : 0.025
    b07-122999  dummy_a 2025-10-15 08:56:46 Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented Not implemented