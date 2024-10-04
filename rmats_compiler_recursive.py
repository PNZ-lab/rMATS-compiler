#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


Description = '''
This script takes as input a directory and combines all the *.MATS.JCEC.txt files found into one file per subdirectory with *.MATS.JCEC.txt files.

EXAMPLE:
	For the input directory "/my/dir/" with the following files:
		/my/dir/healthy_v_drug1/SE.MATS.JCEC.txt
		/my/dir/healthy_v_drug1/RI.MATS.JCEC.txt
		/my/dir/healthy_v_drug1/MXE.MATS.JCEC.txt
		/my/dir/healthy_v_drug1/A3SS.MATS.JCEC.txt
		/my/dir/healthy_v_drug1/A5SS.MATS.JCEC.txt
		/my/dir/healthy_v_drug2/SE.MATS.JCEC.txt
		/my/dir/healthy_v_drug2/RI.MATS.JCEC.txt
		/my/dir/healthy_v_drug2/MXE.MATS.JCEC.txt
		/my/dir/healthy_v_drug2/A3SS.MATS.JCEC.txt
		/my/dir/healthy_v_drug2/A5SS.MATS.JCEC.txt
	Two files will be generated:
		/my/dir/healthy_v_drug1_rMATS_compiled.tsv
		/my/dir/healthy_v_drug2_rMATS_compiled.tsv

FUNCTION:
	You provide it with the folder that contains all *MATS.JCEC.txt files, it then:
		1) Finds these files
		2) Combines them using pandas' concatenate function
		3) Adds a column that specifies the event type (SE, MXE, RI, A3/5SS)
		4) Writes a tsv file for the combined splicing data in the input directory (or a specified directory [-out PATH])
	Optionally, the script can decrease the size of the output tsv file by:
		5) Excluding the majority of columns that aren't common across all event types [-simple]
		  i) Columns removed with -simple:
			riExonStart_0base, riExonEnd, ID.1, IJC_SAMPLE_1, SJC_SAMPLE_1, IJC_SAMPLE_2, SJC_SAMPLE_2, longExonStart_0base, longExonEnd, shortES, shortEE, flankingES, flankingEE, 1stExonStart_0base, 1stExonEnd, 2ndExonStart_0base, 2ndExonEnd
		  ii) Columns retained with -simple:
			ID, GeneID, geneSymbol, chr, strand, upstreamES, upstreamEE, downstreamES, downstreamEE, IncFormLen, SkipFormLen, PValue, FDR, IncLevel1, IncLevel2, IncLevelDifference, Splicing Event, exonStart_0base, exonEnd
		6) Excluding events where the IncLevelDifference falls below a given value [-PSI FLOAT]
		7) Excluding events where the FDR is above a given value [-FDR FLOAT]

USAGE:
	python /path/to/this/script /full/path/to/rmats/directory [-out /full/path/to/output/directory] [-simple] [-PSI FLOAT] [-FDR FLOAT]

	You can run this script from the login node on the HPC. Just load pandas first:
		module load pandas

'''

import argparse
import os
import pandas as pd

parser = argparse.ArgumentParser(description=Description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('rmats_dir_path', help='Insert the full path to the rmats _analysis folder')
parser.add_argument('-out', '--out_file_dir', help='Insert the full path to the output directory', default='')
parser.add_argument('-PSI', '--PSI_diff_threshold', help='Provide the threshold of inclusion for PSI values', default=0)
parser.add_argument('-FDR', '--FDR_diff_threshold', help='Provide the threshold of inclusion for FDR values', default=1)
parser.add_argument('-simple', '--simplify', help='Keeps only the most informative columns to save on file size', action='store_true')

args	  = parser.parse_args()
rmats_dir = args.rmats_dir_path
out_file_dir  = args.out_file_dir
simple	= args.simplify
PSI_diff_threshold = float(args.PSI_diff_threshold)
FDR_threshold = float(args.FDR_diff_threshold)

rmats_dir = os.path.abspath(rmats_dir)
out_file_dir  = os.path.abspath(out_file_dir)

if out_file_dir == '':
	out_file_dir = rmats_dir
	print('No output file directory provided. Defaulting to: %s' %(rmats_dir))

#%% if the -simple parameter is given, output only these columns:
simpl_cols = [
	"ID",
	"GeneID",
	"geneSymbol",
	"chr",
	"strand",
	# "riExonStart_0base",
	# "riExonEnd",
	"upstreamES",
	"upstreamEE",
	"downstreamES",
	"downstreamEE",
	# "ID.1",
	# "IJC_SAMPLE_1",
	# "SJC_SAMPLE_1",
	# "IJC_SAMPLE_2",
	# "SJC_SAMPLE_2",
	"IncFormLen",
	"SkipFormLen",
	"PValue",
	"FDR",
	"IncLevel1",
	"IncLevel2",
	"IncLevelDifference",
	"Splicing Event",
	# "longExonStart_0base",
	# "longExonEnd",
	# "shortES",
	# "shortEE",
	# "flankingES",
	# "flankingEE",
	"exonStart_0base",
	"exonEnd"
	# "1stExonStart_0base",
	# "1stExonEnd",
	# "2ndExonStart_0base",
	# "2ndExonEnd"
	]

#%%


print()
print('--- rmats_compiler.py starting ---')
print()




print()
print('Settings:')
print('input directory       = %s' %(rmats_dir))
print('output file directory = %s' %(out_file_dir))
print('simple output         = %s' %(simple))
print('FDR_threshold        = %f' %(FDR_threshold))
print('PSI_diff_threshold    = %f' %(PSI_diff_threshold))



print()
print('Searching folder : %s for *MATS.JCEC.txt files...' %(rmats_dir))

JCEC_locations_dict = {} # Contains paths to all JCEC files with roots as the key. This enables running the script for multiple conditions

for root, dirs, files in os.walk(rmats_dir):
	for file in files:
		if 'MATS.JCEC.txt' in file:
			file_path = os.path.join(root, file)
			#print('\tFound : %s' %(file_path))
			if root not in JCEC_locations_dict:
				JCEC_locations_dict[root] = [file_path]
			else:
				JCEC_locations_dict[root].append(file_path)

#%%
no_directories = len(JCEC_locations_dict)
no_files       = sum(len(value) for value in JCEC_locations_dict.values())
print('Found %i files in %i directories:' %(no_files, no_directories))
for rMATS_analysis in JCEC_locations_dict:
	print('\t%s:' %(rMATS_analysis))
	for file_path in JCEC_locations_dict[rMATS_analysis]:
		print('\t\t%s' %(os.path.basename(file_path)))


#%%

def JCEC_compiler(key, list_of_JCEC_paths):
	print('\nCombining dataframes in subdirectory: %s' %(os.path.basename(key)))
	JCEC_dfs = [] #The file paths converted to dataframes - now with a column for event type
	for file_path in list_of_JCEC_paths:
		basename = os.path.basename(file_path)
		as_event = basename.split('.MATS.JCEC.txt')[0]
		file_df  = pd.read_csv(file_path, sep='\t')
		file_df['Splicing Event'] = as_event #Add event type as a column to dataframe
		file_df.reset_index(drop=True)
		JCEC_dfs.append(file_df)

	print("\tConcatenating dataframes with pandas for dir %s:" %(key))
	#print("\t\t%s" %(key))


	df_concat = pd.concat(JCEC_dfs)


	#Finding original dimensions :
	rows_orig, columns_orig = df_concat.shape
	dataset_size = rows_orig*columns_orig
	print('\tSize of concatenated dataset : %i (%i*%i)' %(dataset_size, rows_orig, columns_orig))

	if simple:
		df_concat = df_concat[simpl_cols]

	df_concat['IncLevelDifference'] = pd.to_numeric(df_concat['IncLevelDifference'], errors='coerce')
	df_concat['FDR'] = pd.to_numeric(df_concat['FDR'], errors='coerce')

	FDR_to_remove = (df_concat['FDR'] > FDR_threshold).sum() # The number of cells that fail to clear our FDR threshold
	PSI_to_remove  = (abs(df_concat['IncLevelDifference']) < PSI_diff_threshold).sum()


	print('\tremoved based on FDR_threshold : %i' %(FDR_to_remove))
	print('\tremoved based on PSI_threshold  : %i' %(PSI_to_remove))

	df_concat_PSI = df_concat[abs(df_concat['IncLevelDifference']) >= PSI_diff_threshold]
	df_concat_PSI_FDR = df_concat_PSI[abs(df_concat_PSI['FDR']) <= FDR_threshold]

	if simple or PSI_diff_threshold != 0 or FDR_threshold != 0:
		rows_new, columns_new = df_concat_PSI_FDR.shape
		dataset_size_new = rows_new*columns_new
		dataset_size_new_perc = dataset_size_new/dataset_size*100
		print('\tSize of simplified and/or PSI/FDR-filtered dataset : %i (%i*%i) - %.2f%% of original' %(dataset_size_new, rows_new, columns_new, dataset_size_new_perc))


	folder_name = os.path.basename(key)
	file_suffix = '_rMATS_compiled.tsv'
	file_basename = folder_name + file_suffix
	out_file_path = os.path.join(out_file_dir, file_basename)
	print('Writing combined dataframe to : %s' %(out_file_path))
	df_concat_PSI_FDR.to_csv(out_file_path, sep='\t')

	print()




for rMATS_analysis in JCEC_locations_dict:
	JCEC_compiler(rMATS_analysis, JCEC_locations_dict[rMATS_analysis])

#%%
if no_files%5 != 0:
	print('>>>WARNING: Number of files not divisible by 5. Are all event types present?')

print('--- rmats_compiler_recursive.py finished ---')
print()
