# Prahari AI — Judge FAQ

This document prepares the presentation team for potential questions from the Karnataka State Police Hackathon Judges.

### Q: Why did you choose Zoho Catalyst?
**A:** Zoho Catalyst was chosen for its enterprise-ready serverless capabilities. It allows us to seamlessly host our FastAPI backend via AppSail and Next.js frontend on Web Client Hosting without worrying about infrastructure scaling. It also provides built-in Object Storage for media evidence and native cron jobs for our scheduled AI sync tasks.

### Q: What is the scale of the dataset?
**A:** We generated a custom synthetic dataset of 100,000 cases representing decades of policing in Karnataka. This dataset isn't just rows in a CSV; it is fully relational, meaning people, vehicles, and communications are organically linked. This allows us to demonstrate true graph intelligence rather than simple mock data.

### Q: Why use both PostgreSQL and Neo4j?
**A:** Relational databases like PostgreSQL are excellent for transactional integrity (e.g., saving an FIR form without data corruption). However, detecting a crime syndicate requires traversing 5 to 6 degrees of separation (e.g., Person A called Person B, who shares an address with Person C, who was arrested for a crime involving Vehicle X). Neo4j executes these queries in milliseconds, whereas PostgreSQL would require highly inefficient recursive joins.

### Q: How does the AI model determine the "Risk Score"?
**A:** The AI Risk Engine uses a combination of temporal anomalies (crimes happening at unusual times), geospatial clustering (proximity to known gang territories in Karnataka), and semantic similarity (M.O. matching via Qdrant vector search). The model outputs a confidence score and explicitly lists the "Feature Importance," ensuring the AI is explainable to human officers.

### Q: How could Karnataka Police deploy this tomorrow?
**A:** The platform is already containerized via Docker and orchestrated for Zoho Catalyst AppSail. From an integration standpoint, our backend exposes standardized REST APIs, meaning existing CCTNS systems could push data directly into Prahari AI without disrupting current operations.
