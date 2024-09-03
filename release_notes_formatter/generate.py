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
    app: str
    substrate: str
    last_revision: str
    amd_22_04: str
    amd_20_04: str
    arm_22_04: str
    arm_20_04: str
    
    output_file: str
    display_name: str
    
    repo_name: str
    packaging: str
    
    tag_number: str
    channel: str
    min_juju: str
    max_juju: str
    cloud_version: str
    cloud_type: str
    
    revision: dict
    topic: dict
    
    def __init__(self):
        config = {}
        with open(CONFIG_PATH) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            
        self.app = config['app']
        self.substrate = config['substrate']
        self.last_revision = config['last_revision']
        self.amd_22_04 = config['amd_22_04']
        self.amd_20_04 = config['amd_20_04']
        self.arm_22_04 = config['arm_22_04']
        self.arm_20_04 = config['arm_20_04']
        self.output_file = config['output_file']
                
        variables = {}
        with open(VARIABLES_PATH) as f:
            variables = yaml.load(f, Loader=yaml.FullLoader)
        
        self.display_name = variables[self.app][self.substrate]['display_name']
        self.repo_name = f'{self.app}-operator' if (self.substrate == 'vm') else f'{self.app}-k8s-operator'
        self.packaging = 'snap' if (self.substrate == 'vm') else 'rock'
        
        self.revision = {}
        self.revision['amd_22_04'] = self.amd_22_04 if self.amd_22_04 else 0
        self.revision['amd_20_04'] = self.amd_20_04 if self.amd_20_04 else 0 
        self.revision['arm_22_04'] = self.arm_22_04 if self.arm_22_04 else 0
        self.revision['arm_20_04'] = self.arm_20_04 if self.arm_20_04 else 0
    
        # Discourse topics (e.g. '/t/123')
        self.topic = {}
        self.topic['all_revisions'] = variables[self.app][self.substrate]['all_revisions']
        self.topic['system_requirements'] = variables[self.app][self.substrate]['system_requirements']
        
        # TODO: change to full tag with 'rev'
        self.tag_number = max(self.revision.values()) # tag is always largest revision number
        
        # Charmhub channel (e.g. '1/stable')
        if 'channel' in variables[self.app]:
            self.channel = variables[self.app]['channel']
        else:
            self.channel = variables[self.app][self.substrate]['channel'] # necessary for mysql-router
        
        self.min_juju, self.max_juju = self.get_juju_versions()
        
        self.cloud_type, self.cloud_version = self.get_cloud_version()
        
    def get_juju_versions(self):
        min_juju = ''
        max_juju = ''
        
        request_url = f"https://api.github.com/repos/canonical/{self.repo_name}/contents/metadata.yaml"
        params = {'ref': f"rev{self.tag_number}"}
        r = requests.get(request_url, params)
        if r.status_code == 200:
            content = base64.b64decode(r.json()['content']).decode('utf-8')
            content = yaml.load(content, Loader=yaml.FullLoader)
            juju_versions = {}
            if "assumes" in content:
                assumes = content["assumes"]
                for i in assumes:
                    if type(i) == dict:
                        if "any-of" in i:
                            juju_versions = [item['all-of'] for item in i['any-of']]
                            
                            version_pattern = r'(\d+(\.\d+)*)'
                            min_version = re.search(version_pattern, juju_versions[0][0]).group(1)
                            max_version = re.search(version_pattern, juju_versions[-1][-1]).group(1)
                            
                            min_juju = min_version
                            max_juju = max_version
        return min_juju, max_juju
    
    def get_cloud_version(self):
        cloud_type = ''
        cloud_version = ''
        
        request_url = f"https://api.github.com/repos/canonical/{self.repo_name}/contents/.github/workflows/ci.yaml"
        params = {'ref': f"rev{self.tag_number}"}
        r = requests.get(request_url, params)
        if r.status_code == 200:
            content = base64.b64decode(r.json()['content']).decode('utf-8')
            content = yaml.load(content, Loader=yaml.FullLoader)
            
            if "cloud" in content["jobs"]["integration-test"]["with"]:
                cloud_type = content["jobs"]["integration-test"]["with"]["cloud"]
                
                cloud_version_key = f"{cloud_type}-snap-channel"
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
        pr_url = f"https://github.com/canonical/{params.repo_name}/pull/{pr_num}"
        
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
    request_url = f"https://api.github.com/repos/canonical/{params.repo_name}/compare/rev{params.last_revision}...rev{params.tag_number}"
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
    template = env.get_template(f"{params.app}.md.jinja")

    # Render release notes from template and write to file
    charm_variables = asdict(params)
    output_text = template.render(charm_variables, commits=commits_variables)
    
    output_file = params.output_file
    if not output_file:
        output_file = f"{params.app}-{params.substrate}-release-notes-{params.tag_number}.md"
    with open(output_file, 'w') as f:
        f.write(output_text)
        
    print(f"Formatted release notes for {params.display_name} revisions {params.revision.values()} saved to '{output_file}'")