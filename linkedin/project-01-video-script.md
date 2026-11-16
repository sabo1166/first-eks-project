# Video Script & Storyboard — Project 01

**Format:** 1080 × 1920 · 30 FPS · 60 s · H.264 MP4 · burned-in English captions + `.srt`
**Rendered file:** `linkedin/assets/project-01-linkedin-video.mp4`
**Source:** `linkedin/assets/video-source/scene.html` (deterministic `render(t)`), `render.py` (Playwright frames), ffmpeg encode.
**Audio:** none in this version — no text-to-speech engine was available. The narration below is ready to record.

| Time | Scene | On screen | Caption / narration |
|---|---|---|---|
| 0–5 s | 1 · Hook | "Building Kubernetes from the ground up." · MG mark · gradient bar | Building Kubernetes from the ground up — no managed service. |
| 5–9 s | 2 · Architecture | AWS/VPC frame; Control Plane, Worker 01, Worker 02 slide in | Three EC2 instances on Amazon Linux 2023: one control plane, two workers. |
| 9–13 s | 2 · Evidence | **Real EC2 console snapshot**: 3 instances Running (t3.medium + 2 × t3a.medium) | The real thing: all three instances running in my AWS account. |
| 13–19 s | 3 · Bootstrap | containerd chips (SystemdCgroup = true) on each node; `$ kubeadm init`; API Server, Scheduler, Controller Manager, etcd appear | containerd with systemd cgroups, kernel networking prep, kubeadm v1.37.2. |
| 19–25 s | 3 · Join + CNI | `$ kubeadm join` on both workers; API↔kubelet links; Flannel bar; three green **Ready** badges | kubeadm init, kubeadm join, and Flannel for Pod networking. All three nodes Ready. |
| 25–31.5 s | 4 · Workload | Deployment card `nginx · replicas: 2`; links drop to workers; Pods drop into Worker 01 and Worker 02 | An Nginx Deployment with two replicas… |
| 31.5–38 s | 4 · Status | Pods switch to **Running**; Deployment shows **2/2 Available** | …and the scheduler placed one Pod on each worker. 2/2 Available. |
| 38–43 s | 5 · Service | Service card `nginx · 32170 → 80`; client badge; traffic dots flow to both Pods | A NodePort Service on port 32170 routes traffic to both Pods. |
| 43–48 s | 5 · Honesty note | Amber badge: "External browser access: next verification step" | Next step: verify external browser access through the NodePort. |
| 48–60 s | 6 · Outro | Navy card: Project 01 title, status summary, MG, "Learning by building. Engineering through practice." | Project 01: Self-Managed Kubernetes on AWS EC2. |

## Re-rendering

```bash
cd linkedin/assets/video-source
python3 render.py /tmp/frames            # 1800 JPEG frames
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -c:v libx264 -preset veryfast -crf 18 \
       -pix_fmt yuv420p -movflags +faststart ../project-01-linkedin-video.mp4
```

Preview in a browser: open `scene.html?play`.

## Adding narration later

Record the caption lines above (≈ 130 words, calm pace), then:

```bash
ffmpeg -i project-01-linkedin-video.mp4 -i narration.wav -c:v copy -c:a aac -shortest out.mp4
```

When the browser test succeeds, change the 43–48 s badge and caption to the verified result
and re-render.
