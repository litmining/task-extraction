# extract abstracts from neurovault papers

import os
import csv
from typing import Dict, Optional
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define constants
MAP_FOLDER = "data/neurovault_labeled_papers/"
INDEX_FILE = MAP_FOLDER + "nv_labeled_tasks_pmcid_map.json"
TASK_FILE_PATTERN = MAP_FOLDER + "nv_labeled_tasks_{chunk_number}.json"
CHUNK_SIZE = 50
CSV_FILE = "data/neurovault_labeled_papers/pmid_collection_statisticmaps_text_subset.csv"
#ATLAS_TASKS = get_all_cognitive_atlas_tasks()
import csv
import sys
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)
from cognitiveatlas.api import get_task

def read_csv_data(csv_file: str, chunk_size: int = 1000, max_rows: Optional[int] = None) -> Dict[str, str]:
    """
    Read CSV data from file in chunks.

    Args:
        csv_file: Path to CSV file.
        chunk_size: Number of rows to read per chunk (default: 1000).
        max_rows: Maximum number of rows to read (default: None).
    Returns:
        Dictionary of CSV data keyed by PMID.
    """
    csv_data = {}
    # Reset file pointer to start
    file.seek(0)
    for chunk_idx in range(0, max_rows, chunk_size):
        with open(csv_file, 'r') as file:
            # Get header
            header = next(csv.reader(file))
        
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header again
            
            chunk = []
            total_rows = 0
            
        for i, row in enumerate(csv_reader):
            if max_rows and total_rows >= max_rows:
                break
                
            chunk.append(row)
            if len(chunk) >= chunk_size:
                # Process the chunk
                for row in chunk:
                    pmid, *fields = row
                    csv_data[pmid] = dict(zip(header, row))
                    total_rows += 1
                    if max_rows and total_rows >= max_rows:
                        break
                chunk = []  # Clear the chunk
                
        # Process any remaining rows in the last chunk
        for row in chunk:
            pmid, *fields = row
            csv_data[pmid] = dict(zip(header, row))
            total_rows += 1
            
        print(f"Processed {total_rows} rows in total")
    return csv_data

def read_csv_chunk(csv_file: str, chunk_size: int = 10, chunk_number: int = 1) -> Dict[str, str]:
    """
    Read specific chunk of CSV data from file.

    Args:
        csv_file: Path to CSV file.
        chunk_size: Number of rows per chunk (default: 1000).
        chunk_number: Which chunk to read (0-based index, default: 0).
    Returns:
        Dictionary of CSV data keyed by PMID.
    """
    csv_data = {}
    with open(csv_file, 'r') as file:
        # Get header
        header = next(csv.reader(file))
        
        # Skip to the desired chunk
        csv_reader = csv.reader(file)
        rows_to_skip = chunk_number * chunk_size
        for _ in range(rows_to_skip):
            try:
                next(csv_reader)
            except StopIteration:
                print(f"Warning: File has fewer than {rows_to_skip} rows")
                return csv_data

        # Read the desired chunk
        rows_read = 0
        while rows_read < chunk_size:
            try:
                row = next(csv_reader)
                pmid, *fields = row
                csv_data[pmid] = dict(zip(header, row))
                rows_read += 1
            except StopIteration:
                break

        print(f"Processed chunk {chunk_number} ({rows_read} rows)")
    return csv_data

from concurrent.futures import ThreadPoolExecutor, as_completed

def pmcid_map_file_add_index(index_file: str, pmcid: str, add_location: str):
    if not os.path.exists(index_file):
        with open(index_file, 'w') as file:
            json.dump({}, file)
    with open(index_file, 'r') as file:
        index_map = json.load(file)
        if pmcid not in list(index_map.keys()):
            index_map[pmcid] = [add_location]
        else:
            index_map[pmcid].append(add_location)
    with open(index_file, 'w') as file:
        json.dump(index_map, file)

def pmcid_map_file_get_index(index_file: str, pmcid: str):
    with open(index_file, 'r') as file:
        index_map = json.load(file)
        return index_map[pmcid]

def process_chunk(chunk_number: int, 
                  chunk_size: int = CHUNK_SIZE,
                  csv_file: str = CSV_FILE,
                  index_file: str = INDEX_FILE,
                  task_file_pattern: str = TASK_FILE_PATTERN):
    csv_data = read_csv_chunk(csv_file, chunk_size=chunk_size, chunk_number=chunk_number)
    nv_labeled_tasks = []
    key_list = ['id', 'name', 'definition_text']
    for k, v in csv_data.items():
        try:
            task_info = get_task(v["cognitive_paradigm_cogatlas_id"]).json
            print([task_info['id'], task_info['name'], task_info['definition_text']])
            task_info_dict = {key: task_info[key] if task_info[key] is not None else None for key in key_list}
            pmcid_map_file_add_index(index_file, k, task_file_pattern.format(chunk_number=chunk_number))
            output = {k: {'pmcid': k, 'task': task_info_dict, 'pmid': v['pmid'], 'doi': v['doi']}}
            nv_labeled_tasks.append(output)
        except Exception:
            pass
        
    # Export to JSON
    with open(task_file_pattern.format(chunk_number=chunk_number), 'w') as f:
        json.dump(nv_labeled_tasks, f)


if __name__ == "__main__":

    chunk_numbers = range(0, 23)
    # find max processors
    max_workers = os.cpu_count()-4

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_chunk, chunk_number): chunk_number for chunk_number in chunk_numbers}
        for future in as_completed(futures):
            chunk_number = futures[future]
            try:
                future.result()
                print(f"Chunk {chunk_number} processed successfully.")
            except Exception as e:
                print(f"Chunk {chunk_number} generated an exception: {e}")
    
    with open(INDEX_FILE, 'r+') as file:
        index_map = json.load(file)
        index_map = dict(sorted(index_map.items()))
        print(f"Total unique PMCIDs: {len(index_map.keys())}")
        file.seek(0)
        file.truncate()
        json.dump(index_map,file)
