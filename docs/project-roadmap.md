# Project Roadmap — MG Kubernetes Engineering Series

## Project 01 — open items

Project 01 is **not closed** until these are done:

| # | Item | Why it matters |
|---|---|---|
| 1 | Verify Nginx through NodePort 32170 (first `curl` from inside the VPC, then a browser) | Proves the Service → Pod path end to end |
| 2 | Add real evidence to `screenshots/`: `kubectl get nodes -o wide`, `kubectl get pods -o wide`, `kubectl get svc`, security group rules, browser result | Credibility — every claim in the README should have proof |
| 3 | Record any real errors hit during the build in `troubleshooting.md` | Troubleshooting is the most valuable part of a portfolio project |
| 4 | Confirm the exact `kubeadm init` flags (Pod CIDR) and instance types | Docs must match what was actually run |
| 5 | Commit the Deployment/Service YAML (`kubectl get deploy,svc nginx -o yaml`, cleaned) | Reproducibility |
| 6 | Reconcile worker naming: EC2 `k8s-worker-01` = `10.0.7.102`, `k8s-worker-02` = `10.0.13.238` (reverse of the stated inventory) | Docs, diagram and node names must agree |
| 7 | Decide on the repository name (`first-eks-project` vs. e.g. `k8s-kubeadm-on-ec2`) | The name currently says EKS; the project is self-managed |

## Series plan (reviewed)

| # | Project | Builds on | Notes from review |
|---|---|---|---|
| 01 | Self-managed Kubernetes on EC2 with kubeadm | — | In progress (open items above) |
| 02 | Workloads, Services, ConfigMaps, Secrets, Health Probes | 01 | Use the same cluster; add readiness/liveness probes to Nginx and a small app |
| 03 | Ingress Controller, DNS, HTTPS/TLS | 02 | On a self-managed cluster the ingress controller is itself exposed via NodePort or an AWS NLB — a good lesson in what "LoadBalancer" means without a cloud controller |
| 04 | Persistent Volumes, StorageClasses, Stateful apps | 02 | Self-managed clusters have no default StorageClass; install the AWS EBS CSI driver (needs IAM on the nodes) or start with a local-path provisioner |
| 05 | Helm charts and reusable deployments | 02–04 | Needed before 07, since Prometheus/Grafana are normally installed via Helm |
| 06 | Autoscaling and resource management | 05 | Requires metrics-server; requests/limits, HPA, then Cluster Autoscaler later on EKS |
| 07 | Monitoring with Prometheus and Grafana | 05, 06 | kube-prometheus-stack via Helm |
| 08 | Centralized logging and troubleshooting | 07 | Loki or OpenSearch; correlate logs with metrics |
| 09 | **CI/CD with GitHub Actions** | 05 | **Suggested swap with 10:** build and push images first… |
| 10 | **GitOps with Argo CD** | 09 | …then let Argo CD deploy what CI produced. This is the natural pipeline order |
| 11 | Security: RBAC, NetworkPolicies, Pod Security | 02–10 | Flannel does not enforce NetworkPolicy — this project includes migrating to Calico or Cilium |
| 12 | Production-style Kubernetes platform on AWS | all | Strong candidate for **Amazon EKS with Terraform** — comparing managed vs. the self-managed cluster from Project 01 |

### Gap worth adding

**Day-2 operations** — `etcd` snapshot/restore and a `kubeadm upgrade` (e.g. v1.37 → v1.38).
These are core skills for self-managed clusters and are not covered by any project above. They
fit naturally as an extension of Project 01 or as part of Project 08.

## Rule for every project

Each project must include: real implementation, measurable verification, troubleshooting notes,
GitHub documentation and a LinkedIn content package. Project 02 does not start until Project 01's
open items are closed and reviewed.
