
## Charmhub

Every charm or bundle of charms that is listed on charmhub.io has its own path: `charmhub.io/some-charm` or `charmhub.io/some-charm-bundle`.

All documentation pages here are rendered from Discourse posts created and hosted in the Discourse instance `discourse.charmhub.io`. More about this in the section [Discourse vs. Charmhub]().

## Discourse

Discourse is the primary host and source of truth for our documentation. This section contains practical guides for writing docs on Discourse, more in-depth explanations about the most relevant nuances of Discourse/Charmhub, and some useful references. 

### How-To

#### How to edit an existing page 
These are the steps to edit a page that already exists on Charmhub.

1. Go to `charmhub.io/<your-charm>`

2. Navigate to the page you want to edit

3. At the very bottom of the page, there is a blue information box. Click on the linked text “Help improve this document in the forum”. This will take you to its corresponding discourse topic. 

4. At the bottom of the discourse post, click on the icon that looks like a square and a pencil, with the text “Edit”. 

5. If you do not see this icon, see the section Publish the topic and turn it into a Wiki.

6. Edit the topic and press the orange “Save edit” button located on the bottom left of the editor.

7. If this topic is not linked to the charm's charmhub.io documentation, refer to Step X in the section [How to add a new page to existing docs](#how-to-add-a-new-page-to-existing-docs).

#### How to add a new page to existing docs 
These are the steps to add a new page to a charm that already has documentation on charmhub.

1. Go to [`discourse.charmhub.io`](https://discourse.charmhub.io/)

Make sure you’re logged in. If this is your first time logging in, use your Canonical Google account.

2. Create a new topic

Click on the gray button that says “New Topic” on the top-right corner of discourse.charmhub.io.

Use the charm category.

3. Publish the topic and turn it into a Wiki
When ready, press the orange “Create Topic” button in the bottom left
Will take you to page discourse.charmub.io/t/ksdlkf/1234, this is unique ID

Bottom right wrench, turn to wiki so others can edit. If you don’t see this button, talk to Andreia Velasco Gomes.

4. Add page to the navigation
When the topic is published and you are ready to add it to a charm’s documentation, head towards the Overview topic. 

You can find the Overview topic by heading to charmhub.io/<your-charm>, scrolling to the bottom, and clicking on “Help improve this document in the forum”. 

#### How to create docs for a new charm 
These are the steps to set up docs for a brand new charm that is listed on charmhub. (You can still set up the docs if it is not listed; you just won’t be able to see the rendered output yet)

1. Create an Overview topic

2. Add the Overview discourse link to the repository’s metadata.yaml
The link should be assigned to the key docs:, somewhere near the charm’s name and description. See mongodb-operator’s metadata.yaml for an example.

3. Plan the structure of your documentation
This is important! A Data Platform charm does not need to reproduce every page that exists in other DP charms. 

First, determine whether your charm is a “main” charm or a “support” charm. 

A main charm would be PostgreSQL, MySQL, MongoDB, Kafka, etc. This kind of charm follows a similar structure, as explained in the section Pages > Main charms.

If it’s small, subordinate, or tooling - see Pages > Support charms

Submit your structure proposal to Andreia Velasco Gomes for review and approval. 

### Explanation

#### Navigation table

The navigation table is a part of a charm’s “Overview” topic that does not get rendered on charmhub.io. It tells the flask app how to link the separate published topics together into one charm’s documentation set.

```
| Level | Path | Navlink |
|-------|--------|-------|
| 1 | tutorial   | [Tutorial]() |
| 2 | t-overview | [Overview](/t/9296) |
| 2 | t-set-up   | [1. Set up the environment](/t/9297) |
| 2 | t-deploy   | [2. Deploy PostgreSQL](/t/9298) |
```

- Level: This is the hierarchy level, where 1 is the topmost. 
- Path: This is the slug that will be used in the URL of its corresponding charmhub.io page. We try to keep them consistent throughout all Data Platform docs. Check this Slug Reference 🪱 
- Navlink: [<Nav title>](<topic ID>)
The nav title applies exclusively to the navigation menu. If the actual title of the page is very long and would wrap several times in the nav menu, you can consider shortening it here. 
The topic ID is a unique ID given to each discourse topic. You can find it in the URL of the topic: discourse.charmhub.io/t/some-page-title/1234
- Group headers 
Make empty [group parent]()
No page link for now due to discourse-gatekeeper limitation

#### Discourse vs. Charmhub
>Discourse instances

>Flask app for each

>Rendered site, generated with Vanilla

>Limitations of charmhub.io

#### Auto-generated Charmhub content (API)
>Resources, Integrations, Libraries, Configuration, Actions

#### Formatting and syntax on Discourse
>Markdown + HTML, avoid the latter when possible

>Additional markdown features: notes, images

>Not all syntax you see in other instances is available on Charmhub. E.g. no [tabs] yet
Heading anchors

## FAQ

Do all published docs become available on Charmhub on all tracks (edge/beta/candidate/stable) as soon as it is published?

Why don't I see the “Edit” button on a topic? 

The Charmhub page for Charm X is completely empty - it doesn’t even have a home page. How do I add docs here?
