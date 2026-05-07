Before applying the LayerLists in "Theme_LayerList_Sample.icmt", complete the following steps:
1. Download the "Basic Items" data from the GSI (Geospatial Information Authority of Japan) download service. 
2. Convert the coordinate system of the downloaded XML files to JGD2011 using the script "GSI_CONV_2024to2011.py". 
3. Using the software FDGV, export all required geographic features within the target area as SHP files. 
4. The exported SHP files include unnecessary prefixes (such as date information) in their filenames.
Use "GSI_remove_ShpPrefix9.py" to remove the first 9 characters from each filename. 
5. Create a folder named "BackGroundSHP" directly under the model’s local root working directory.
Save all renamed SHP files into this folder. 
6. Finally, apply the LayerList "GSI_MAP" in the InfoWorksICM model.
