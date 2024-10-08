from dataclasses import *
import re
import yaml
import base64
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

VARIABLES_PATH = Path('variables.yaml')
CONFIG_PATH = Path('config.yaml')
TEMPLATES_PATH = Path('templates/')

@dataclass
class CharmParameters:
    name: dict
    substrate: str
    packaging: str
            
    revision: dict
    tag_number: str
    channel: str
    
    cloud_version: str
    cloud_type: str

    topic: dict
    
    def __init__(self):
        config = {}
        with open(CONFIG_PATH) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        
        variables = {}
        with open(VARIABLES_PATH) as f:
            variables = yaml.load(f, Loader=yaml.FullLoader)
        
        self.name = {}
        self.name['app'] = config['app']
        self.substrate = config['substrate']
        self.packaging = 'snap' if (self.substrate == 'vm') else 'rock'        
        
        self.name['display'] = variables[self.name['app']][self.substrate]['display_name']
        self.name['repo'] = f"{self.name['app']}-operator" if (self.substrate == 'vm') else f"{self.name['app']}-k8s-operator"
        
        self.revision = {}
        self.revision['last_revision'] = config['last_revision']
        self.revision['amd_22_04'] = config['amd_22_04'] if config['amd_22_04'] else 0
        self.revision['amd_20_04'] = config['amd_20_04'] if config['amd_20_04'] else 0 
        self.revision['arm_22_04'] = config['arm_22_04'] if config['arm_22_04'] else 0
        self.revision['arm_20_04'] = config['arm_20_04'] if config['arm_20_04'] else 0
    
        # Discourse topics (e.g. '/t/123')
        self.topic = {}
        self.topic['all_revisions'] = variables[self.name['app']][self.substrate]['all_revisions']
        self.topic['system_requirements'] = variables[self.name['app']][self.substrate]['system_requirements']
        
        # TODO: change to full tag with 'rev'
        self.tag_number = max(self.revision.values()) # tag is always largest revision number
        
        # Charmhub channel (e.g. '1/stable')
        if 'channel' in variables[self.name['app']]:
            self.channel = variables[self.name['app']]['channel']
        else:
            self.channel = variables[self.name['app']][self.substrate]['channel'] # necessary for mysql-router
        
        self.cloud_type, self.cloud_version = self.get_cloud_version()
        
    
    def get_cloud_version(self):
        cloud_type = ''
        cloud_version = ''
        
        request_url = f"https://api.github.com/repos/canonical/{self.name['repo']}/contents/.github/workflows/ci.yaml"
        params = {'ref': f"rev{self.tag_number}"}
        r = requests.get(request_url, params)
        if r.status_code == 200:
            content = base64.b64decode(r.json()['content']).decode('utf-8')
            content = yaml.load(content, Loader=yaml.FullLoader)
            
            if "cloud" in content["jobs"]["integration-test"]["with"]:
                cloud_type = content["jobs"]["integration-test"]["with"]["cloud"]
                
                cloud_version_key = f"{cloud_type}-snap-channel"
                if cloud_version_key in content["jobs"]["integration-test"]["with"]:
                    cloud_version = content["jobs"]["integration-test"]["with"][cloud_version_key]
            
        return cloud_type, cloud_version
        
    def get_microk8s_version(self):
        print('microk8s')
            
def classify_messages(commits):
    bot = [] # bot actions
    jira = [] # prefaced by Jira ticket
    other = [] # prefaced by [MISC] or none of the above
    for i in commits:
        message = commits[i]['message']
        if commits[i]['author'][-5:] == "[bot]":
            bot.append(message)
        elif message[0:7] == "[DPE-":
            jira.append(commits[i])
        elif message[0:6] == "[MISC]":
            message = message.replace('[MISC]','')
            other.append(message)
        else:
            other.append(message)
    
    # Sort bot commits incrementally for readability
    bot = sorted(bot, key=str.lower)
    
    return bot, jira, other
            
def format_line(line):
    '''
    Format a GitHub commit message as:
        `<message text> (PR #<pr number>)[<pr_url>]) ([DPE-<ticket number>](<ticket url>))`
    '''
    pr_pattern = r"\(#(\d+)\)"
    dpe_pattern = r'[\[\(\s]*DPE-(\d+)[\]\)\s]*'
    
    pr_match = re.search(pr_pattern, line, flags=re.DOTALL)
    dpe_match = re.search(dpe_pattern, line, flags=re.DOTALL)
    
    if pr_match: # Transform into hyperlink
        pr_num = pr_match.group(1)
        pr_url = f"https://github.com/canonical/{params.name['repo']}/pull/{pr_num}"
        
        line = re.sub(pr_pattern, f"([PR #{pr_num}]({pr_url}))", line)
        line = line.strip()
        
    if dpe_match: # Remove from beginning and append to the end as a hyperlink
        dpe_num = dpe_match.group(1)

        line = re.sub(dpe_pattern, '', line).strip()
        line += f" ([DPE-{dpe_num}](https://warthogs.atlassian.net/browse/DPE-{dpe_num}))"

    line = "* " + line
    return line

if __name__ == '__main__':
    
    params = CharmParameters()
    
    # Get list of commits from GitHub 
    request_url = f"https://api.github.com/repos/canonical/{params.name['repo']}/compare/rev{params.revision['last_revision']}...rev{params.tag_number}"
    print(f"Requesting commits from GitHub API: {request_url}")
    r = requests.get(request_url)
    if r.status_code == 404:
        print("404: Github API request unsuccessful")
        exit()
    
    results = r.json().get("commits", [])
    
    # Extract commit heading (i.e. PR title) and author
    commits = {}
    for i in range (0,len(results)):
        commit_info = {}
        commit_info['author'] = results[i]['author']['login']
        
        message = results[i]['commit']['message']
        end_id = message.find('\n')
        if end_id > -1:
            commit_info['message'] = message[0:end_id]
        else:
            commit_info['message'] = message
            
        commits[i] = commit_info
        
    # Classify commit types
    bot, jira, other = classify_messages(commits)

    # Format each line and join all commits back into one string
    bot = "\n".join([format_line(line) for line in bot])
    jira = "\n".join([format_line(line) for line in jira])
    other = "\n".join([format_line(line) for line in other])

    # Generate jinja variables
    commits_variables = {'jira':jira, 'other':other, 'bot':bot}

    # Set up jinja environment
    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    template = env.get_template(f"{params.name['app']}.md.jinja")

    # Render release notes from template and write to file
    charm_variables = asdict(params)
    output_text = template.render(charm_variables, commits=commits_variables)
    

    output_file = f"{params.name['app']}-{params.substrate}-release-notes-{params.tag_number}.md"
    with open(output_file, 'w') as f:
        f.write(output_text)
        
    print(f"Formatted release notes for {params.name['display']} revisions {params.revision.values()} saved to '{output_file}'")