#%% 
import json
import re
from typing import List
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Example
ann = json.load(open('./data/labelbuddy_annotations/nv_collection/annotations.json'))
#%%
class Article():
    def __init__(self, annotation: dict):
        
        #self.subheaders = get_subheaders(body)
        self.text = annotation['text']
        self.headers = self.get_headers()
        self.body = self.get_header_section('body')
        self.abstract = self.get_header_section('abstract')
        self.supplement = self.get_header_section('supplement')
        self.title = self.get_header_section('title')
        self.keywords = self.get_header_section('keywords')
        self.methods = self.get_methods()
        if self.methods == None:
            self.methods = "No explicit methods section"

    def get_headers(self) -> List:
        '''
        Extract the body text from an annotation dictionary.

        Returns:
            List[List[str, int, int]]: A list of lists containing the header text,
                                       start index, and end index.
        '''
        header_pattern = r"\n\# [A-Za-z ]+\n"
        headers = []
        for match in re.finditer(header_pattern, self.text):
            headers.append([match.group(), match.start()])
        for i in range(len(headers)-1):
            headers[i].append(headers[i+1][1]-1)
        headers[-1].append(len(self.text)-headers[-1][1])
        return headers
    def get_header_section(self, header_text: str) -> str:
        '''
        Extract the section of text that corresponds to a given header.
        header_text (str): The text of the header to extract the section from.
        ['title','keywords','abstract','body','supplemental']
        '''
        pattern = r"\n\# " + header_text
        for header in self.headers:
            if re.search(pattern, header[0].lower()):
                return self.text[header[1]:header[2]]
        return None
    
    def get_body(self) -> str:
        '''
        Extract the body section from the text.
        '''
        body_section = self.get_header_section('body')
        return body_section
    
    def get_subheaders(self, header_section: str) -> List[str]:
        '''
        Extract the subheaders from a section of text.
        '''
        subheader_pattern = r"\n\#\# [A-Za-z ]+\n"
        subheaders = []
        section = self.get_header_section(header_section)
        if not section:
            return None
        if section:
            if not re.search(subheader_pattern, section.lower()):
                print(f'No subheaders found in {header_section} section')
                return None
            for match in re.finditer(subheader_pattern, section.lower()):
                subheaders.append([match.group(), match.start()])
            for i in range(len(subheaders)-1):
                subheaders[i].append(subheaders[i+1][1]-1)
            subheaders[-1].append(len(section)-subheaders[-1][1])
            return subheaders
    
    def get_methods(self) -> str:
        '''
        Extract the methods section from the body text.
        '''
        methods_pattern = r"(material|method)"
        sections = ['body', 'supplement']
        for section in sections:
            if self.get_subheaders(section):
                subheaders = self.get_subheaders(section)
                section_text = self.get_header_section(section)
                for subheader in subheaders:
                    subheader_text = subheader[0].lower()
                    if re.search(methods_pattern, subheader_text):
                        methods = section_text[subheader[1]:subheader[2]]
                        return methods
            else: continue
        return None

# Example 1: No explicit methods section
article = Article(ann[0])
print(article.methods)

# Example 2: Explicit methods section
article = Article(ann[1])
print(article.methods)

# Example 3: Abstract
print(article.abstract)
#%%
# Get labels and annotated text from annotation.json
def extract_annotated_text(full_text, start_char, end_char):
    """
    Extract a substring from full_text based on start and end character indices.

    Args:
        full_text (str): The complete text to extract from.
        start_char (int): Starting index of the substring.
        end_char (int): Ending index of the substring.

    Returns:
        str: The extracted substring.
    """
    return full_text[start_char:end_char]

def get_labels_and_annotated_text(annotation:dict)->dict:
    '''
    Extract the labels and annotated text from an annotation.json file.
    
    Returns a dictionary with the following keys:
    {
        "pmcid": <str>,
        "pmid": <str>,
        "doi": <str>,
        "batch": <int>,
        "annotations": {
            "label_name <str>": [annotated_text <str>]
        }
    }
    '''
    pmcid = annotation['metadata']['pmcid']
    pmid = annotation['metadata']['pmid']
    doi = annotation['metadata']['doi']
    batch = annotation['metadata']['batch']
    full_text = annotation['text']
    output = {"pmcid":pmcid, "pmid":pmid, "doi":doi, "batch":batch, "annotations":{}}
    for ann in annotation['annotations']:
        extracted_text = extract_annotated_text(full_text, ann['start_char'], ann['end_char'])
        label_name = ann['label_name']
        if label_name not in output['annotations']:
            output['annotations'][label_name] = [extracted_text]
        else:
            output['annotations'][label_name].append(extracted_text)
    return output

# Example:
labels = get_labels_and_annotated_text(ann[0])
print(labels)
#%%