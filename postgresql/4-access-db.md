# Access PostgreSQL database

## Retrieve credentials

Connecting to the database requires that you know three pieces of information: The internal PostgreSQL database’s username and password, and the host machine’s IP address.

The IP address of the PgBouncer K8s’s host can be found with `juju status`:

```shell
...
App              Version  Status  Scale  Charm            Channel    Rev  Address         Exposed  Message
pgbouncer-k8s    1.18.0   active      1  pgbouncer-k8s    1/stable    76  10.152.183.84   no   
```

To retrieve the username and password, run the action `get-credentials` on the leader unit of `data-integrator`:

```shell
juju run data-integrator/leader get-credentials
```

Below is a sample output:

```shell
postgresql:
  database: test123
  endpoints: pgbouncer-k8s-0.pgbouncer-k8s-endpoints.test16.svc.cluster.local:6432
  password: VYm6tg2KkFOBj8mP3IW9O821
  username: relation_id_7
  version: "14.9"
```



## `psql`

The easiest way to access PostgreSQL is via the [PostgreSQL Command Line Client `psql`](https://www.postgresql.org/docs/14/app-psql.html), which is already installed on the host you're connected to.

To access the PostgreSQL database via PgBouncer, use the port 6432 and your host’s IP address:

```shell
psql -h <pgbouncer_app_ip> -p 6432 -U <data-integrator_username> -W -d tutorial-db

# Example
psql -h 10.152.183.84 -p 6432 -U relation_id_7 -W -d tutorial-db
```

Inside PostgreSQL, list available databases on the host with `show databases`:

```
Password for user relation_id_7:  VYm6tg2KkFOBj8mP3IW9O821
psql (14.9 (Ubuntu 14.9-0ubuntu0.22.04.1))
Type "help" for help.

tutorial-db=> \l
                                     List of databases
   Name        |     Owner     | Encoding | Collate |  Ctype  |        Access privileges        
---------------+---------------+----------+---------+---------+---------------------------------
...
 tutorial-db   | relation_id_5 | UTF8     | C       | C.UTF-8 | relation_id_5=CTc/relation_id_5+
               |               |          |         |         | relation_id_7=CTc/relation_id_5+
               |               |          |         |         | admin=CTc/relation_id_5
...
```

You can now interact with PostgreSQL directly using any [SQL Queries](https://www.postgresql.org/docs/14/sql-syntax.html).

For example, entering `SELECT VERSION(), CURRENT_DATE;` should output something like:

```
test123=> SELECT VERSION(), CURRENT_DATE;
                                                               version                                                                | current_date 
--------------------------------------------------------------------------------------------------------------------------------------+--------------
 PostgreSQL 14.9 (Ubuntu 14.9-0ubuntu0.22.04.1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 11.4.0-1ubuntu1~22.04) 11.4.0, 64-bit | 2023-10-23
(1 row)
```


Feel free to test out any other PostgreSQL queries. When you’re ready to leave the psql shell, you can just type exit.

Now you will be in your original shell where you first started the tutorial. Here you can interact with Juju and MicroK8s.

### Remove the user

To remove the user, remove the relation. Removing the relation automatically removes the user that was created when the relation was created. 

Run the following command to remove the relation:
```shell
juju remove-relation pgbouncer-k8s data-integrator
```

Now try again to connect to the same PgBouncer K8s you used earlier:
```shell
psql -h 10.152.183.84 -p 6432 -U relation_id_7 -W -d test123
```

This will output an error message because this user no longer exists.
```shell
psql: error: connection to server at "10.152.183.92", port 5432 failed: FATAL:  password authentication failed for user "relation_id_7"
```
This is expected, as `juju remove-relation pgbouncer-k8s data-integrator` also removes the user.

[note]
**Note**: Data remains on the server at this stage.
[/note]

Relate the two applications again if you wanted to recreate the user:
```shell
juju integrate data-integrator pgbouncer-k8s
```
Re-relating generates a new user and password:
```shell
juju run data-integrator/leader get-credentials
```
You can connect to the database with these new credentials.

From here you will see all of your data is still present in the database.