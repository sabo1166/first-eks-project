# Lessons Learned

## Engineering takeaways

1. **A managed service hides a lot.** Building the cluster by hand made every layer visible:
   kernel modules, cgroups, container runtime, certificates, static Pods, CNI and kube-proxy.
2. **The runtime and kubelet must agree on cgroups.** `SystemdCgroup = true` is a one-line
   setting that decides whether the cluster is stable.
3. **A node is not `Ready` until it has networking.** Kubernetes does not ship a Pod network;
   the CNI (Flannel here) is a required component, not an add-on.
4. **The control plane is protected by a taint.** Workloads landed only on the workers because
   kubeadm taints the control-plane node `NoSchedule`.
5. **The scheduler spreads replicas.** With two equal workers, the two Nginx replicas landed on
   different nodes, which gives basic resilience to a single node failure.
6. **Creating a Service is not the same as reaching it.** The NodePort Service exists, but
   external access depends on AWS networking (public IP, security group) — a separate layer
   that still has to be verified.
7. **Three address spaces.** Node IPs (VPC), Pod IPs (Flannel) and Service IPs (cluster) are
   different networks; most networking confusion comes from mixing them up.

## Security considerations

| Area | Current state (lab) | Production practice |
|---|---|---|
| SELinux | Permissive | Enforcing with container policies |
| API server (6443) | Reachable between nodes | Never open to `0.0.0.0/0`; restrict to nodes and admin IPs, or use a private endpoint |
| NodePort | 32170 to be opened for testing | Only from your own IP for tests; use a LoadBalancer/Ingress with TLS for real traffic |
| Join token | 24 h default TTL | Keep TTL short; never commit tokens; delete unused tokens (`kubeadm token delete`) |
| `admin.conf` | Full cluster-admin credential | Never commit or share; create scoped RBAC users instead |
| Node access | — | Prefer SSM Session Manager over open SSH (port 22) |
| Network policy | None (Flannel does not enforce NetworkPolicy) | Use a CNI that enforces policies (e.g. Calico/Cilium) — planned for Project 11 |
| etcd | Unencrypted Secrets at rest by default | Enable encryption at rest for Secrets |

## Cost considerations

- Three EC2 instances run continuously while the cluster exists — **stop them when not
  practising**. A kubeadm cluster usually survives a stop/start, but private IPs must stay the
  same (they do for a stopped instance in the same subnet).
- Public IPv4 addresses are billed per hour on AWS; avoid assigning them to nodes that do not
  need them.
- EBS root volumes are billed even while instances are stopped.
- Check that no unused Elastic IPs, load balancers or volumes remain after experiments.

> Exact costs depend on the instance types chosen; record them in this file once confirmed.
