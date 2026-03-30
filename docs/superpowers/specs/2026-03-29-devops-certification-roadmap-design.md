# Junior → Senior DevOps: Linux Foundation Certification Roadmap

**Date:** 2026-03-29
**Author:** agungtguritno
**Goal:** Structured path from Junior DevOps (Linux/cloud ops background) to Senior Platform/SRE Engineer using Linux Foundation certifications as the primary framework.

---

## Context

**Starting point:**
- Strong Linux server operations background
- Cloud provider experience (AWS-focused)
- Some hands-on ECS and EKS (not day-to-day)
- Currently using `ck-x-simulator` for Kubernetes exam practice

**Target senior profile:** Kubernetes Platform Engineer + Cloud-Native DevOps + SRE/Reliability Engineer

**Pace model:**
- Start at Pace A (5–7h/week) to build sustainable habit
- Accelerate to Pace B (10–15h/week) once rhythm is established
- Accelerate to Pace C (20+h/week) for final push

---

## Overall Structure

Three sequential phases. Each phase maps to a pace level and a cluster of certifications.

| Phase | Certifications | Pace | Estimated Duration |
|-------|---------------|------|--------------------|
| 1 — Foundation | LFCS | A | 3–4 months |
| 2 — Kubernetes Core | CKA → CKAD → CKS | A→B | 9–12 months |
| 3 — Platform + Cloud-Native | ICA → CNPE + AWS parallel | B→C | 4–6 months |

**Total at full Pace A:** 18–22 months
**If Pace B by month 4:** 14–16 months
**If Pace C by month 8+:** 10–12 months

---

## Phase 1: Foundation — LFCS (Months 1–4)

### Purpose
Structured Linux mastery. Fills gaps that will surface as blockers in CKA — especially networking and storage internals.

### Exam Profile
- **Format:** Performance-based, 2 hours
- **Passing score:** 66%
- **Allowed resources:** Official documentation during exam

### Core Topics
| Topic | Why It Matters Later |
|-------|---------------------|
| File system, permissions, ACLs | Container volume mounts, security contexts |
| Systemd, process management | Container runtime, cgroup limits |
| Networking: routing, iptables, DNS | Kubernetes CNI, Services, NetworkPolicy |
| Storage: LVM, filesystems, mount points | PersistentVolumes, StorageClass |
| Shell scripting | Automation, exam speed |
| Package management (apt/yum) | Node setup, tooling in CKA |

### Practice Engine
- Killercoda Linux labs (free, browser-based)
- `ck-x-simulator` terminal environment for scripting practice
- Personal VM or cloud instance for destructive exercises (iptables, LVM)

### Exit Criteria
Pass LFCS **and** be able to explain without reference:
- How iptables chains process a packet
- How cgroups limit memory/CPU for a process
- How DNS resolution works (stub resolver → recursive → authoritative)
- How to mount a new disk, partition it, and add to fstab

---

## Phase 2: Kubernetes Core — CKA → CKAD → CKS (Months 4–16)

### Sequencing rationale
CKA must come first — it is a prerequisite for CKS and provides the cluster-level mental model that CKAD builds on. CKAD is faster to pass once CKA is solid. CKS is the Senior differentiator.

---

### CKA — Certified Kubernetes Administrator (Months 4–8)

**Exam profile:** Performance-based, 2 hours, 66% passing score, CKA-specific allowed docs

**Core domains:**
- Cluster architecture, installation, configuration (kubeadm)
- Workloads: Deployments, StatefulSets, DaemonSets, Jobs, CronJobs
- Services and networking: CNI, Services, Ingress, NetworkPolicy
- Storage: PV, PVC, StorageClass, dynamic provisioning
- Troubleshooting: node failures, pod failures, networking issues, etcd backup/restore
- RBAC: Roles, ClusterRoles, ServiceAccounts

**Practice engine:** `ck-x-simulator` daily — 45-minute timed sessions minimum 4x/week

**Senior signal this builds:** Can diagnose a broken cluster (failed node, misconfigured RBAC, network policy blocking traffic) without Googling fundamentals.

**Exit criteria:** Pass CKA + complete 3 full timed mock exams scoring 80%+ before sitting the real exam.

---

### CKAD — Certified Kubernetes Application Developer (Months 8–11)

**Exam profile:** Performance-based, 2 hours, 66% passing score

**Core domains:**
- Application design: multi-container pods (sidecar, init, ambassador patterns)
- Configuration: ConfigMaps, Secrets, environment variables
- Observability: liveness/readiness/startup probes, logging
- Resource management: requests, limits, LimitRange, ResourceQuota
- Services and networking: ClusterIP, NodePort, Ingress rules
- Helm basics: chart structure, values, templating

**Practice engine:** `ck-x-simulator` + Killercoda CKAD scenarios

**Senior signal this builds:** Can design a production-grade app deployment with proper resource constraints, health checks, and configuration management — not just "make it run."

---

### CKS — Certified Kubernetes Security Specialist (Months 11–16)

**Prerequisite:** Active CKA certification

**Exam profile:** Performance-based, 2 hours, 67% passing score

**Core domains:**
| Domain | Key Tools |
|--------|-----------|
| Cluster hardening | RBAC least privilege, API server flags, admission controllers |
| System hardening | AppArmor, seccomp, kernel hardening |
| Minimize microservice vulnerabilities | Pod Security Standards, OPA/Gatekeeper |
| Supply chain security | Image scanning (Trivy), signing, minimal base images |
| Monitoring, logging, runtime security | Falco, audit logging, immutable containers |
| Network policies | Ingress/egress rules, default deny patterns |

**Senior signal this builds:** This is the biggest Junior → Senior gap in platform engineering. Juniors deploy; seniors own the security posture. CKS forces you to think attacker-first.

---

## Phase 3: Platform + Cloud-Native — ICA → CNPE + AWS (Months 16–22)

### ICA — Istio Certified Associate (Months 16–19)

**Exam profile:** Multiple choice, 90 minutes

**Core topics:**
- Istio architecture: control plane (istiod), data plane (Envoy proxies)
- Traffic management: VirtualService, DestinationRule, Gateway
- Observability: distributed tracing (Jaeger), metrics (Prometheus), Kiali
- Security: mTLS, AuthorizationPolicy, PeerAuthentication
- Resilience: retries, timeouts, circuit breaking, canary deployments

**Why this matters for SRE:** Service mesh is how you get per-service SLOs, zero-downtime deployments, and automatic mTLS between services. ICA makes you dangerous at reliability work.

---

### CNPE — Cloud Native Platform Engineer (Months 19–22)

**Exam profile:** Performance-based

**Core topics:**
- GitOps: ArgoCD, Flux — declarative cluster state management
- CI/CD pipeline design: GitHub Actions, GitLab CI, Tekton
- Multi-cluster management and federation
- Platform engineering patterns: internal developer platforms, self-service
- Observability stack: Prometheus + Grafana + Loki + Tempo (full stack)
- Cost optimization and capacity planning

**Senior signal this builds:** CNPE is the credential that says "I don't just run Kubernetes — I build the platform other developers deploy onto."

---

### AWS Parallel Track (Pace C phase)

Start AWS certifications once CNPE is in progress — your EKS/ECS background means you're not starting from zero.

Recommended sequence:
1. **AWS SAA-C03** (Solutions Architect Associate) — validates cloud architecture breadth
2. **AWS DevOps Professional** or **AWS SAP-C02** — targets your exact Senior profile

---

## Beyond Certs: What Makes You Actually Senior

Certifications prove knowledge. The following prove seniority. Build these alongside the cert track:

| Skill | Tool to Learn | When to Start |
|-------|--------------|---------------|
| GitOps workflows | ArgoCD or Flux | During CKA |
| Infrastructure as Code | Terraform + Helm | During CKAD |
| Observability | Prometheus + Grafana + Loki | During CKS |
| Incident response | Runbooks, postmortems, SLO design | During ICA |
| CI/CD ownership | GitHub Actions or GitLab CI | During CNPE |
| Cost awareness | AWS Cost Explorer, Kubecost | During AWS track |

**The definitive Senior signal:** You receive an alert at 2am, SSH into a Kubernetes cluster, and within 15 minutes identify that a NetworkPolicy is blocking traffic between namespaces because a label selector is wrong — and you fix it without waking anyone else up. LFCS → CKA → CKS is the exact path that builds that muscle.

---

## Pace Acceleration Triggers

Move from Pace A to B when:
- You are completing weekly study sessions consistently without forcing it
- Mock exam scores are consistently above 75% before you sit the real exam
- You find yourself studying extra on weekends voluntarily

Move from Pace B to C when:
- You have passed CKA and your daily practice is automatic
- You have a clear 3–4 month window (no major life disruptions)
- CNPE + AWS track is in sight

---

## Resources

| Resource | Use Case |
|----------|----------|
| `ck-x-simulator` (this repo) | CKA/CKAD/CKS timed practice |
| Killercoda | Free browser labs for all certs |
| killer.sh | Official exam simulators (included with LF exam purchase) |
| Linux Foundation Training (LFT) | Official courses if needed |
| Kubernetes docs (kubernetes.io) | Primary reference during exams |
| Istio docs (istio.io) | ICA reference |
