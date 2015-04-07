#!/usr/bin/python

# import modules
import fileinput
import sys

# Open the annotation file to be read
Annotation_file = fileinput.input([sys.argv[1]])
# Open the mapping file to be read
Mapping_file = fileinput.input([sys.argv[2]])
# Create and open the result file
Result_file = open(sys.argv[3], "a")

# Variables, lists and dictionaries
EST_line_dict = {}
EST_dict = {}
EST_list = []
Temp_list = []
Temp_line = []
Final_list = []
Final_dict = {}
EST_temp_dict = {}
count_line = 0
       
# Iterate through each line in the annotation file, tab-delimit and select the key and value
for line in Annotation_file:
	
	Annotation_Line = line.split('\t')

	# Move to list and dictionary if annotation is found
	if Annotation_Line[3] != 'topnrEvalue' and Annotation_Line[3] != 'No_sig_nr_hit':
		
		NCBI_ID_entries = Annotation_Line[2].split('|')
		EST = Annotation_Line[0]
		NCBI_ID = NCBI_ID_entries[1]
		NCBI_eValue = Annotation_Line[3]
		Swiss_ID = Annotation_Line[6]
		Swiss_eValue = Annotation_Line[8]
		Temp_list = [EST, NCBI_ID, NCBI_eValue, Swiss_ID, Swiss_eValue]
		EST_dict[EST] = Temp_list
		EST_list.append(Temp_list)
	
		# Separate dict that holds the full line for printing
		EST_line_dict[EST] = line

	# Save header for print-out	
	elif Annotation_Line[0] == 'ContigName':
		Annotation_header = line
	
	Temp_list = list()

print "Finished making the EST dictionary"
            
# Iterate through each line in the mapping file, tab-delimit and clean up the EST entries for each tag
for line in Mapping_file:
	line = line.rstrip('\r\n')
	Mapping_Line = line.split('\t')
	EST_entries = Mapping_Line[32].split(';')
	
	# Print the header to the result file
	if Mapping_Line[0] == 'Tag':
		Mapping_header = line 
		Result_file.write(Mapping_header)
		Result_file.write('\t')
		Result_file.write(Annotation_header)
	
	# Iterate through the EST entries and search for hits in the EST dictionary, if found move to a new temp dictionary
	else:
		for item in EST_entries:
			if item in EST_dict:
				EST_temp_dict[item] = EST_dict[item]
		
		# Check if the EST_temp_dict contains any entries
		if len(EST_temp_dict) >= 1:
			
			# Write a newline between each tag-group and count the total number of tags with annotated EST's
			Result_file.write("\n")
			count_line += 1
			for item in EST_entries:
				if item in EST_dict:
					# Create a temporary list of lists containing the entries in the EST_temp_dict
					Temp_line = EST_dict[item]
					Temp_list.append(Temp_line)
		
		# Use this commented section for a print out of the results without collapsing to single entries
		#Final_list = Temp_list
		
		# Sort the Temp_list by NCBI's gi then e-value
		Temp_list = sorted(Temp_list, key=lambda item: (item[1], float(item[2])))
		
		# Collapse list to single entries with lowest e-value for each NCBI gi ID (ex '323434961')
		Identifier = 0
		Prev_identifier = 0
		for item in Temp_list:
			Identifier = item[1]
			if Identifier != Prev_identifier:
				Final_list.append(item)
			
			Prev_identifier = Identifier
		
		# Re-sort the Temp_list by e-value
		Final_list = sorted(Final_list, key=lambda item: float(item[2]))
		
		# Iterate over the keys in the final dict and write to file
		for item in Final_list:
			Result_file.write(line)
			Result_file.write('\t')
			Result_file.write(EST_line_dict[item[0]])
		
		# Clear lists for next line
		EST_temp_dict.clear()
		Final_list = list()
		Temp_line = list()	
		Temp_list = list()

print "Finished searching the mapping file against the EST dictionary"

# Close open files     
Annotation_file.close()
Mapping_file.close()
Result_file.close()

print "Total number of annotated tags", count_line
print "Script finished"
