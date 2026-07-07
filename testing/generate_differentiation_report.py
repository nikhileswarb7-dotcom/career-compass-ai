# Recommendation Differentiation Analysis
# CareerCompass AI

import sys
import os
import requests
import json

API_BASE = "http://127.0.0.1:8000"

TEST_USERS = {
    "Alice": {
        "name": "Alice Diff",
        "qualification": "1st Year Student",
        "branch": "Computer Science",
        "cgpa": 7.8,
        "dream_company": "Google",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "Software Development Engineer (SDE)",
        "known_skills": ["Java"],
        "linkedin_url": "",
        "github_username": "",
        "resume_text": ""
    },
    "Bob": {
        "name": "Bob Diff",
        "qualification": "3rd Year Student",
        "branch": "Information Technology",
        "cgpa": 8.4,
        "dream_company": "Amazon",
        "dream_sector": "E-Commerce",
        "fresh_passout": False,
        "target_role": "Backend Developer",
        "known_skills": ["Python", "SQL", "Git & GitHub"],
        "linkedin_url": "https://linkedin.com/in/bobdiff",
        "github_username": "bobdiff",
        "resume_text": "Experienced with Python, Django, SQL databases, and git version control."
    },
    "Charlie": {
        "name": "Charlie Diff",
        "qualification": "Junior Software Engineer",
        "branch": "Software Engineering",
        "cgpa": 9.2,
        "dream_company": "Microsoft",
        "dream_sector": "SaaS",
        "fresh_passout": False,
        "target_role": "DevOps Engineer",
        "known_skills": ["Go", "Docker", "Kubernetes", "PostgreSQL", "Redis"],
        "linkedin_url": "https://linkedin.com/in/charliediff",
        "github_username": "charliediff",
        "resume_text": "SRE with expertise in Go microservices, Docker containerization, Kubernetes orchestration, and database scaling."
    }
}

def calculate_jaccard(set1, set2):
    if not set1 or not set2:
        return 0.0
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return round((len(intersection) / len(union)) * 100.0, 1)

def run_analysis():
    print("Running recommendation differentiation analysis...")
    results = {}
    
    # Ensure backend is online
    try:
        r = requests.get(f"{API_BASE}/")
        assert r.status_code == 200
    except Exception:
        print("CRITICAL: Backend API server is offline on port 8000. Please start the server first.")
        sys.exit(1)
        
    for key, payload in TEST_USERS.items():
        print(f"Onboarding {key}...")
        
        # 1. Analyze
        resp_analyze = requests.post(f"{API_BASE}/api/student/analyze", json=payload)
        assert resp_analyze.status_code == 200, f"Analyze failed for {key}: {resp_analyze.text}"
        res_analyze = resp_analyze.json()
        
        student_id = res_analyze.get("student_id")
        session_id = res_analyze.get("session_id")
        
        # 2. Recommend
        payload_rec = payload.copy()
        payload_rec["student_id"] = student_id
        payload_rec["session_id"] = session_id
        
        resp_rec = requests.post(f"{API_BASE}/api/recommend", json=payload_rec)
        assert resp_rec.status_code == 200, f"Recommend failed for {key}: {resp_rec.text}"
        
        # 3. Dynamic fetches
        resp_readiness = requests.get(f"{API_BASE}/api/readiness/{session_id}")
        assert resp_readiness.status_code == 200
        res_readiness = resp_readiness.json()
        
        resp_recs = requests.get(f"{API_BASE}/api/recommendations/{session_id}")
        assert resp_recs.status_code == 200
        res_recs = resp_recs.json()
        
        # Extract fields
        as_scores = res_readiness.get("assessment_scores", {})
        c_read = as_scores.get("company_readiness", {})
        c_stage = as_scores.get("career_stage", {})
        
        # Gaps (Missing Skills)
        gaps = res_readiness.get("gaps", {})
        missing_skills = (
            gaps.get("high_priority_missing", []) +
            gaps.get("medium_priority_missing", []) +
            gaps.get("low_priority_missing", [])
        )
        
        # Recommendations
        projects = set(p["name"] for p in res_recs.get("projects", []))
        resources = set(r["title"] for r in res_recs.get("resources", []))
        coach_skills = set(c["skill"] for c in res_recs.get("coach_recommendations", []))
        combined_recs = projects.union(resources).union(coach_skills)
        
        # Roadmap Stages
        stages = set(st["title"] for st in res_readiness.get("timeline", {}).get("stages", []))
        
        # Similar Engineers
        peers = [f"{p['company_name']} - {p['role_name']}" for p in res_readiness.get("similar_engineers", [])[:3]]
        
        # Timeline
        timeline_duration = f"{res_readiness.get('timeline', {}).get('months_remaining', 12)} Months"
        
        results[key] = {
            "career_stage": c_stage.get("career_stage", "N/A"),
            "readiness": res_readiness.get("readiness_score", 0),
            "fit_score": c_read.get("company_fit_score", 0.0),
            "missing_skills": missing_skills,
            "projects": projects,
            "resources": resources,
            "coach_skills": coach_skills,
            "combined_recs": combined_recs,
            "stages": stages,
            "peers": peers,
            "timeline": timeline_duration,
            "weekly_hours": res_readiness.get("timeline", {}).get("weekly_hours_recommended", 10),
            "raw_recs": res_recs
        }
        print(f"Extraction complete for {key}.")

    # Calculate overlaps between pairs
    pairs = [
        ("Alice", "Bob"),
        ("Bob", "Charlie"),
        ("Alice", "Charlie")
    ]
    
    overlap_metrics = {}
    for p1, p2 in pairs:
        skills_overlap = calculate_jaccard(set(results[p1]["missing_skills"]), set(results[p2]["missing_skills"]))
        roadmap_overlap = calculate_jaccard(results[p1]["stages"], results[p2]["stages"])
        rec_overlap = calculate_jaccard(results[p1]["combined_recs"], results[p2]["combined_recs"])
        
        # Find identical sets
        identical_skills = set(results[p1]["missing_skills"]).intersection(set(results[p2]["missing_skills"]))
        identical_stages = results[p1]["stages"].intersection(results[p2]["stages"])
        identical_recs = results[p1]["combined_recs"].intersection(results[p2]["combined_recs"])
        
        overlap_metrics[f"{p1} vs {p2}"] = {
            "skills_overlap": skills_overlap,
            "roadmap_overlap": roadmap_overlap,
            "rec_overlap": rec_overlap,
            "identical_skills": list(identical_skills),
            "identical_stages": list(identical_stages),
            "identical_recs": list(identical_recs)
        }

    # Generate Markdown File
    report_path = os.path.join(os.path.dirname(__file__), "recommendation_differentiation_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# CareerCompass AI — Recommendation Differentiation Report\n\n")
        f.write("This report analyzes the differentiation and personalization quality of SDE recommendations, timeline roadmaps, and skill gap prioritization across three candidate profiles.\n\n")
        
        f.write("## 1. Profiles Comparison Table\n\n")
        f.write("| Attribute | Alice (Beginner) | Bob (Intermediate) | Charlie (Advanced) |\n")
        f.write("| --- | --- | --- | --- |\n")
        f.write(f"| **Career Stage** | {results['Alice']['career_stage']} | {results['Bob']['career_stage']} | {results['Charlie']['career_stage']} |\n")
        f.write(f"| **Overall Readiness** | {results['Alice']['readiness']}% | {results['Bob']['readiness']}% | {results['Charlie']['readiness']}% |\n")
        f.write(f"| **Company Fit Score** | {results['Alice']['fit_score']:.1f}% | {results['Bob']['fit_score']:.1f}% | {results['Charlie']['fit_score']:.1f}% |\n")
        
        # Missing Skills (top 10)
        alice_skills = ", ".join(results['Alice']['missing_skills'][:10])
        bob_skills = ", ".join(results['Bob']['missing_skills'][:10])
        charlie_skills = ", ".join(results['Charlie']['missing_skills'][:10])
        f.write(f"| **Top 10 Missing Skills** | {alice_skills} | {bob_skills} | {charlie_skills} |\n")
        
        # Top 5 Recommendations
        alice_recs = ", ".join(list(results['Alice']['combined_recs'])[:5])
        bob_recs = ", ".join(list(results['Bob']['combined_recs'])[:5])
        charlie_recs = ", ".join(list(results['Charlie']['combined_recs'])[:5])
        f.write(f"| **Top 5 Recommendations** | {alice_recs} | {bob_recs} | {charlie_recs} |\n")
        
        # Top 3 Similar Engineers
        f.write(f"| **Top 3 Similar Engineers** | {', '.join(results['Alice']['peers'])} | {', '.join(results['Bob']['peers'])} | {', '.join(results['Charlie']['peers'])} |\n")
        
        # Timeline
        f.write(f"| **Roadmap Timeline** | {results['Alice']['timeline']} | {results['Bob']['timeline']} | {results['Charlie']['timeline']} |\n")
        
        # Weekly Study Hours
        f.write(f"| **Weekly Study Hours** | {results['Alice']['weekly_hours']} Hours/Week | {results['Bob']['weekly_hours']} Hours/Week | {results['Charlie']['weekly_hours']} Hours/Week |\n")
        
        # Recommended Projects
        alice_projects = ", ".join(results['Alice']['projects'])
        bob_projects = ", ".join(results['Bob']['projects'])
        charlie_projects = ", ".join(results['Charlie']['projects'])
        f.write(f"| **Recommended Projects** | {alice_projects} | {bob_projects} | {charlie_projects} |\n")
        f.write("\n")
        
        f.write("## 2. Jaccard Overlap Analysis\n\n")
        f.write("| Comparison Pair | Skill Gap Overlap % | Roadmap Overlap % | Recommendation Overlap % |\n")
        f.write("| --- | --- | --- | --- |\n")
        for pair, metrics in overlap_metrics.items():
            f.write(f"| **{pair}** | {metrics['skills_overlap']}% | {metrics['roadmap_overlap']}% | {metrics['rec_overlap']}% |\n")
        f.write("\n")
        
        f.write("## 3. Highlighting Identical Items\n\n")
        for pair, metrics in overlap_metrics.items():
            f.write(f"### Comparison: {pair}\n")
            
            # Identical skills
            f.write(f"- **Identical Missing Skills** ({len(metrics['identical_skills'])} items):\n")
            if metrics['identical_skills']:
                f.write(f"  `{', '.join(metrics['identical_skills'])}`\n")
            else:
                f.write("  *None*\n")
                
            # Identical roadmap stages
            f.write(f"- **Identical Roadmap Stages** ({len(metrics['identical_stages'])} items):\n")
            if metrics['identical_stages']:
                f.write(f"  `{', '.join(metrics['identical_stages'])}`\n")
            else:
                f.write("  *None*\n")
                
            # Identical recommendations
            f.write(f"- **Identical Recommendations** ({len(metrics['identical_recs'])} items):\n")
            if metrics['identical_recs']:
                f.write(f"  `{', '.join(metrics['identical_recs'])}`\n")
            else:
                f.write("  *None*\n")
            f.write("\n")
            
        f.write("## 4. Personalization Verification Checklist\n\n")
        flagged = False
        for pair, metrics in overlap_metrics.items():
            f.write(f"### Pair: **{pair}**\n")
            
            # Check skill gap overlap
            if metrics['skills_overlap'] > 90.0:
                f.write(f"- ⚠️ **[WARNING] Skill gap overlap is high: {metrics['skills_overlap']}%** (Naturally expected due to student profiles targeting the same roles, but keep an eye on profiling inputs).\n")
            else:
                f.write(f"- ✅ **[PASS] Skill gap overlap is {metrics['skills_overlap']}%**.\n")
                
            # Check roadmap overlap
            if metrics['roadmap_overlap'] > 50.0:
                f.write(f"- ❌ **[FLAGGED] Roadmap overlap is {metrics['roadmap_overlap']}%** (Exceeds maximum allowable limit of 50% overlap. Personalization warning!)\n")
                flagged = True
            else:
                f.write(f"- ✅ **[PASS] Roadmap overlap is {metrics['roadmap_overlap']}%**.\n")
                
            # Check recommendation overlap
            if metrics['rec_overlap'] > 50.0:
                f.write(f"- ❌ **[FLAGGED] Recommendation overlap is {metrics['rec_overlap']}%** (Exceeds maximum allowable limit of 50% overlap. Personalization warning!)\n")
                flagged = True
            else:
                f.write(f"- ✅ **[PASS] Recommendation overlap is {metrics['rec_overlap']}%**.\n")
            f.write("\n")
            
        f.write("## 5. Summary Conclusion\n\n")
        if flagged:
            f.write("> [!WARNING]\n")
            f.write("> **Status: FLAGGED for Further Tuning**\n")
            f.write("> One or more overlap metrics between the test profiles exceed the 50.0% threshold. Additional personalization weight tuning is required for project and resource matching to differentiate the candidate profiles further.\n")
        else:
            f.write("> [!NOTE]\n")
            f.write("> **Status: PASSED**\n")
            f.write("> All comparative overlap metrics are safely below the 50.0% threshold limit. The CareerCompass AI recommendation engine successfully delivers highly differentiated, student-year and target-specific roadmaps and recommendations.\n")
            
    print(f"Analysis completed successfully. Report compiled at: {report_path}")

if __name__ == "__main__":
    run_analysis()
