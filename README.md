# GDrive Folder Size Calculator & Mover

This script helps the UW Rec IT stay within 100 GB shared drive limit mandated by Google, as we switch over to SharePoint.


`main.py` is the main script: it accepts a file containing comma separated files to folders that need to be moved to Spare Drives. After calculating the optimal pairing of all subfolders so that no Shared Drive > 100GB, you are prompted to enter X number of spare Shared Drives needed to properly store all the folders specified in the original comma separated file.

`gdrive_calculator.py` is from the main repo but modified for our purposes, including the addition of the "parents" field in order to move a folder from its previous parent folder to its new parent folder. View the original repository this repo was forked from, to get instructions on how to start running this file (we need the required Google packages in order to access the GDrive API, and many other Python files in this project use `gdrive_calculator.py`)

`getFoldersSizesAll.py` was a helper script to sanity check that all folders in question have < 100GB size, and also with shared drives that are barely over the 100GB limit, find the optimal folder to move to help us get under the 100GB limit.

