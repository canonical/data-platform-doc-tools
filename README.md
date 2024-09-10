# Data Platform documentation tools

Templates and miscellaneous tooling to help with writing and maintaining Data Platform Charmhub docs:
* [Generate release notes](#generate-release-notes)
* [Documentation review](#documentation-review)

## Generate release notes
Create formatted release notes from GitHub commits for a range of revisions.

### Usage
Fill in the [`config.yaml`](release_notes_formatter/config.yaml) file with the relevant charm parameters, then run `generate.py`.

```shell
$ cd release_notes_formatter

$ nano config.yaml
app: postgresql
substrate: vm
last_revision: 351

amd_22_04: 363
amd_20_04: 
arm_22_04: 364
arm_20_04: 

$ python3 generate.py
Requesting commits from GitHub API: https://api.github.com/repos/canonical/postgresql-k8s-operator/compare/rev351...rev364
Formatted release notes for PostgreSQL K8s revisions dict_values([363, 0, 364, 0]) saved to 'postgresql-k8s-release-notes.md'
```

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
