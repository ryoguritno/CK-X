# Junior → Senior DevOps Certification Roadmap — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Progress from Junior DevOps (Linux/cloud background) to Senior Platform/SRE Engineer through Linux Foundation certifications and hands-on practice.

**Architecture:** Three sequential phases — Foundation (LFCS) → Kubernetes Core (CKA → CKAD → CKS) → Platform (ICA → CNPE + AWS). Each phase builds directly on the previous. No skipping.

**Tech Stack:** Linux, Kubernetes, Istio, ArgoCD, Terraform, Helm, Prometheus/Grafana/Loki, GitHub Actions, AWS (EKS/ECS/IAM)

---

## Study Rhythm (apply to every task)

- **Pace A:** 5–7h/week — 2× weekday sessions (1h each) + 1× weekend session (3–5h)
- **Pace B:** 10–15h/week — 4× weekday sessions (1.5h each) + 1× weekend session (4–5h)
- **Pace C:** 20+h/week — daily 1.5–2h sessions + full weekend day

**Weekly ritual:**
- Monday: new concept introduction
- Wednesday: hands-on lab practice
- Saturday/Sunday: timed practice + review weak areas

---

## Phase 1: LFCS — Foundation (Months 1–4)

### Task 1: Study Environment Setup

**Resources:**
- `ck-x-simulator` — already available at `/home/agungtguritno/ck-x-simulator/`
- Killercoda account: https://killercoda.com (free, no install required)
- LFCS exam registration: https://training.linuxfoundation.org/certification/linux-foundation-certified-sysadmin-lfcs/

- [ ] **Step 1: Verify ck-x-simulator is running**

```bash
cd ~/ck-x-simulator
docker compose up -d
docker compose ps
```

Expected: all services `healthy` or `running`

- [ ] **Step 2: Create a study log file**

```bash
mkdir -p ~/study-log
cat > ~/study-log/progress.md << 'EOF'
# Study Log

## LFCS
- [ ] Week 1-2: Essential commands & file system
- [ ] Week 3-4: Process management & systemd
- [ ] Week 5-7: Networking fundamentals
- [ ] Week 8-9: Storage management
- [ ] Week 10-11: Shell scripting
- [ ] Week 12-16: Mock exams + LFCS exam

## CKA
## CKAD
## CKS
## ICA
## CNPE
EOF
```

- [ ] **Step 3: Create a Killercoda account and complete the "Linux Basics" playground**

Go to: https://killercoda.com/learn — complete the first Linux scenario to confirm environment works.

- [ ] **Step 4: Register for LFCS exam** (can do later, but register early — gives you 12 months to schedule)

---

### Task 2: Essential Commands & File System (Weeks 1–2)

**Topics:** File system hierarchy, navigation, permissions, ACLs, links, find, tar, compression

**Killercoda labs:**
- https://killercoda.com/learn — "Linux File System" scenarios
- Search "LFCS" on Killercoda for dedicated practice scenarios

- [ ] **Step 1: Study file system hierarchy — know each directory's purpose**

Run this on any Linux system and verify you can explain every line:
```bash
ls -la /
# Explain: /proc, /sys, /run, /dev, /etc, /var, /usr, /opt, /home, /tmp
```

- [ ] **Step 2: Practice permissions until automatic**

```bash
# Create test files and practice chmod/chown
mkdir ~/perm-practice
touch ~/perm-practice/{file1,file2,file3}

# Set permissions symbolically and numerically — know both
chmod u+x,g+r,o-rwx ~/perm-practice/file1
chmod 754 ~/perm-practice/file2

# Set ACLs (exam tests this)
setfacl -m u:nobody:rx ~/perm-practice/file1
getfacl ~/perm-practice/file1
```

- [ ] **Step 3: Practice find command (heavily tested)**

```bash
# Find files modified in last 24h
find /var/log -mtime -1 -type f

# Find files larger than 100MB
find / -size +100M -type f 2>/dev/null

# Find SUID binaries (security relevance for CKS later)
find / -perm -4000 -type f 2>/dev/null
```

- [ ] **Step 4: Complete 1 Killercoda LFCS scenario and score 100%**

- [ ] **Step 5: Verify mastery — answer these without looking anything up:**
  - What is the difference between a hard link and a symbolic link?
  - What does permission `2755` mean?
  - How do you find all files owned by user `www-data`?

---

### Task 3: Process Management & Systemd (Weeks 3–4)

**Topics:** systemd units, journald, ps/top/htop, kill signals, nice/renice, cgroups (critical for Kubernetes later)

- [ ] **Step 1: Master systemd service management**

```bash
# These commands must be muscle memory
systemctl status sshd
systemctl start/stop/restart/enable/disable sshd
systemctl list-units --type=service --state=running
systemctl daemon-reload  # after editing unit files

# View and follow logs
journalctl -u sshd -f
journalctl --since "1 hour ago"
journalctl -p err  # errors only
```

- [ ] **Step 2: Create a custom systemd service (exam task type)**

```bash
cat > /etc/systemd/system/myapp.service << 'EOF'
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m http.server 8080
Restart=on-failure
User=nobody

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now myapp.service
systemctl status myapp.service
```

- [ ] **Step 3: Understand cgroups (this directly maps to Kubernetes resource limits)**

```bash
# View cgroup hierarchy
ls /sys/fs/cgroup/

# View memory limit for a process
cat /proc/$(pgrep sshd | head -1)/cgroup

# Create a cgroup and apply memory limit (conceptual — understand the mechanism)
# cgcreate -g memory:/mygroup
# echo $((256*1024*1024)) > /sys/fs/cgroup/memory/mygroup/memory.limit_in_bytes
```

- [ ] **Step 4: Verify mastery — answer without looking:**
  - How do you find which process is using the most CPU?
  - What signal does `kill` send by default? What does SIGKILL do differently from SIGTERM?
  - What is the relationship between systemd cgroups and Kubernetes resource limits?

---

### Task 4: Networking Fundamentals (Weeks 5–7)

**Topics:** IP addressing, routing, iptables, DNS, SSH tunneling, firewalld/ufw

**Why 3 weeks:** Networking is the most tested area in LFCS and the most critical for CKA. Do not rush this.

- [ ] **Step 1: Master IP and routing commands**

```bash
# View interfaces and IPs
ip addr show
ip link show

# View routing table
ip route show

# Add a static route (exam task)
ip route add 192.168.2.0/24 via 192.168.1.1 dev eth0

# Test connectivity
ping -c 3 8.8.8.8
traceroute 8.8.8.8
```

- [ ] **Step 2: Understand iptables (this IS Kubernetes networking)**

```bash
# View all rules
iptables -L -n -v

# View NAT table (how Kubernetes Services work)
iptables -t nat -L -n -v

# Add a rule to accept traffic on port 8080
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Drop all traffic from an IP
iptables -A INPUT -s 10.0.0.5 -j DROP

# Save rules (persist across reboots)
iptables-save > /etc/iptables/rules.v4
```

- [ ] **Step 3: Understand DNS resolution chain**

```bash
# View DNS config
cat /etc/resolv.conf
cat /etc/hosts
cat /etc/nsswitch.conf  # controls resolution order

# Trace DNS resolution
dig google.com +trace
nslookup kubernetes.default.svc.cluster.local  # (will be used heavily in CKA)

# Test from inside ck-x-simulator
# The cluster DNS will be at 10.96.0.10 (CoreDNS)
```

- [ ] **Step 4: Practice SSH tunneling (exam task type)**

```bash
# Local port forward: access remote service via local port
ssh -L 8080:localhost:80 user@remote-host

# Dynamic SOCKS proxy
ssh -D 1080 user@remote-host
```

- [ ] **Step 5: Complete the Killercoda "Linux Networking" scenarios**

- [ ] **Step 6: Verify mastery — answer without looking:**
  - A packet arrives on `eth0` destined for port 80. Walk through the iptables chains it traverses.
  - What is the difference between `/etc/resolv.conf` and `/etc/hosts`?
  - How does Kubernetes use iptables to implement Services? (high-level answer is fine now)

---

### Task 5: Storage Management (Weeks 8–9)

**Topics:** LVM, filesystems (ext4, xfs), mounting, fstab, swap

- [ ] **Step 1: LVM workflow — create PV → VG → LV → filesystem**

```bash
# This is the exact workflow for exam tasks
# Assume /dev/sdb is a new disk

# Create physical volume
pvcreate /dev/sdb
pvdisplay

# Create volume group
vgcreate myvg /dev/sdb
vgdisplay

# Create logical volume (10GB)
lvcreate -L 10G -n mylv myvg
lvdisplay

# Create filesystem
mkfs.ext4 /dev/myvg/mylv

# Mount
mkdir /data
mount /dev/myvg/mylv /data

# Persist across reboots
echo '/dev/myvg/mylv /data ext4 defaults 0 2' >> /etc/fstab
mount -a  # verify fstab is valid before rebooting
```

- [ ] **Step 2: Extend an LV (common exam task)**

```bash
# Add more space to existing LV
lvextend -L +5G /dev/myvg/mylv

# Resize the filesystem to use new space
resize2fs /dev/myvg/mylv  # ext4
# xfs_growfs /data  # for XFS filesystems
```

- [ ] **Step 3: Verify mastery — answer without looking:**
  - What is the difference between a PV, VG, and LV?
  - How does LVM map conceptually to Kubernetes PersistentVolumes?
  - What does `mount -a` do and why is it important to run before rebooting?

---

### Task 6: Shell Scripting (Weeks 10–11)

**Topics:** bash scripting, loops, conditionals, functions, cron jobs, text processing (awk, sed, grep)

- [ ] **Step 1: Write a health check script (exam-style task)**

```bash
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash

SERVICE=$1
if [ -z "$SERVICE" ]; then
  echo "Usage: $0 <service-name>"
  exit 1
fi

if systemctl is-active --quiet "$SERVICE"; then
  echo "OK: $SERVICE is running"
  exit 0
else
  echo "CRITICAL: $SERVICE is NOT running"
  systemctl start "$SERVICE"
  exit 1
fi
EOF
chmod +x /usr/local/bin/health-check.sh
```

- [ ] **Step 2: Write a log parser (awk/sed practice)**

```bash
# Count HTTP status codes in nginx log
awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Extract lines between two timestamps
sed -n '/2026-03-29 10:00/,/2026-03-29 11:00/p' /var/log/syslog

# Find failed SSH logins
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn
```

- [ ] **Step 3: Create a cron job**

```bash
# Edit crontab
crontab -e

# Add: run health-check every 5 minutes, log output
*/5 * * * * /usr/local/bin/health-check.sh nginx >> /var/log/health-check.log 2>&1

# Verify
crontab -l
```

---

### Task 7: LFCS Mock Exams & Exam (Weeks 12–16)

- [ ] **Step 1: Complete all available Killercoda LFCS scenarios**

Go to: https://killercoda.com — search "LFCS" — complete every available scenario. Target: 100% on all.

- [ ] **Step 2: Complete killer.sh LFCS simulator** (included with LFCS exam purchase)

Score target: **70%+ before sitting the real exam**. If below 70%, identify weak areas and return to the relevant task above.

- [ ] **Step 3: Run a timed full mock exam (120 minutes, no pausing)**

Simulate real exam conditions: no notes, only kubernetes.io/docs and man pages allowed.

- [ ] **Step 4: Schedule and sit the LFCS exam**

- [ ] **Step 5: After passing — update study log**

```bash
sed -i 's/- \[ \] Week 1-2: Essential commands/- [x] Week 1-2: Essential commands/' ~/study-log/progress.md
# Update all LFCS items as complete
```

**Pace acceleration check:** If you hit Pace B naturally during LFCS prep, continue at Pace B for CKA.

---

## Phase 2: CKA — Certified Kubernetes Administrator (Months 4–8)

### Task 8: Kubernetes Environment Setup

- [ ] **Step 1: Start ck-x-simulator and verify cluster is healthy**

```bash
cd ~/ck-x-simulator
docker compose up -d
docker compose ps
# All services must be healthy before practicing
```

- [ ] **Step 2: Verify kubectl access**

```bash
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

Expected: cluster info displayed, nodes in `Ready` state, system pods running.

- [ ] **Step 3: Set up kubectl aliases (exam speed)**

```bash
cat >> ~/.bashrc << 'EOF'
alias k=kubectl
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"
complete -F __start_kubectl k
EOF
source ~/.bashrc

# Test: these two commands must produce identical output
kubectl get pods
k get pods
```

- [ ] **Step 4: Configure vim for YAML editing (critical for exam)**

```bash
cat >> ~/.vimrc << 'EOF'
set expandtab
set tabstop=2
set shiftwidth=2
set autoindent
EOF
```

---

### Task 9: Core Workloads (Weeks 1–4 of CKA)

**Topics:** Pods, Deployments, StatefulSets, DaemonSets, Jobs, CronJobs, ReplicaSets

- [ ] **Step 1: Create resources imperatively (exam speed technique)**

```bash
# Pod
k run nginx --image=nginx --dry-run=client -o yaml > pod.yaml
k apply -f pod.yaml

# Deployment
k create deployment myapp --image=nginx --replicas=3 $do > deploy.yaml
k apply -f deploy.yaml

# Job
k create job myjob --image=busybox $do -- sh -c "echo hello" > job.yaml
k apply -f job.yaml

# CronJob
k create cronjob mycron --image=busybox --schedule="*/5 * * * *" $do -- sh -c "echo hello" > cron.yaml
k apply -f cron.yaml
```

- [ ] **Step 2: Practice rollouts**

```bash
k set image deployment/myapp nginx=nginx:1.21
k rollout status deployment/myapp
k rollout history deployment/myapp
k rollout undo deployment/myapp
```

- [ ] **Step 3: Complete ck-x-simulator workloads section**

Open http://localhost:30080 — navigate to workloads tasks — complete all with score 100%.

---

### Task 10: Services & Networking (Weeks 5–7 of CKA)

**Topics:** ClusterIP, NodePort, LoadBalancer, Ingress, NetworkPolicy, CoreDNS, CNI

- [ ] **Step 1: Create and test all Service types**

```bash
# Expose a deployment
k expose deployment myapp --port=80 --target-port=80 --type=ClusterIP $do > svc.yaml
k apply -f svc.yaml

# Test DNS resolution from within cluster
k run tmp --image=busybox --rm -it --restart=Never -- nslookup myapp
# Expected: resolves to ClusterIP

# NodePort
k expose deployment myapp --port=80 --type=NodePort $do
```

- [ ] **Step 2: Write a NetworkPolicy (most missed topic in CKA)**

```yaml
# deny-all-ingress.yaml — default deny pattern
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

```yaml
# allow-from-frontend.yaml — allow specific ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-frontend
  namespace: default
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

```bash
k apply -f deny-all-ingress.yaml
k apply -f allow-from-frontend.yaml
# Test: frontend pod can reach backend; other pods cannot
```

- [ ] **Step 3: Verify mastery — answer without looking:**
  - A pod cannot reach a Service by name. Walk through your debugging steps.
  - What iptables rule does Kubernetes create for a ClusterIP Service?
  - What is the difference between a NetworkPolicy `podSelector: {}` and omitting `podSelector`?

---

### Task 11: Storage (Weeks 8–9 of CKA)

**Topics:** PersistentVolume, PersistentVolumeClaim, StorageClass, dynamic provisioning, volume types

- [ ] **Step 1: Create PV → PVC → Pod workflow**

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mypv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/mypv
```

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mypvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```yaml
# pod-with-pvc.yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-storage
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /data
      name: storage
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: mypvc
```

```bash
k apply -f pv.yaml -f pvc.yaml -f pod-with-storage.yaml
k get pv,pvc
# PVC status must be: Bound
```

---

### Task 12: Cluster Administration (Weeks 10–12 of CKA)

**Topics:** kubeadm, etcd backup/restore, RBAC, node management, certificates

- [ ] **Step 1: etcd backup (guaranteed exam task)**

```bash
# Get etcd connection details
k describe pod etcd-controlplane -n kube-system | grep -E "listen-client|cert|key|trusted"

# Backup
ETCDCTL_API=3 etcdctl snapshot save /tmp/etcd-backup.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status /tmp/etcd-backup.db --write-out=table
```

- [ ] **Step 2: RBAC — create Role, RoleBinding, ClusterRole**

```bash
# Create Role (namespace-scoped)
k create role pod-reader --verb=get,list,watch --resource=pods $do > role.yaml

# Create ServiceAccount
k create serviceaccount mysa $do > sa.yaml

# Bind them
k create rolebinding mysa-pod-reader --role=pod-reader --serviceaccount=default:mysa $do > rb.yaml

k apply -f role.yaml -f sa.yaml -f rb.yaml

# Verify
k auth can-i list pods --as=system:serviceaccount:default:mysa
# Expected: yes
k auth can-i delete pods --as=system:serviceaccount:default:mysa
# Expected: no
```

- [ ] **Step 3: Drain and uncordon a node**

```bash
# Safely evict all pods from a node
k drain node01 --ignore-daemonsets --delete-emptydir-data

# Bring node back
k uncordon node01
```

---

### Task 13: Troubleshooting (Weeks 13–14 of CKA)

**Topics:** Pod failures, node failures, networking issues, cluster component failures

- [ ] **Step 1: Pod troubleshooting checklist — memorize this order**

```bash
# 1. Check pod status
k get pod mypod -o wide

# 2. Describe for events
k describe pod mypod

# 3. Check logs
k logs mypod
k logs mypod --previous  # crashed container

# 4. Exec into running pod
k exec -it mypod -- sh

# 5. Check node
k describe node $(k get pod mypod -o jsonpath='{.spec.nodeName}')
```

- [ ] **Step 2: Node troubleshooting checklist**

```bash
# 1. Check node status
k get nodes
k describe node node01

# 2. SSH to node
ssh node01

# 3. Check kubelet
systemctl status kubelet
journalctl -u kubelet -f

# 4. Check container runtime
systemctl status containerd
crictl ps
```

- [ ] **Step 3: Complete ck-x-simulator troubleshooting section**

Open http://localhost:30080 — navigate to troubleshooting tasks — complete all. These are the closest to real exam difficulty.

---

### Task 14: CKA Mock Exams & Exam (Weeks 15–16)

- [ ] **Step 1: Complete 3 full timed sessions in ck-x-simulator (120 min each)**

Target: score 80%+ on all three before scheduling.

- [ ] **Step 2: Complete killer.sh CKA simulator** (2 attempts included with exam purchase)

Score target: 70%+ before sitting. killer.sh is harder than the real exam.

- [ ] **Step 3: Review all tasks you missed — understand WHY, not just the fix**

- [ ] **Step 4: Schedule and sit the CKA exam**

- [ ] **Step 5: After passing — begin CKAD immediately (knowledge is hot)**

---

### Task 15: CKAD (Months 8–11)

**Topics:** Multi-container patterns, probes, resource limits, ConfigMaps, Secrets, Helm

- [ ] **Step 1: Multi-container pod patterns**

```yaml
# Sidecar pattern — log forwarder alongside main app
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: logs
      mountPath: /var/log/nginx
  - name: log-forwarder
    image: busybox
    command: ["sh", "-c", "tail -f /logs/access.log"]
    volumeMounts:
    - name: logs
      mountPath: /logs
  volumes:
  - name: logs
    emptyDir: {}
```

- [ ] **Step 2: Probes — liveness, readiness, startup**

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 3
```

- [ ] **Step 3: Resource limits (maps directly to cgroups from LFCS)**

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

- [ ] **Step 4: ConfigMap and Secret injection**

```bash
# Create ConfigMap
k create configmap myconfig --from-literal=DB_HOST=postgres --from-literal=DB_PORT=5432

# Create Secret
k create secret generic mysecret --from-literal=DB_PASSWORD=s3cr3t

# Reference in pod
k run myapp --image=nginx $do > pod.yaml
# Add envFrom to spec manually:
# envFrom:
# - configMapRef:
#     name: myconfig
# - secretRef:
#     name: mysecret
```

- [ ] **Step 5: Basic Helm usage**

```bash
# Install chart
helm repo add stable https://charts.helm.sh/stable
helm install myrelease stable/nginx --set replicaCount=2

# List, upgrade, rollback
helm list
helm upgrade myrelease stable/nginx --set replicaCount=3
helm rollback myrelease 1

# Template rendering (debug)
helm template myrelease stable/nginx --set replicaCount=2
```

- [ ] **Step 6: Complete killer.sh CKAD simulator — score 70%+ then sit exam**

---

### Task 16: CKS — Kubernetes Security Specialist (Months 11–16)

**Prerequisite:** Active CKA certification (valid 3 years)

- [ ] **Step 1: Pod Security Standards**

```yaml
# Enforce restricted profile on a namespace
apiVersion: v1
kind: Namespace
metadata:
  name: secure-ns
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

- [ ] **Step 2: NetworkPolicy — default deny pattern (CKS exam staple)**

```yaml
# deny-all-egress.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-egress
  namespace: secure-ns
spec:
  podSelector: {}
  policyTypes:
  - Egress
```

```bash
# Apply to every namespace: deny all, then explicitly allow
k apply -f deny-all-ingress.yaml -n secure-ns
k apply -f deny-all-egress.yaml -n secure-ns
# Then add specific allow policies per service
```

- [ ] **Step 3: RBAC audit — least privilege check**

```bash
# Find overly permissive roles
k get clusterrolebindings -o json | jq '.items[] | select(.subjects[]?.name == "system:anonymous")'

# Check what a ServiceAccount can do
k auth can-i --list --as=system:serviceaccount:default:mysa
```

- [ ] **Step 4: Falco — runtime security**

```bash
# Install Falco (exam environment will have it)
# Write a custom rule
cat > /etc/falco/rules.d/custom.yaml << 'EOF'
- rule: Terminal shell in container
  desc: A shell was spawned inside a container
  condition: >
    spawned_process
    and container
    and shell_procs
  output: >
    Shell spawned in container (user=%user.name container=%container.name
    image=%container.image.repository:%container.image.tag)
  priority: WARNING
EOF
systemctl restart falco
```

- [ ] **Step 5: Image scanning with Trivy**

```bash
# Scan an image for vulnerabilities
trivy image nginx:latest

# Scan only HIGH and CRITICAL
trivy image --severity HIGH,CRITICAL nginx:latest

# Scan a running cluster
trivy k8s --report summary cluster
```

- [ ] **Step 6: AppArmor profile for a pod**

```bash
# Load an AppArmor profile
apparmor_parser -r -W /etc/apparmor.d/myprofile

# Apply to pod via annotation
# annotations:
#   container.apparmor.security.beta.kubernetes.io/mycontainer: localhost/myprofile
```

- [ ] **Step 7: Complete killer.sh CKS simulator — score 67%+ then sit exam**

---

## Phase 3: Platform + Cloud-Native (Months 16–22)

### Task 17: ICA — Istio Certified Associate (Months 16–19)

- [ ] **Step 1: Install Istio on ck-x-simulator cluster**

```bash
curl -L https://istio.io/downloadIstio | sh -
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
```

- [ ] **Step 2: Traffic management — canary deployment**

```yaml
# VirtualService: 90% stable, 10% canary
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: myapp
spec:
  hosts:
  - myapp
  http:
  - route:
    - destination:
        host: myapp
        subset: stable
      weight: 90
    - destination:
        host: myapp
        subset: canary
      weight: 10
```

- [ ] **Step 3: Enable mTLS**

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```

- [ ] **Step 4: Sit ICA exam after completing official Istio docs labs**

---

### Task 18: CNPE + GitOps (Months 19–22)

- [ ] **Step 1: Install ArgoCD**

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

- [ ] **Step 2: Deploy an application via GitOps**

```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourname/k8s-manifests
    targetRevision: HEAD
    path: apps/myapp
  destination:
    server: https://kubernetes.default.svc
    namespace: myapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

- [ ] **Step 3: Set up observability stack**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3000:80
# Default login: admin / prom-operator
```

- [ ] **Step 4: Sit CNPE exam**

---

### Task 19: AWS Parallel Track (Pace C — Months 19–22)

- [ ] **Step 1: Register for AWS SAA-C03 (Solutions Architect Associate)**

Practice: AWS free tier + AWS Skill Builder labs

- [ ] **Step 2: Focus on EKS and ECS depth** (your existing experience is a head start)

```bash
# EKS-specific practice
aws eks create-cluster --name mycluster --region us-east-1 \
  --kubernetes-version 1.29 \
  --role-arn arn:aws:iam::ACCOUNT:role/eksClusterRole \
  --resources-vpc-config subnetIds=subnet-xxx,securityGroupIds=sg-xxx

# ECS task definition practice
aws ecs register-task-definition --cli-input-json file://task-def.json
```

- [ ] **Step 3: After SAA-C03 — target AWS DevOps Professional**

---

## Pace Acceleration Triggers

| Check | If true → do this |
|-------|------------------|
| Completing weekly sessions without forcing | Move to Pace B |
| Mock exam scores consistently 80%+ | Sit the real exam within 2 weeks |
| Finding yourself studying extra on weekends | You're already at Pace B — acknowledge it |
| Passed CKA, daily practice feels automatic | Move to Pace C |

---

## Senior Signal Milestones

Track these alongside certs — they signal real Senior-level capability:

- [ ] Diagnosed a pod networking issue in ck-x-simulator without using any notes
- [ ] Built a complete GitOps pipeline (code push → ArgoCD sync → production)
- [ ] Written a Falco rule that caught a real unexpected behavior in your cluster
- [ ] Designed an SLO for a Kubernetes-hosted service with error budget policy
- [ ] Onboarded a junior engineer by walking them through a cluster architecture
