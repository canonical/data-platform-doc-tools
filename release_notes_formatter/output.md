>Reference > Release Notes > [All revisions] > Revision 269/268

# Revision 269/268

Dear community,

Canonical's newest Charmed MySQL operator has been published in the [8.0/stable channel].

Due to the newly added support for `arm64` architecture, the MySQL charm now releases two revisions simultaneously: 
* Revision 268 is built for `amd64`
* Revision 269 is built for `arm64`

To make sure you deploy for the right architecture, we recommend setting an [architecture constraint](https://juju.is/docs/juju/constraint#heading--arch) for your entire juju model.

Otherwise, it can be done at deploy time with the `--constraints` flag:
```shell
juju deploy mysql --constraints arch=<arch> 
```
where `<arch>` can be `amd64` or `arm64`.

---

## Highlights 
*  Strip passwords from command execute output and tracebacks ([PR #499](https://github.com/canonical/mysql-operator/pull/499)) ([DPE-4266](https://warthogs.atlassian.net/browse/DPE-4266))
* Use poetry package-mode=false ([PR #495](https://github.com/canonical/mysql-operator/pull/495))

## Bugfixes

TODO: Fill in manually based on Highlights section

## Dependencies and automations
* [discourse-gatekeeper] Migrate charm docs ([PR #486](https://github.com/canonical/mysql-operator/pull/486))
* Update data-platform-workflows to v18 ([PR #490](https://github.com/canonical/mysql-operator/pull/490))

## Technical details
This section contains some technical details about the charm's contents and dependencies. 

If you are jumping over several stable revisions, check [previous release notes][All revisions] before upgrading.

### Requirements
See the [system requirements] page for more details about software and hardware prerequisites.

### Packaging

This charm is based on the Charmed MySQL snap ([Revision 112/113][112/113]) . It packages:
* [mysql-server-8.0 `v8.0.37`]
* [mysql-router `v8.0.37`]
* [mysql-shell `v8.0.37`]
* [prometheus-mysqld-exporter `v0.14.0`]
* [prometheus-mysqlrouter-exporter `v5.0.1`]
* [percona-xtrabackup `v8.0.35`]


### Libraries and interfaces
This charm revision imports the following libraries: 
* **mysql `v0`**
  * See the API reference in the [MySQL Libraries tab]
* **grafana_agent `v0`** for integration with Grafana 
    * Implements  `cos_agent` interface
* **rolling_ops `v0`** for rolling operations across units 
    * Implements `rolling_op` interface
* **tempo_k8s `v1`, `v2`** for integration with Tempo charm
    * Implements `tracing` interface
* **tls_certificates_interface `v2`** for integration with TLS charms
    * Implements `tls-certificates` interface

See the [`/lib/charms` directory on GitHub] for more details about all supported libraries.

See the [`metadata.yaml` file on GitHub] for a full list of supported interfaces.


<!-- Topics -->
[All revisions]: /t/11881
[system requirements]: /t/11742

<!-- GitHub -->
[`/lib/charms` directory on GitHub]: https://github.com/canonical/mysql-operator/tree/main/lib/charms
[`metadata.yaml` file on GitHub]: https://github.com/canonical/mysql-operator/blob/main/metadata.yaml

<!-- Charmhub -->
[8.0/stable channel]: https://charmhub.io/mysql?channel=8.0/stable

<!-- Snap/Rock -->
[`charmed-mysql` packaging]: https://github.com/canonical/charmed-mysql-snap

[MySQL Libraries tab]: https://charmhub.io/mysql/libraries

[113/114]: https://github.com/canonical/charmed-mysql-snap/releases/tag/rev114
[rock image]: https://github.com/canonical/charmed-mysql-rock/pkgs/container/charmed-mysql

[mysql-server-8.0 `v8.0.37`]: 8.0.37-0ubuntu0.22.04.1
[mysql-router `v8.0.37`]: 8.0.37-0ubuntu0.22.04.1
[mysql-shell `v8.0.37`]: 8.0.37+dfsg-0ubuntu0.22.04.1~ppa3
[prometheus-mysqld-exporter `v0.14.0`]: 0.14.0-0ubuntu0.22.04.1~ppa2
[prometheus-mysqlrouter-exporter `v5.0.1`]: 5.0.1-0ubuntu0.22.04.1~ppa1
[percona-xtrabackup `v8.0.35`]: 8.0.35-31-0ubuntu0.22.04.1~ppa3
