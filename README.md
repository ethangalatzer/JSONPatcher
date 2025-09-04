This project patches JSON files through other JSON files by adding, modifying or deleting.

Logic is in jsonpatcher.py, using json library to parse and click library for command line interfacing. 

All tests in testsuite.py, each function has one or more tests, and there is a full test that runs through the whole process, using testdata.json, testpatch1.json, and testpatch2.json.


To install:
  1. Download all files
  2. In command prompt, navigate into the main folder
  3. Run the following in command prompt:
     
       python -m venv venv
     
       venv\Scripts\activate
     
       python -m pip install -e .
     
To use:
  While in venv, patch a JSON file with the following command:
  
  jsonpatcher --input inputfile.json --patch patchfile.json --output outputfile.json
  
  For multiple patch files, repeat '--patch patchfile.json' for each file

To test:
  Navigate to the jsonpatcher folder and run testsuite.py
     
