# Screenshots

Real evidence only. Suggested files:

| File | Content |
|---|---|
| `01-nodes-ready.png` | `kubectl get nodes -o wide` |
| `02-flannel-pods.png` | `kubectl get pods -n kube-flannel -o wide` |
| `03-nginx-pods.png` | `kubectl get pods -o wide` (one Pod per worker) |
| `04-nginx-service.png` | `kubectl get svc nginx` (NodePort 32170) |
| `05-security-group.png` | Security group inbound rules |
| `06-browser-access.png` | Nginx welcome page via `<public-ip>:32170` (when verified) |

Before committing, blur public IPs, account IDs and any token/hash values.
