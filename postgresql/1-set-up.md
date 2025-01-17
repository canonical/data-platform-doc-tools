# Set up the environment

In this page, we will set up a development environment with the required components for deploying Charmed PostgreSQL K8s.

## Summary
* [Set up Multipass]
* [Set up Juju]

---

## Set up Multipass

Multipass is a quick and easy way to launch virtual machines running Ubuntu. It uses the cloud-init standard to install and configure all the necessary parts automatically.

Install Multipass from [Snap](https://snapcraft.io/multipass?_gl=1*p32nht*_gcl_au*ODEzODE4NzE2LjE3MTc0MTcxNzQ.*_ga*MTEyNTQ0MjIwMi4xNzIxMTI4MjY1*_ga_5LTL1CNEJM*MTcyMjAwNjUxMy4zNy4xLjE3MjIwMDY2MTguNjAuMC4w) with the following command:

```shell
sudo snap install multipass
```

Launch a new VM using the [`charm-dev`](https://github.com/canonical/multipass-blueprints/blob/main/v1/charm-dev.yaml) cloud-init config:

```shell
multipass launch --cpus 4 --memory 8G --disk 50G --name my-vm charm-dev
```
>Note: All ‘multipass launch’ parameters are described [here](https://multipass.run/docs/launch-command?_gl=1*1y9uf34*_gcl_au*ODEzODE4NzE2LjE3MTc0MTcxNzQ.*_ga*MTEyNTQ0MjIwMi4xNzIxMTI4MjY1*_ga_5LTL1CNEJM*MTcyMjAwNjUxMy4zNy4xLjE3MjIwMDY2MTguNjAuMC4w).

The Multipass [list of commands](https://multipass.run/docs/multipass-cli-commands?_gl=1*p32nht*_gcl_au*ODEzODE4NzE2LjE3MTc0MTcxNzQ.*_ga*MTEyNTQ0MjIwMi4xNzIxMTI4MjY1*_ga_5LTL1CNEJM*MTcyMjAwNjUxMy4zNy4xLjE3MjIwMDY2MTguNjAuMC4w) is short and self-explanatory. For example, to show all running VMs, just run the command multipass list.

As soon as a new VM has started, access it using

```shell
multipass shell my-vm
```
>Note: If at any point you’d like to leave a Multipass VM, enter Ctrl+D or type exit.

All necessary components have been pre-installed inside the VM already, like MicroK8s and Juju. The files `/var/log/cloud-init.log` and `/var/log/cloud-init-output.log` contain all low-level installation details.

## Set up Juju

Let’s bootstrap Juju to use the local LXD controller:

```shell
juju bootstrap localhost overlord
```

A controller can work with different [models](https://juju.is/docs/juju/model?_gl=1*p32nht*_gcl_au*ODEzODE4NzE2LjE3MTc0MTcxNzQ.*_ga*MTEyNTQ0MjIwMi4xNzIxMTI4MjY1*_ga_5LTL1CNEJM*MTcyMjAwNjUxMy4zNy4xLjE3MjIwMDY2MTguNjAuMC4w). Set up a specific model for Charmed PostgreSQL K8s named `tutorial`:

```shell
juju add-model tutorial
```

You can now view the model you created above by running the command `juju status`. You should see something similar to the following example output:

```shell
Model     Controller  Cloud/Region        Version  SLA          Timestamp
tutorial  charm-dev   microk8s/localhost  2.9.42   unsupported  11:56:38+01:00

Model "admin/tutorial" is empty.
```

>Tip: You can keep a separate terminal open running `juju status --watch 1s`. This will create a permanent status display that updates every second.

