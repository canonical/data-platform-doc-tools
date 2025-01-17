# Integrate PostgreSQL with PgBouncer


[Juju integrations](https://juju.is/docs/sdk/integration?_gl=1*1vu8j91*_gcl_au*ODEzODE4NzE2LjE3MTc0MTcxNzQ.*_ga*MTEyNTQ0MjIwMi4xNzIxMTI4MjY1*_ga_5LTL1CNEJM*MTcyMjAwNjUxMy4zNy4xLjE3MjIwMDc3NzYuNTkuMC4w), previously known as “relations”, are connections to an application via a particular endpoint. Integrations automatically create a username, password, and database for the desired user/application. It is a better practice to connect to PostgreSQL via a specific user rather than the admin user.

When setting up PostgreSQL for use cases with heavy workloads, the database performance might be reduced due to multiple read/write requests. In such cases, it is recommended to use a connection pooler such as [PgBouncer]().

In this section, you will learn how to use juju integrations by deploy the `pgbouncer-k8s` charmed operator and integrate it with `postgresql-k8s`.

## Summary
* 


---

## Deploy Charmed PgBouncer

Deploy Charmed PgBouncer for K8s with the following command:

```shell
juju deploy pgbouncer-k8s --channel 1/stable --trust
```

If you run `juju status`, you will see that PgBouncer is in a blocked state due to a missing integration with PostgreSQL.

To integrate them, simply run

```shell
juju integrate postgresql-k8s pgbouncer-k8s
```

Now, `juju status` will report a new blocking reason:  `Missing relation: database` as it waits for a client to consume the database service.

[WHY DO WE NEED DATA-INTEGRATOR ON VM vs. K8S?] 

Deploy `data-integrator` and request access to database `tutorial-db`:

```shell
juju deploy data-integrator --config database-name=tutorial-db
```

Integrate it with `pgbouncer` to create a user:
```shell
juju integrate data-integrator pgbouncer
```

In a few seconds, the entire model will have an active status and `pgbouncer` will be running inside of `data-integrator`.

[juju status output]