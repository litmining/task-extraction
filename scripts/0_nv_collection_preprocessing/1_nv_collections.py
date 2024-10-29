# %%
# show the first 5 rows of the nv_collections.csv file
import pandas as pd
import os
os.chdir("../")
print(os.getcwd())

# %%

# %%
# show the first 5 rows of the nv_collections_images.csv file
df_images = pd.read_csv('data/julios_nv_collection/nv_collections_images.csv')
print(df_images.head())
# remove rows where collection_id is null
df_images = df_images[df_images['collection_id'].notna()]
# export as json
df_images.to_json('data/julios_nv_collection/nv_collections_images.json', orient='records')


# %%
# import nv_pmc_ids.txt as a list of int
nv_pmc_ids = [int(line.strip()) for line in open('data/julios_nv_collection/nv_pmc_ids.txt', 'r')]


# remove rows where pmcid is null
df_images = df_images[df_images['pmcid'].notna()]
#convert df_images['pmcid'] to int
df_images['pmcid'] = df_images['pmcid'].astype(int)

# return the row from the df_images dataframe where the pmcid is equal to the value in the nv_pmc_ids list
subset_df_images = df_images[df_images['pmcid'].isin(nv_pmc_ids)]

# export as json
subset_df_images.to_json('data/julios_nv_collection/nv_collections_images_subset.json', orient='records')


# %%
