# Carousel Outline — Project 01 (1080 × 1350, 8 slides)

Visual identity: light background with subtle grid, navy `#0B2A5B`, electric blue `#1D4ED8`,
cyan `#06B6D4`, Inter typeface, MG mark top-left, slide number bottom-right.

| # | Title | Content | Visual |
|---|---|---|---|
| 1 | Building Kubernetes from the ground up | Project 01 · Self-managed cluster on AWS EC2 with kubeadm | MG mark, large headline, small 3-node icon |
| 2 | Why not just use EKS? | To understand what a managed service hides: runtime, certificates, control plane, networking | Two columns: "Managed hides" / "Self-managed exposes" |
| 3 | The architecture | 1 control plane + 2 workers · AL2023 · v1.37.2 · containerd · Flannel | `diagrams/architecture.png` (cropped) |
| 4 | Real infrastructure | 3 EC2 instances Running (t3.medium + 2 × t3a.medium) | `screenshots/00-ec2-instances-running.png` |
| 5 | Preparing the nodes | overlay + br_netfilter · ip_forward · SELinux permissive · `SystemdCgroup = true` | Code card with the 4 settings and one-line "why" each |
| 6 | Bootstrap: init → CNI → join | What `kubeadm init` creates; why nodes are NotReady until Flannel; what the join token and CA hash prove | 3-step horizontal flow |
| 7 | Workload & Service | Deployment 2/2 · one Pod per worker (control-plane taint) · NodePort 32170 | Pods on two workers + Service arrow; amber tag "browser test: next" |
| 8 | Lessons & next | 4 lessons · Next: browser verification, then Project 02 (ConfigMaps, Secrets, probes) | Checklist + GitHub link + "Learning by building." |

Add a real `kubectl get nodes -o wide` / `kubectl get pods -o wide` screenshot to slides 6–7
once captured — terminal evidence is stronger than illustrations.
