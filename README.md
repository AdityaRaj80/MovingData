# MovingData - Intelligent Multi-Cloud Data Pipeline

## Overview
MovingData is a secure, intelligent multi-cloud data management system designed to simulate data-in-motion across distributed storage environments.  
It dynamically analyzes, encrypts, and moves data between MinIO (S3), Azurite (Azure Blob), and FakeGCS (GCP) - ensuring encryption-at-rest, encryption-in-transit, and predictive automation.

Built for the NetApp "Data-in-Motion" Hackathon, this project demonstrates adaptive data orchestration, Kafka-based event streaming, and intelligent storage policy enforcement.

## Problem Statement
Organizations increasingly face challenges in handling distributed, multi-cloud data efficiently - requiring real-time responsiveness, security, and cost optimization.  
This project provides a prototype that automates data tiering, replicates files across multiple storages, integrates Kafka streaming, and enforces encryption at every layer.

## Architecture
| Layer | Component | Description |
|-------|------------|-------------|
| API Layer | FastAPI | Handles encryption, migration logic, and APIs |
| UI Layer | Streamlit | Dashboard to visualize data movement |
| Data Plane | Redpanda (Kafka) | Simulates data in motion |
| Storage | MinIO, Azurite, FakeGCS | Simulated AWS, Azure, GCP |
| Database | MongoDB | Stores metadata and policy logs |
| Encryption | Fernet + SSE-KMS | Dual-layered protection |

## Key Features
- Application-level Fernet (AES) encryption before upload  
- MinIO KMS (SSE-KMS) encryption-at-rest  
- Multi-cloud replication verified by SHA checksum  
- Real-time streaming via Redpanda  
- Fully containerized setup using Docker Compose  

## How to Run (Local)
```bash
git clone https://github.com/AdityaRaj80/MovingData.git
cd MovingData/infra
docker compose up -d --build
```
Access:
- FastAPI → http://localhost:8001/docs  
- Streamlit → http://localhost:8501  

## Verification
```bash
docker exec -it infra-minio-1 sh -lc "mc admin kms key status local"
docker exec -it infra-minio-1 sh -lc "mc stat local/netapp-bucket/file_001.txt"
```

## Achievements
| Layer | Mechanism | Verified |
|-------|------------|-----------|
| Application | Fernet (AES-128-GCM) | ✔ |
| Storage | SSE-KMS (MinIO) | ✔ |
| Network | Docker bridge | ✔ |
| Streaming | Redpanda | ✔ |

## Future Scope
- ML-based policy engine for predictive tiering  
- Integration with real cloud APIs  
- Kubernetes orchestration  
- Cost-aware storage optimization  

## Team
- Pranak Shah (2022B2A71344P)  
- Aditya Raj (2022B2A41583P)  
- Kush Natani (2022B4AA1288P)  
- Dhruv Gupta (2022A3PS1206P)

**MovingData - Redefining Secure Data in Motion**
