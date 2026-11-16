# Architecture

## High-level view

```text
AWS Cloud (VPC, private addressing 10.0.x.x)
└── EC2-based Kubernetes cluster (kubeadm, v1.37.2)
    ├── Control Plane  10.0.11.65
    │   ├── kube-apiserver
    │   ├── kube-scheduler
    │   ├── kube-controller-manager
    │   ├── etcd
    │   └── kubelet + containerd
    ├── Worker 01      10.0.13.238
    │   ├── kubelet + containerd + kube-proxy
    │   └── nginx Pod (replica 1)
    ├── Worker 02      10.0.7.102
    │   ├── kubelet + containerd + kube-proxy
    │   └── nginx Pod (replica 2)
    └── Flannel CNI (DaemonSet on every node, VXLAN overlay)

Deployment "nginx" (replicas: 2) ──manages──▶ ReplicaSet ──▶ 2 Pods
Service (type NodePort, nodePort 32170) ──selects──▶ Pods with the nginx label
```

The editable diagram is in [`diagrams/architecture.mmd`](../diagrams/architecture.mmd); the
polished export is [`diagrams/architecture.svg`](../diagrams/architecture.svg).

## Control Plane vs Worker responsibilities

| Component | Runs on | Responsibility |
|---|---|---|
| `kube-apiserver` | Control Plane | The only entry point to the cluster. Validates requests, stores state in etcd. Everything — kubectl, kubelets, controllers — talks to it on port 6443. |
| `etcd` | Control Plane | Key-value store holding the entire cluster state (desired and observed). |
| `kube-scheduler` | Control Plane | Watches for Pods without a node and picks one, based on resources, taints, affinity and spreading. |
| `kube-controller-manager` | Control Plane | Runs reconciliation loops (Deployment, ReplicaSet, Node, ServiceAccount…) that drive actual state toward desired state. |
| `kubelet` | Every node | Node agent. Receives Pod specs from the API server and asks containerd to run the containers; reports node and Pod status. |
| `containerd` | Every node | Container runtime (via CRI). Pulls images and runs containers. |
| `kube-proxy` | Every node | Programs iptables/IPVS rules so Service IPs and NodePorts route to Pod endpoints. |
| Flannel | Every node | Assigns each node a Pod subnet and builds the overlay network between nodes. |

The control plane components run as **static Pods** managed by the kubelet from manifests in
`/etc/kubernetes/manifests/` — this is how kubeadm deploys them.

By default kubeadm taints the control-plane node with
`node-role.kubernetes.io/control-plane:NoSchedule`, which is why the Nginx replicas landed only
on the two workers.

## Networking layers

There are three different address spaces in this cluster — keeping them apart is the key to
understanding Kubernetes networking:

| Layer | Example | Provided by |
|---|---|---|
| Node IPs | `10.0.11.65`, `10.0.13.238`, `10.0.7.102` | AWS VPC subnets |
| Pod IPs | `10.244.x.y` (Flannel default — confirm the CIDR used at `kubeadm init`) | Flannel |
| Service IPs | `10.96.x.y` (kubeadm default service CIDR) | kube-apiserver / kube-proxy |

### How Pods talk across nodes (Flannel VXLAN)

1. Each node receives its own Pod subnet (for example `10.244.1.0/24` on Worker 01 and
   `10.244.2.0/24` on Worker 02).
2. A packet from a Pod on Worker 01 to a Pod on Worker 02 leaves the Pod through a veth pair
   into the `cni0` bridge.
3. The routing table sends traffic for the remote Pod subnet to the `flannel.1` VXLAN device.
4. Flannel encapsulates the packet in UDP (port **8472**) addressed to Worker 02's **node IP**.
5. Worker 02 decapsulates it and delivers it to the destination Pod.

This is why the security group must allow UDP 8472 between nodes.

## How the Deployment keeps two replicas

`Deployment (replicas: 2)` → creates a `ReplicaSet` → the ReplicaSet controller continuously
compares the number of matching Pods with the desired count. If a Pod is deleted or its node
fails, the controller creates a replacement and the scheduler places it on an available node.

## How the NodePort Service works

```text
Client ──▶ <Worker public IP>:32170
              │  kube-proxy rule (iptables) on that node
              ▼
        Service (ClusterIP + nodePort 32170)
              │  load-balances across endpoints
              ├──▶ nginx Pod on Worker 01 :80
              └──▶ nginx Pod on Worker 02 :80 (via Flannel if remote)
```

- A NodePort opens the **same port on every node** (range 30000–32767).
- Traffic hitting *any* node on 32170 is forwarded to one of the Service endpoints — even a
  Pod on another node.
- For a browser to reach it, the node needs a reachable (public) address **and** the security
  group must allow inbound TCP 32170 from the client. **This path has not yet been verified.**

## Required ports (reference)

| Port / Protocol | Direction | Purpose |
|---|---|---|
| TCP 6443 | Workers → Control Plane | Kubernetes API server |
| TCP 2379–2380 | Control Plane | etcd (local in this single-control-plane setup) |
| TCP 10250 | Control Plane ↔ all nodes | kubelet API |
| TCP 10257 / 10259 | Control Plane (local) | controller-manager / scheduler |
| UDP 8472 | All nodes ↔ all nodes | Flannel VXLAN |
| TCP 30000–32767 | Client → nodes | NodePort Services (32170 used here) |

> The security group was configured to allow node-to-node communication. The exact rule set
> used should be captured as a screenshot in `screenshots/` (see roadmap open items).
