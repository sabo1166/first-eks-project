# Troubleshooting

## Errors actually encountered in this project

> **To be completed from real evidence.** No error logs from the build were available when this
> documentation was written, so nothing is listed here yet. Rather than invent issues, add each
> real one using the template below.

### Template

```markdown
### <Short error title>

**Symptom:** what you saw (exact error message, `kubectl` output)
**Where:** control plane / worker-01 / worker-02, which step
**Root cause:** why it happened
**Fix:** the command or change that resolved it
**Verification:** how you confirmed it was fixed
```

## Diagnostic reference (not errors from this build)

General kubeadm diagnostics worth knowing. These are reference material, **not** a record of
problems encountered.

| Symptom | Likely cause | Check |
|---|---|---|
| Node stays `NotReady` | No CNI installed, or CNI Pod failing on that node | `kubectl get pods -n kube-flannel -o wide`, `kubectl describe node <node>` |
| CoreDNS `Pending` | No Pod network yet | Install the CNI, then `kubectl get pods -n kube-system` |
| `kubeadm join` hangs or times out | Port 6443 blocked between worker and control plane | `nc -zv 10.0.11.65 6443` from the worker; check security group |
| `kubeadm join` token error | Token expired (24 h default) | `kubeadm token create --print-join-command` |
| kubelet crash-looping before init/join | Normal — kubelet has no config yet | `journalctl -u kubelet -f` after init/join |
| Control-plane Pods restarting | cgroup driver mismatch | `grep SystemdCgroup /etc/containerd/config.toml` must be `true` |
| Flannel Pod `CrashLoopBackOff` | Pod CIDR mismatch with `--pod-network-cidr`, or `br_netfilter` missing | `kubectl logs -n kube-flannel <pod>`, `lsmod \| grep br_netfilter` |
| Pods on different nodes can't reach each other | UDP 8472 blocked | Security group rules between nodes |
| NodePort not reachable from browser | No public IP, port 32170 not allowed inbound, or wrong IP | `kubectl get svc`, instance public IP, security group inbound rules |

## Useful commands

```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl describe pod <pod>
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get endpointslices -l kubernetes.io/service-name=nginx
journalctl -u kubelet --no-pager | tail -50
sudo crictl ps -a
```
