# DeepFields.MasterCatalog
DeepFields.MasterCatalog

Compiling a master catalog for high-redshift galaxies in several famous (non-lensed) deep fields. 

We try to compile coordinate, redshift, photometry and derived mass properties as many as possible. A lot of works are still needed. Community efforts are super welcome. This shall benefit many galaxy evolution studies.

We store the meta info of each catalog as a "\*.ini" file under the `"data/catalog_meta_info/"` folder. The catalog data file path or TAP URL, column name conventions and other information are all defined therein. 

We have a BASH shell script "pipeline-make-deep-field-master-catalog" that calls each step of our master catalog creation, in a style like:
```
pipeline-make-deep-field-master-catalog 1 1 1
```
The three numbers are referred to as "Category", "Job", and "Task" numbers, respectively.
The Category number actually corresponds to the first-level sub-folder name in the "pipeline" directory. Then the Job number to the second-level sub-folder name therein. The third number, Task, means the script name under the path "pipeline/Category\*/Job\*/". 
We define such a relatively complex pipeline structure just for future extension perspective (following [D. Liu et al. 2019a, ApJS, 244, 40](https://ui.adsabs.harvard.edu/abs/2019ApJS..244...40L/abstract)). 

Currently the most important Job is just `"pipeline/1_constructing_master_catalog/2_constructing_master_catalog/"`. Scripts under that path that do not have a file name starting with number means auxiliary scripts. They shall not be directly called, but are used in the main task scripts. 

The Job before that should just be manually collecting catalog meta info and preparing the "\*.ini" files under the `"data/catalog_meta_info/"` folder. 



_Last update: 2022-03-03, Garching bei München._
