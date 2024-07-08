# Data Platform documentation tools

Templates and miscellaneous tooling to help with writing and maintaining docs.

## Templates

The following files contain templates for the standard types of pages featured in Data Platform docs. 

| Name                                   | template                  | example |
|----------------------------------------|---------------------------|:-------:|
| Overview (i.e. home page)              | [overview.md](templates/overview.md) | example |
| **Tutorial**                           |                           |         |
| Overview                               | [t-overview.md](templates/tutorial/t-overview.md) | example |
| Page                                   | [t-page.md](templates/tutorial/t-page.md) | example |
| **How-To**                             |                           |         |
| Page                                   | [h-page.md](templates/how-to/h-page.md) | example |
| **Reference**                          |                           |         |
| Overview                               | [r-overview.md](templates/reference/r-overview.md) | example |
| System requirements                    | [r-system-requirements.md](templates/reference/r-system-requirements.md) | example |
| Release Notes Overview                 | [release-notes-overview.md](templates/reference/release-notes-overview.md) | example |
| Release Notes Revision X | [release-notes-revision.md](templates/reference/release-notes-revision.md) | example |
| Page                                   | [r-page.md](templates/reference/r-page.md) | example |
| **Explanation**                        |                           |         |
| Page                                   | [e-page.md](templates/explanation/e-page.md) | example |

### Markdown and syntax

All templates are written with Discourse-compatible markdown. Some elements are Discourse-specific and will not be parsed by other Markdown editors (e.g. `[note] [/note]`).

Sections that must be filled in by the writer are marked in {curly brackets}. I tried to be consistent so that, when the same content gets repeated, you can easily find and replace. 

Markdown comments in the format `<!-- sample comment -->` are meant as guidance and should be removed before publishing the Discourse topic.

## Documentation review
To start a documentation review process:
1. Create a new branch (use Jira ticket name when applicable)
2. Create a new markdown file in your charm's directory and Diataxis group. Use the discourse slug as the filename.
E.g. `postgresql/how-to/h-deploy-lxd.md`

> [!NOTE]  
> Ignore any sub-directories/groups below the 4 main Diataxis categories

3. Submit your PR and add reviewers
4. Once the review process is over, copy the reviewed page onto discourse
5. Close the PR without merging.