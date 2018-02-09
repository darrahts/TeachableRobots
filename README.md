# TeachableRobots
This is a working repo, while we strive to do our best to ensure the code and instructions available here are 100% operational, there are times when this will not be the case.  Thank you for your patience!

- ensure the teachablerobots folder is in your PYTHONPATH variable.
  -- open a terminal
  -- type "sudo nano ~/.bashrc" (without quotes)
  -- at the end of the file add:
       PYTHONPATH="${PYTHONPATH}:[absolute-path-to-teachablerobotsParentFolder/]"
  -- save the file
  -- in the terminal type "source ~/.bashrc" (without quotes)
  -- DONE! :)

- Nearly all of the scripts in the scripts folder need their imports fixed in the following form:
  -- old version: "from Communicate import *"
  -- new version: "from teachablerobots.src.Communicate import *"
  -- same format with any other robot classes
