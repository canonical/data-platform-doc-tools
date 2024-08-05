import dataclasses
import pathlib

import requests
import yaml
import re

NAVTABLE_START_MARKER = "[details=Navigation]"
NAVTABLE_END_MARKER = "[/details]"

DOCS_PATH = pathlib.Path("docs/")

DIATAXIS_DICT = {"t-": "tutorial", "h-": "how-to", "r-": "reference", "e-": "explanation"}

@dataclasses.dataclass
class Topic:
    path: pathlib.Path
    id: str  

def get_raw_markdown(topic_id: str):
    """
    Returns the raw markdown content of a discourse.charmhub.io topic given its unique ID
    """
    response = requests.get(f"https://discourse.charmhub.io/raw/{topic_id}/1")  # "/1" for post 1
    response.raise_for_status()

    return response.text

def parse_navtable(overview_topic_raw: str):
    """
    Parses the navtable of an overview topic and returns a structured list

    Args:
        overview_topic_raw (str): The raw markdown of the overview topic

    Raises:
        Exception: Navtable start marker was not found
        Exception: Navtable end marker was not found

    Returns:
        list: List of dictionaries where the keys are the columns of the navtable: 'Level', 'Path', 'Navlink'.
    """
    start_index = overview_topic_raw.find(NAVTABLE_START_MARKER)
    if start_index == -1:
        raise Exception("Could not find Navtable start marker " + NAVTABLE_START_MARKER + " in the overview topic") 

    end_index = overview_topic_raw.find(NAVTABLE_END_MARKER)
    if end_index == -1:
        raise Exception("Could not find Navtable end marker " + NAVTABLE_END_MARKER + " in the overview topic")

    start_index += len(NAVTABLE_START_MARKER)
    end_index = overview_topic_raw.find(NAVTABLE_END_MARKER, start_index)

    table_raw = overview_topic_raw[start_index:end_index].strip().split('\n') # remove whitespace and split by newline
    
    table_parsed = []
    column_labels = []
    for row_index,row_contents in enumerate(table_raw):
        if row_index==0:
            column_labels=[i.strip() for i in row_contents.split('|')]
        elif row_index==1: continue
        else:
            row_dict = {column_labels[i]:v.strip() for i,v in enumerate(row_contents.split('|')) if i > 0 and i < len(column_labels) - 1}
            if row_dict: # don't consider row if empty
                table_parsed.append(row_dict)
    
    return table_parsed

def get_local_paths(table_parsed: list):
    """
    Calculates the equivalent local path for each topic's .md file

    Args:
        table_parsed (list): List of dictionaries where the keys are the columns of the navtable: 'Level', 'Path', 'Navlink'.

    Returns:
        list : List of Topic dataclass objects
    """
    topics = []
    for item in table_parsed:

        pattern = r'\]\(/t/([^)]+)\)' # All characters between "](/t/" and ")"
        
        match = re.search(pattern, item['Navlink'])
        if match:
            topic_id = match.group(1)
        else:
            continue

        topic_slug = item['Path']
        topic_section = get_diataxis_section(topic_slug)

        # If topic_section is empty, the page will simply go in the root DOCS_PATH directory
            
        topics.append(Topic(DOCS_PATH / topic_section / str(topic_slug + ".md"), topic_id))
    
    return topics
 
def get_diataxis_section(topic_slug: str):
    """
    Given a charmhub slug/path (e.g. "h-deploy"), returns corresponding diataxis section or an empty string
    """
    prefix = topic_slug[:2]

    try:
        section = DIATAXIS_DICT[prefix]
    except KeyError: # return empty string if no diataxis prefix found 
        return ""

    return section

def get_overview_topic_from_metadata():
    """Parses the URL to the overview topic from repository's metadata.yaml and returns its raw markdown content

    Raises:
        Exception: Unexpected URL

    Returns:
        str: Raw markdown content of overview topic
    """
    discourse_instance_url = "https://discourse.charmhub.io/"

    overview_link: str = yaml.safe_load(pathlib.Path("metadata.yaml").read_text())["docs"]
    if not overview_link.startswith(discourse_instance_url):
        raise Exception(f"Overview URL should start with {discourse_instance_url}")

    topic_id = overview_link.split("/")[-1]
    
    return get_raw_markdown(topic_id)
 
if __name__ == "__main__":
    try:
        # Get overview page from metadata.yaml "docs" parameter
        overview_topic_raw = get_overview_topic_from_metadata()

        # Parse navigation table into a list of dicts
        table_parsed = parse_navtable(overview_topic_raw)

        # Calculate local file paths for each topic
        topics = get_local_paths(table_parsed)

        # Download topics as .md files to their corresponding local paths
        print('Downloading topics locally...')
        for topic in topics:
            print(topic.path)
            topic_raw = get_raw_markdown(topic.id)
            topic.path.parent.mkdir(parents=True, exist_ok=True)
            topic.path.write_text(topic_raw)
        
        print("success")
    except:
        print("failed somewhere")
        exit()
