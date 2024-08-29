import re
import yaml
import json
import requests
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

VARIABLES_PATH = Path('variables.yaml')
CONFIG_PATH = Path('config.yaml')
TEMPLATES_PATH = Path('templates/')

def classify_commits(commits):
    renovate = [] # @renovate
    github_actions = [] # @github-actions
    jira = [] # prefaced by Jira ticket
    other = [] # prefaced by [MISC] or none of the above
    for commit in commits:
        if commit.find("@github-actions") > -1:
            github_actions.append(commit)
        elif commit.find("@renovate") > -1:
            renovate.append(commit)
        elif commit[0:7] == "* [DPE-":
            jira.append(commit)
        elif commit[0:8] == "* [MISC]":
            commit = commit.replace('* [MISC]','*')
            other.append(commit)
        else:
            other.append(commit)
    
    # Sort bot commits incrementally
    github_actions = sorted(github_actions, key=str.lower)
    renovate = sorted(renovate, key=str.lower)
    
    return renovate, github_actions, jira, other
            
def format_line(line):
    author_match = re.search(r"( by \@\S+ in)", line, flags=re.DOTALL)
    
    if author_match:
        author = author_match.group(1)
        line = line.replace(author, '')
        
    dpe_pattern = r"\[DPE-(\d+)\]"
    pr_pattern = r"https://github.com/[^/]+/[^/]+/pull/(\d+)"
    
    dpe_match = re.search(dpe_pattern, line, flags=re.DOTALL)
    pr_match = re.search(pr_pattern, line, flags=re.DOTALL)
    
    if pr_match:
        pr_num = pr_match.group(1)
        pr_url = pr_match.group(0)
        
        line = re.sub(pr_pattern, f"([PR #{pr_num}]({pr_url}))", line)
        line = line.strip()
        
        if dpe_match: # TODO: Remove extra whitespace after bullet point 
            dpe_num = dpe_match.group(1)

            line = re.sub(dpe_pattern, "", line)
            line += f" ([DPE-{dpe_num}](https://warthogs.atlassian.net/browse/DPE-{dpe_num}))"

    return line

def get_charm_dict(arm_revision, amd_revision, app, substrate):
    with open(VARIABLES_PATH) as f:
        dict = yaml.load(f, Loader=yaml.FullLoader)
    
    charm_dict = {}
    charm_dict['app'] = app
    charm_dict['substrate'] = substrate
    charm_dict['display_name'] = dict[app][substrate]['display_name']
    charm_dict['repo_name'] = f'{app}-operator' if (substrate == 'vm') else f'{app}-k8s-operator'
    charm_dict['packaging'] = 'snap' if (substrate == 'vm') else 'rock'
    charm_dict['amd_revision'] = amd_revision
    charm_dict['arm_revision'] = arm_revision
    charm_dict['min_juju'] = dict[app]['min_juju']
    charm_dict['all_revisions'] = dict[app][substrate]['all_revisions']
    charm_dict['system_requirements'] = dict[app][substrate]['system_requirements']
    
    if 'channel' in dict[app]:
        charm_dict['channel'] = dict[app]['channel']
    else:
        charm_dict['channel'] = dict[app][substrate]['channel'] # necessary for mysql-router
        
    return charm_dict

if __name__ == '__main__':
    #TODO Enforce consistent formatting for [DPE-123]
    #TODO Enforce PR prefix "Fix:" or labels
    
    # Load input parameters from `config.yaml`
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    
    app = config['app']
    substrate = config['substrate']
    arm = config['arm_revision']
    amd = config['amd_revision']
    input_file = config['input_file']
    output_file = config['output_file']
    
    print(f"Generating variables for {app}-{substrate}, revisions {arm}/{amd}...")
    charm_variables = get_charm_dict(arm, amd, app, substrate)
    
    # Get release notes from GitHub 
    github_notes = ''
    if input_file:
        with open(input_file, 'r') as file:
            github_notes = file.read()
    else:
        tag_number = max(int(arm), int(amd)) # tag is always largest revision number
        print(f"Requesting text from github.com/canonical/{charm_variables['repo_name']}/releases/tags/rev{tag_number}...")
        r = requests.get(f"https://api.github.com/repos/canonical/{charm_variables['repo_name']}/releases/tags/rev{tag_number}")
        if r.status_code == 404:
            print("404 not found: Github API request unsuccessful")
            exit()
        github_notes = json.loads(r.text)['body']
    
    print(f"Formatting commits...")
    # Isolate commits
    match = re.search(
        r"## What's Changed\s*(.*?)\s*\n\n",
        github_notes,
        flags=re.DOTALL,
    )
    if not match:
        print('Could not find GitHub commits. Exiting.')
        exit()
        
    commits = match.group(1).split("\n")

    # Classify commit types
    renovate, github_actions, jira, other = classify_commits(commits)

    # Format each line and join all commits back into one string
    github_actions = "\n".join([format_line(line) for line in github_actions])
    renovate = "\n".join([format_line(line) for line in renovate])
    jira = "\n".join([format_line(line) for line in jira])
    other = "\n".join([format_line(line) for line in other])

    # Generate jinja variables
    commits_variables = {'jira':jira, 'other':other, 'github_actions':github_actions, 'renovate':renovate}

    # Set up jinja environment and template
    print("Building jinja template...")
    file_loader = FileSystemLoader(TEMPLATES_PATH)
    env = Environment(loader=file_loader)
    
    template = env.get_template(f"{app}.md.jinja")

    # Render release notes from template and write to file
    output_text = template.render(charm=charm_variables, commits=commits_variables)
    if not output_file:
        output_file = f'{app}-{substrate}-release-notes.md'
    with open(output_file, 'w') as f:
        f.write(output_text)
        
    print(f"Formatted release notes for {charm_variables['display_name']} Revision {amd}/{arm} saved to '{output_file}'")