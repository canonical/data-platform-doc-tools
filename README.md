# Data Platform documentation tools

Templates and miscellaneous tooling to help with writing and maintaining Data Platform Charmhub docs:
* [Documentation review](#documentation-review)
* [Generate release notes](#generate-release-notes)

## Documentation review
To start a documentation review process:
1. Create a new branch (use Jira ticket ID when applicable)
2. Create a new markdown file in your charm's directory, ignoring Diataxis groups. Use the discourse slug as the filename.
E.g. `postgresql-k8s/h-deploy-gke.md`

> [!NOTE]  
> Ignore the navigation hierarchy; no need to create intermediate directories like `postgresql-k8s/how-to/set-up/h-deploy.gke.md`

3. Submit your PR and add reviewers
4. Once the review process is over, copy the reviewed page onto discourse
5. Close the PR without merging.

## Generate release notes
Located at [`release_notes_formatter/`](release_notes_formatter/)/

The [`generate.py`](release_notes_formatter/generate.py) script creates formatted release notes from GitHub commits for a given revision.

### Usage
First, fill in `config.yaml` with the right charm and revisions. See [Configuration](#configuration) for more information.

Then, run `generate.py`.
```shell
cd release_notes_formatter
python3 generate.py
```

### Configuration
[`config.yaml`](release_notes_formatter/config.yaml)

The script loads the `config.yaml` file containing parameters about the product and revision. For example:
```yaml
# (Required) Application name: mysql, postgresql, pgbouncer, mysql-router
app: mysql

# (Required) Substrate: vm, k8s
substrate: vm

# (Required) Revisions for each build
arm_revision: 269
amd_revision: 268

# (Optional) Output file for formatted release notes
# Default: {app}-{substrate}-release-notes.md
output_file: ''

# (Optional) Input file with GitHub release notes text (Must contain '## What's Changed` heading) 
# Default: GitHub API query with tag based on revisions
input_file: ''
```

