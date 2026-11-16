# Implementation Steps

Each step lists the commands used and **why** they are needed. Steps 2–6 run on **all three
nodes**; steps 7–9 on the **Control Plane** only; step 10 on the **workers**.

> Commands follow the official kubeadm installation flow for Kubernetes v1.37 on an RPM-based
> distribution. Secrets (join token, CA hash) are replaced with placeholders.

## 1. Create three EC2 instances

| EC2 Name tag | Type | AMI | Private IP (from console) |
|---|---|---|---|
| eks-Control Plane | t3.medium | Amazon Linux 2023 | 10.0.11.65 (stated) |
| k8s-worker-01 | t3a.medium | Amazon Linux 2023 | 10.0.7.102 |
| k8s-worker-02 | t3a.medium | Amazon Linux 2023 | 10.0.13.238 |

> The worker IPs above come from the EC2 console and are the reverse of the inventory in the
> README — see the reconciliation note there. Both instance types (2 vCPU, 4 GiB) meet kubeadm
> minimums.

kubeadm's minimum for a control plane is **2 vCPU and 2 GB RAM**; workers need at least 2 GB.

## 2. Allow node-to-node communication (security group)

Allow the ports listed in [architecture.md → Required ports](architecture.md#required-ports-reference)
between the three instances. A common approach is a self-referencing rule on a shared security
group (source = the same security group).

## 3. Set hostnames (optional but recommended)

```bash
sudo hostnamectl set-hostname control-plane   # worker-01 / worker-02 on the workers
```

Readable node names make `kubectl get nodes` output meaningful.

## 4. Kernel modules and networking sysctls

```bash
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF
sudo sysctl --system
```

**Why:**

- `overlay` — the filesystem driver containerd uses for image layers.
- `br_netfilter` + `bridge-nf-call-iptables` — makes bridged Pod traffic visible to iptables,
  which kube-proxy relies on for Services.
- `ip_forward` — lets the node route packets between Pods and other nodes.

Swap must be off (kubelet refuses to start with swap by default). Amazon Linux 2023 EC2 AMIs
ship without swap; verify with `swapon --show` (empty output = no swap).

## 5. SELinux permissive

```bash
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config
```

**Why:** containers need to read host paths (for example Pod networking files). Permissive mode
is what the kubeadm documentation uses; it logs violations without blocking. In production you
would keep SELinux enforcing with proper policies.

## 6. Install and configure containerd

```bash
sudo dnf install -y containerd
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml > /dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo systemctl enable --now containerd
```

**Why `SystemdCgroup = true`:** the kubelet and the container runtime must use the **same cgroup
driver**. On systemd-based systems kubeadm configures the kubelet with the `systemd` driver;
if containerd uses `cgroupfs` instead, nodes become unstable (Pods restarting, control-plane
components crashing).

Verify:

```bash
grep SystemdCgroup /etc/containerd/config.toml
systemctl is-active containerd
```

## 7. Install kubeadm, kubelet and kubectl v1.37.2

```bash
cat <<EOF | sudo tee /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.37/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.37/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF

sudo dnf install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
sudo systemctl enable --now kubelet
kubeadm version
```

**Why `exclude=`:** prevents a routine `dnf update` from upgrading Kubernetes packages
unintentionally. Cluster upgrades must be done deliberately with `kubeadm upgrade`.

The kubelet will restart in a loop until `kubeadm init`/`join` gives it a configuration —
this is expected.

## 8. Initialise the Control Plane (control-plane only)

```bash
sudo kubeadm init \
  --apiserver-advertise-address=10.0.11.65 \
  --pod-network-cidr=10.244.0.0/16
```

> ⚠️ Confirm the exact flags you used. `10.244.0.0/16` is Flannel's default Pod CIDR; if a
> different CIDR was used, Flannel's ConfigMap must match it.

**What `kubeadm init` does:**

1. **Preflight checks** — swap, ports, runtime, cgroup driver.
2. **Certificates** — creates a cluster CA and certificates under `/etc/kubernetes/pki`.
3. **kubeconfig files** — for admin, kubelet, controller-manager and scheduler.
4. **Static Pod manifests** — API server, controller-manager, scheduler and etcd in
   `/etc/kubernetes/manifests`; the kubelet starts them.
5. **Taints the node** — `node-role.kubernetes.io/control-plane:NoSchedule`.
6. **Bootstrap token** — creates a short-lived token (24 h by default) for workers to join.
7. **Add-ons** — CoreDNS and kube-proxy.

## 9. Configure kubectl (control-plane only)

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
kubectl get nodes
```

At this point the control-plane node shows `NotReady` — there is no Pod network yet.

## 10. Install Flannel CNI (control-plane only)

```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
kubectl get pods -n kube-flannel
```

**What Flannel does:** runs a DaemonSet (one Pod per node) that allocates a Pod subnet to each
node and creates a VXLAN overlay so Pods on different nodes can reach each other. CoreDNS Pods
stay `Pending` until a CNI is installed — once Flannel is running they start.

## 11. Join the workers (worker-01 and worker-02)

```bash
sudo kubeadm join 10.0.11.65:6443 \
  --token <TOKEN> \
  --discovery-token-ca-cert-hash sha256:<CA_CERT_HASH>
```

If the token expired, generate a new command on the control plane:

```bash
kubeadm token create --print-join-command
```

**What `kubeadm join` does:**

1. Uses the **token** to authenticate to the API server.
2. Uses the **CA cert hash** to verify it is talking to the *real* control plane (protects
   against man-in-the-middle).
3. Performs TLS bootstrap — the kubelet requests its own client certificate.
4. The kubelet registers the node; Flannel and kube-proxy DaemonSets schedule onto it.

## 12. Verify the cluster

```bash
kubectl get nodes -o wide
kubectl get pods -A
```

Result achieved: **all three nodes `Ready`**.

## 13. Deploy Nginx with two replicas

```bash
kubectl create deployment nginx --image=nginx --replicas=2
kubectl get deployment nginx
kubectl get pods -o wide
```

> If you created the Deployment from a YAML manifest instead, commit that manifest under
> `manifests/` and reference it here — the imperative command above is the equivalent.

Result achieved: Deployment **2/2 Available**, both Pods **Running**, **one Pod on each
worker** (the control-plane taint kept them off the control plane; the scheduler spread them
across the two workers).

## 14. Expose Nginx with a NodePort Service

```bash
kubectl expose deployment nginx --type=NodePort --port=80
kubectl get svc nginx
```

Result achieved: Service created, nodePort **32170** (assigned from the 30000–32767 range).

## 15. Test access — ⏳ not yet confirmed

From inside the VPC (for example from the control plane):

```bash
curl -I http://10.0.13.238:32170
curl -I http://10.0.7.102:32170
```

From a browser:

```text
http://<WORKER_PUBLIC_IP>:32170
```

Requirements for the browser test:

- The worker instance has a public IP (or you go through a load balancer / bastion).
- The security group allows inbound **TCP 32170** — ideally **only from your own IP**.

Record the result (screenshot of the browser and of `kubectl get pods,svc -o wide`) in
`screenshots/` before marking this step complete.
