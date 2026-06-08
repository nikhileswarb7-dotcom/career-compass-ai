# CareerCompass AI — Recommendation Differentiation Report

This report analyzes the differentiation and personalization quality of SDE recommendations, timeline roadmaps, and skill gap prioritization across three candidate profiles.

## 1. Profiles Comparison Table

| Attribute | Alice (Beginner) | Bob (Intermediate) | Charlie (Advanced) |
| --- | --- | --- | --- |
| **Career Stage** | Foundational / Early Explorer | Advanced / Pre-Placement | Transitioning Professional |
| **Overall Readiness** | 9% | 57% | 91% |
| **Company Fit Score** | 19.2% | 44.9% | 58.2% |
| **Top 10 Missing Skills** | DSA (Combined), DBMS, Operating Systems, Computer Networks, Spring Boot, System Design, SQL, Object Oriented Programming, REST APIs, MySQL | Microservices, PostgreSQL, Redis, Java, Spring Boot, REST APIs, Message Queues (Kafka), Low Level Design, Java, Spring Boot | Git & GitHub, AWS Basics, Linux Basics, Python, Operating Systems, Computer Networks, Message Queues (Kafka), Python, Operating Systems, Computer Networks |
| **Top 5 Recommendations** | Microservices, Docker, MySQL, DSA (Combined), Computer Networks | Message Queues (Kafka), Mastering Redis Hands-On Exercises, Microservices, Docker, AWS Basics | Message Queues (Kafka), Log Aggregation & Search Pipeline, Python, Computer Networks, Distributed Key-Value Store |
| **Top 3 Similar Engineers** | Myntra - Senior Software Engineer, Blinkit - SDE I, Salesforce - Senior Software Engineer | Amazon - Backend Engineer, Amazon - Backend Engineer, Amazon - Backend Engineer | Microsoft - Backend Engineer, Microsoft - Backend Engineer, Blinkit - Backend Engineer |
| **Roadmap Timeline** | 48 Months | 18 Months | 12 Months |
| **Weekly Study Hours** | 12 Hours/Week | 30 Hours/Week | 14 Hours/Week |
| **Recommended Projects** | Personal Finance Tracker Dashboard, Real-Time Leaderboard System | API Gateway with Dynamic Rate Limiting, E-Commerce Inventory Lock Manager | Distributed Key-Value Store, Log Aggregation & Search Pipeline |

## 2. Jaccard Overlap Analysis

| Comparison Pair | Skill Gap Overlap % | Roadmap Overlap % | Recommendation Overlap % |
| --- | --- | --- | --- |
| **Alice vs Bob** | 35.0% | 0.0% | 22.6% |
| **Bob vs Charlie** | 18.8% | 0.0% | 11.1% |
| **Alice vs Charlie** | 20.0% | 0.0% | 13.3% |

## 3. Highlighting Identical Items

### Comparison: Alice vs Bob
- **Identical Missing Skills** (7 items):
  `Redis, Microservices, Spring Boot, Docker, REST APIs, System Design, Low Level Design`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (7 items):
  `Redis, Microservices, Spring Boot, Docker, REST APIs, System Design, Low Level Design`

### Comparison: Bob vs Charlie
- **Identical Missing Skills** (3 items):
  `System Design, Message Queues (Kafka), AWS Basics`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (3 items):
  `System Design, Message Queues (Kafka), AWS Basics`

### Comparison: Alice vs Charlie
- **Identical Missing Skills** (4 items):
  `System Design, Computer Networks, Git & GitHub, Operating Systems`
- **Identical Roadmap Stages** (0 items):
  *None*
- **Identical Recommendations** (4 items):
  `System Design, Computer Networks, Git & GitHub, Operating Systems`

## 4. Personalization Verification Checklist

### Pair: **Alice vs Bob**
- ✅ **[PASS] Skill gap overlap is 35.0%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ✅ **[PASS] Recommendation overlap is 22.6%**.

### Pair: **Bob vs Charlie**
- ✅ **[PASS] Skill gap overlap is 18.8%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ✅ **[PASS] Recommendation overlap is 11.1%**.

### Pair: **Alice vs Charlie**
- ✅ **[PASS] Skill gap overlap is 20.0%**.
- ✅ **[PASS] Roadmap overlap is 0.0%**.
- ✅ **[PASS] Recommendation overlap is 13.3%**.

## 5. Summary Conclusion

> [!NOTE]
> **Status: PASSED**
> All comparative overlap metrics are safely below the 50.0% threshold limit. The CareerCompass AI recommendation engine successfully delivers highly differentiated, student-year and target-specific roadmaps and recommendations.
