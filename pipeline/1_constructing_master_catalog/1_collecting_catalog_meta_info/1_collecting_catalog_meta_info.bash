#!/bin/bash
# 
#set -e
echo "Please manually collect catalog meta info and store them into the \"data/catalog_meta_info/\" directory of this repository."
echo ""

sleep 5
echo "Below we list the files which are already in that directory:"
repo_dir=$(dirname $(dirname $(dirname $(dirname $(perl -MCwd -e 'print Cwd::abs_path shift' "${BASH_SOURCE[0]}")))))
current_dir=$(pwd)
echo cd $repo_dir/data/catalog_meta_info/
cd $repo_dir/data/catalog_meta_info/
echo ls -1l *.ini
ls -1l *.ini

cd $current_dir
