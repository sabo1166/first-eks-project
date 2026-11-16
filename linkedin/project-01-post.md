# LinkedIn Post — Project 01 (draft for review, not published)

**Attach:** `linkedin/assets/project-01-linkedin-video.mp4` (upload `project-01-subtitles.srt` as captions)

---

I built a Kubernetes cluster without a managed service — to see what EKS and friends actually hide.

Project 01 of my Kubernetes engineering series: a self-managed cluster on AWS EC2, bootstrapped with kubeadm.

🔧 What I built
• 3 EC2 instances on Amazon Linux 2023 — 1 control plane, 2 workers
• containerd as the runtime, configured with SystemdCgroup = true
• Kernel prep: overlay + br_netfilter, IP forwarding, bridged traffic visible to iptables
• kubeadm, kubelet and kubectl v1.37.2
• kubeadm init on the control plane, kubeadm join on both workers
• Flannel CNI for the Pod network (VXLAN overlay)
• An Nginx Deployment with 2 replicas, exposed through a NodePort Service (32170)

✅ Verified
• All 3 nodes Ready
• Deployment 2/2 Available, both Pods Running
• The scheduler placed one Pod on each worker — the control-plane taint kept workloads off the control plane

💡 What I learned
• The kubelet and the container runtime must agree on the cgroup driver — one line in config.toml decides whether the cluster is stable.
• A node isn't Ready until it has a Pod network. The CNI isn't optional.
• Node IPs, Pod IPs and Service IPs are three different networks. Most of my confusion came from mixing them up.
• Creating a Service and reaching it are two different things. The NodePort exists, but external access also depends on AWS networking (public IP + security group).

⏭️ What's next
Verifying browser access through the NodePort, documenting it with evidence, then Project 02: ConfigMaps, Secrets and health probes on the same cluster.

Full documentation, commands and architecture diagram on GitHub:
🔗 github.com/sabo1166/first-eks-project

Learning by building. Engineering through practice.

#Kubernetes #AWS #DevOps #CloudEngineering #kubeadm #containerd #CloudNative #PlatformEngineering #LearningInPublic
