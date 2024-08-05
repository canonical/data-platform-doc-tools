# README

This script parses the discourse documentation link in a charm repository's `metadata.yaml` file and downloads all documentation pages to a local `/docs` folder.

Each page is placed on its corresponding Diataxis folder based on the slug prefix. If no valid prefix is found, the page is placed in the root `/docs` folder.

Any further hierarchy/nesting is ignored. All pages under a Diataxis section will be at the same level.

## Documentation requirements

The documentation must follow standard, existing Discourse documentation requirements. Most importantly, their overview topic contains a navigation table of the following format:

```
| Level | Path | Navlink |
|--------|--------|-------------|
| 1 | tutorial | [Tutorial]() |
| 2 | t-overview | [Overview](/t/9707) |
```

There are currently two extra requirements that the Discourse-hosted documentation must follow for compatibility with the script:
* [Overview topic formatting](#overview-topic)
* [Link formatting in the navigation table](#link-formatting)

Both of them can be removed or adapted if necessary.

### Overview topic
Requirement: The navigation table of the overview page is wrapped by the `[details]` HTML/markdown element as follows:

```
# Navigation

[details=Navigation]

<navigation table goes here>

[/details]

```

> [!NOTE]  
> There should be a whitespace before and after the `[details]` and `[/details]` lines. Otherwise, Discourse/Charmhub may not parse them correctly.

### Link formatting

Links in the `Navlink` column are formatted as `[Text](/t/<number>)`.

They are not formatted as `[Text](/t/<some-additional-slug-text>/<number>)`.

### Sample docs
The following documentation sets fulfill the above requirements and have been tested:
* [PostgreSQL VM](https://discourse.charmhub.io/t/charmed-postgresql-documentation/9710)
* [PostgreSQL K8s](https://discourse.charmhub.io/t/charmed-postgresql-k8s-documentation/9307)
* [PgBouncer VM](https://discourse.charmhub.io/t/pgbouncer-documentation/12133)
* [PgBouncer K8s](https://discourse.charmhub.io/t/pgbouncer-k8s-documentation/12132)
* [MySQL Router K8s](https://discourse.charmhub.io/t/mysql-router-k8s-documentation/12130)