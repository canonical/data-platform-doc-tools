import re
import yaml
import json
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

VARIABLES_PATH = Path('variables.yaml')
CONFIG_PATH = Path('config.yaml')
TEMPLATES_PATH = Path('templates/')

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
        pr_url = f"https://github.com/canonical/{charm_variables['repo_name']}/pull/{pr_num}"
        
        line = re.sub(pr_pattern, f"([PR #{pr_num}]({pr_url}))", line)
        line = line.strip()
        
    if dpe_match: # Remove from beginning and append to the end as a hyperlink
        dpe_num = dpe_match.group(1)

        line = re.sub(dpe_pattern, '', line).strip()
        line += f" ([DPE-{dpe_num}](https://warthogs.atlassian.net/browse/DPE-{dpe_num}))"

    line = "* " + line
    return line

def get_charm_dict(config):
    with open(VARIABLES_PATH) as f:
        variables = yaml.load(f, Loader=yaml.FullLoader)
    
    # Extract input data from config.yaml
    app = config['app']
    substrate = config['substrate']
    amd_22_04 = config['amd_22_04']
    amd_20_04 = config['amd_20_04']
    arm_22_04 = config['arm_22_04']
    arm_20_04 = config['arm_20_04']
   
    # Generate charm variables for template
    charm_dict = {}
    charm_dict['app'] = app
    charm_dict['substrate'] = substrate
    charm_dict['display_name'] = variables[app][substrate]['display_name']
    charm_dict['repo_name'] = f'{app}-operator' if (substrate == 'vm') else f'{app}-k8s-operator'
    charm_dict['packaging'] = 'snap' if (substrate == 'vm') else 'rock'
    
    charm_dict['revision'] = {}
    charm_dict['revision']['amd_22_04'] = amd_22_04 if amd_22_04 else 0
    charm_dict['revision']['amd_20_04'] = amd_20_04 if amd_20_04 else 0 
    charm_dict['revision']['arm_22_04'] = arm_22_04 if arm_22_04 else 0
    charm_dict['revision']['arm_20_04'] = arm_20_04 if arm_20_04 else 0
    
    charm_dict['min_juju'] = variables[app]['min_juju'] # TODO: currently unused
    
    charm_dict['topic'] = {}
    charm_dict['topic']['all_revisions'] = variables[app][substrate]['all_revisions']
    charm_dict['topic']['system_requirements'] = variables[app][substrate]['system_requirements']
    
    if 'channel' in variables[app]:
        charm_dict['channel'] = variables[app]['channel']
    else:
        charm_dict['channel'] = variables[app][substrate]['channel'] # necessary for mysql-router
        
    return charm_dict

if __name__ == '__main__':
    
    # Load input parameters from `config.yaml`
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
       
    charm_variables = get_charm_dict(config)
    
    # Get list of commits from GitHub 
    tag_number = max(charm_variables['revision'].values()) # tag is always largest revision number
    request_url = f"https://api.github.com/repos/canonical/{charm_variables['repo_name']}/compare/rev{config['last_revision']}...rev{tag_number}"
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
    template = env.get_template(f"{config['app']}.md.jinja")

    # Render release notes from template and write to file
    output_text = template.render(charm_variables, commits=commits_variables)
    
    output_file = config['output_file']
    if not output_file:
        output_file = f"{config['app']}-{config['substrate']}-release-notes.md"
    with open(output_file, 'w') as f:
        f.write(output_text)
        
    print(f"Formatted release notes for {charm_variables['display_name']} revisions {charm_variables['revision'].values()} saved to '{output_file}'")