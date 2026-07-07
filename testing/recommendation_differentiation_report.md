# CareerCompass AI — Recommendation Differentiation Report

This report analyzes the differentiation and personalization quality of SDE recommendations, timeline roadmaps, and skill gap prioritization across three candidate profiles.

## 1. Profiles Comparison Table

| Attribute | Alice (Beginner) | Bob (Intermediate) | Charlie (Advanced) |
| --- | --- | --- | --- |
| **Career Stage** | Foundational / Early Explorer | Advanced / Pre-Placement | Transitioning Professional |
| **Overall Readiness** | 8% | 45% | 87% |
| **Company Fit Score** | 18.5% | 25.9% | 47.1% |
| **Top 10 Missing Skills** | DSA (Combined), DBMS, Operating Systems, Computer Networks, Spring Boot, System Design, SQL, Object Oriented Programming, REST APIs, MySQL | Java, DSA (Combined), DBMS, Operating Systems, Computer Networks, Spring Boot, System Design, Object Oriented Programming, REST APIs, MySQL | Git & GitHub, AWS Basics, Linux Basics, Python, Operating Systems, Computer Networks, Message Queues (Kafka), System Design |
| **Top 5 Recommendations** | REST APIs, SQL, Git & GitHub, Object Oriented Programming, Custom Data Structure Library | REST APIs, Object Oriented Programming, Custom Data Structure Library, DSA (Combined), Production SDE Project #66: Android Application | System Design, Log Aggregation & Search Pipeline, Complete Python Beginner's Playlist 2026, Python Certification & Production Architecture, Python |
| **Top 3 Similar Engineers** | Google - Software Development Engineer (SDE), Google - Software Development Engineer (SDE), No Experience (Fresher) - Software Development Engineer (SDE) | Blinkit - Backend Developer, Codezee Solutions Private Limited - Backend Developer, Mudunuru Group - Backend Developer | Blinkit - Software Development Engineer (SDE), Swiggy - Software Development Engineer (SDE), QURILO TECHNOLOGIES LLC - Software Development Engineer (SDE) |
| **Roadmap Timeline** | 48 Months | 18 Months | 12 Months |
| **Weekly Study Hours** | 12 Hours/Week | 30 Hours/Week | 14 Hours/Week |
| **Recommended Projects** | Custom Data Structure Library, Version Controlled Syntax Sandbox | Production SDE Project #66: Android Application, Custom Data Structure Library | Custom Data Structure Library, Log Aggregation & Search Pipeline |

## 2. Jaccard Overlap Analysis

| Comparison Pair | Skill Gap Overlap % | Roadmap Overlap % | Recommendation Overlap % |
| --- | --- | --- | --- |
| **Alice vs Bob** | 82.4% | 0.0% | 61.5% |
| **Bob vs Charlie** | 15.0% | 0.0% | 17.9% |
| **Alice vs Charlie** | 20.0% | 0.0% | 20.7% |

## 3. Highlighting Identical Items

### Comparison: Alice vs Bob
- **Identical Missing Skills** (14 items):
  `System Design, Microservices, REST APIs, DBMS, Object Oriented Programming, Operating Systems, DSA (Combined), Low Level Design, Spring Boot, Redis, MySQL, Computer Networks, High Level Design, Docker`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (16 items):
  `System Design, Microservices, REST APIs, DBMS, Object Oriented Programming, Custom Data Structure Library, DSA (Combined), Operating Systems, Low Level Design, Data Structures & Algorithms Course for SDEs, Spring Boot, Redis, MySQL, High Level Design, Computer Networks, Docker`

### Comparison: Bob vs Charlie
- **Identical Missing Skills** (3 items):
  `Computer Networks, System Design, Operating Systems`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (5 items):
  `System Design, Custom Data Structure Library, Operating Systems, Data Structures & Algorithms Course for SDEs, Computer Networks`

### Comparison: Alice vs Charlie
- **Identical Missing Skills** (4 items):
  `Computer Networks, System Design, Operating Systems, Git & GitHub`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (6 items):
  `System Design, Git & GitHub, Custom Data Structure Library, Operating Systems, Data Structures & Algorithms Course for SDEs, Computer Networks`

## 4. Personalization Verification Checklist

### Pair: **Alice vs Bob**
- ✅ **[PASS] Skill gap overlap is 82.4%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ❌ **[FLAGGED] Recommendation overlap is 61.5%** (Exceeds maximum allowable limit of 50% overlap. Personalization warning!)

### Pair: **Bob vs Charlie**
- ✅ **[PASS] Skill gap overlap is 15.0%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ✅ **[PASS] Recommendation overlap is 17.9%**.

### Pair: **Alice vs Charlie**
- ✅ **[PASS] Skill gap overlap is 20.0%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ✅ **[PASS] Recommendation overlap is 20.7%**.

## 5. Summary Conclusion

> [!WARNING]
> **Status: FLAGGED for Further Tuning**
> One or more overlap metrics between the test profiles exceed the 50.0% threshold. Additional personalization weight tuning is required for project and resource matching to differentiate the candidate profiles further.
