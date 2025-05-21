

# rMATS_compiler/py

This script takes as input a directory and combines all the *.MATS.JCEC.txt files found into one file per subdirectory with *.MATS.JCEC.txt files.

## EXAMPLE:
For the input directory `/my/dir/` with the following files: <br>

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

Example output:
<img width="1318" alt="image" src="https://github.com/user-attachments/assets/65709bdf-1279-445c-ad25-9145cc299412">


## FUNCTION:
You provide it with the folder that contains all *MATS.JCEC.txt files, it then:
1. Finds these files
2. Combines them using pandas' concatenate function
3. Adds a column that specifies the event type (SE, MXE, RI, A3/5SS)
4. Writes a tsv file for the combined splicing data in the input directory (or a specified directory [-out PATH])
<br>
Optionally, the script can decrease the size of the output tsv file by: <br>

5. Excluding the majority of columns that aren't common across all event types [-simple]

	1. Columns removed with -simple:
			riExonStart_0base, riExonEnd, ID.1, IJC_SAMPLE_1, SJC_SAMPLE_1, IJC_SAMPLE_2, SJC_SAMPLE_2, longExonStart_0base, longExonEnd, shortES, shortEE, flankingES, flankingEE, 1stExonStart_0base, 1stExonEnd, 2ndExonStart_0base, 2ndExonEnd
	2. Columns retained with -simple:
			ID, GeneID, geneSymbol, chr, strand, upstreamES, upstreamEE, downstreamES, downstreamEE, IncFormLen, SkipFormLen, PValue, FDR, IncLevel1, IncLevel2, IncLevelDifference, Splicing Event, exonStart_0base, exonEnd
6. Excluding events where the IncLevelDifference falls below a given value [-PSI FLOAT]
7. Excluding events where the FDR is above a given value [-FDR FLOAT]

## USAGE:
    python /path/to/this/script /full/path/to/rmats/directory [-out /full/path/to/output/directory] [-simple] [-PSI FLOAT] [-FDR FLOAT]

### Running script on the HPC
You can run this script from the login node on the HPC. Just load pandas first. Exactly how this is done can change with the dynamic data structure on the HPC. As of 2025-05-21, this command works:

    module load SciPy-bundle/2024.05-gfbf-2024a

For a more generic, long-term solution. See a list of available python modules with:

    module spider pandas

Then get more info on one of the listed options, e.g.:

    module spider pandas/2.2.2

Then load an option from the resulting list, e.g.:

    module load SciPy-bundle/2024.05-gfbf-2024a
