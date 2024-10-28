#!/bin/bash

pubget download --pmcids_file data/julios_nv_collection/nv_pmc_ids.txt \
    --alias nv_collection data/pubget_data

pubget extract_articles data/pubget_data/nv_collection/articlesets

pubget extract_data --articles_with_coords_only data/pubget_data/nv_collection/articles

pubget extract_labelbuddy_data data/pubget_data/nv_collection/subset_articlesWithCoords_extractedData