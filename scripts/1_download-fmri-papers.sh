#!/bin/bash

pubget run --query "( fMRI[Abstract] OR functional MRI[Abstract] OR functional magnetic resonance imaging[Abstract] ) AND human NOT (meta-analy*[Abstract] OR meta analy*[abstract])"     \
    --vectorize_text \
    --vocabulary_file data/1_output_vocab.txt \
    --n_jobs 4                     \
    --alias fmri-papers\
    ~/data/pubget_data

pubget extract_labelbuddy_data pubget_data/fmri-papers/subset_allArticles_extractedData