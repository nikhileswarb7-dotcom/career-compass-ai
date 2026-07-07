import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { Upload, FileText, Check, AlertCircle, ArrowRight } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './StudentForm.css';

const SKILLS_LIST = [
  "Java", "Go", "Python", "Kafka", "Redis", "PostgreSQL", "Docker", "Kubernetes",
  "gRPC", "Microservices", "Spring Boot", "NodeJS", "AWS", "GCP", "DynamoDB",
  "MySQL", "ElasticSearch", "Django", "React", "TypeScript", "NextJS", "Kotlin",
  "Android", "SRE", "System Design", "Distributed Systems"
];

const COMPANIES = ["Blinkit", "Zomato", "Swiggy", "Paytm", "PhonePe", "Flipkart", "Amazon", "Google", "Microsoft", "Meta", "TCS", "Infosys"];

const ROLES = [
  "Software Development Engineer (SDE)",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Software Engineer",
  "Mobile App Developer (Android)",
  "Mobile App Developer (iOS)",
  "Flutter Developer",
  "React Native Developer",
  "DevOps Engineer",
  "Cloud Engineer",
  "Site Reliability Engineer (SRE)",
  "Data Analyst",
  "Data Engineer",
  "Data Scientist",
  "AI Engineer",
  "Machine Learning Engineer",
  "Deep Learning Engineer",
  "NLP Engineer",
  "Computer Vision Engineer",
  "MLOps Engineer",
  "Cyber Security Engineer",
  "Security Analyst",
  "QA Automation Engineer",
  "Product Manager",
  "Associate Product Manager (APM)",
  "Business Analyst",
  "UI/UX Designer",
  "Embedded Software Engineer"
];

const SECTORS = ["Quick-Commerce", "FoodTech", "Fintech", "E-Commerce", "SaaS", "Service-Based", "SocialMedia"];

const QUALIFICATIONS = [
  "1st Year Student",
  "2nd Year Student",
  "3rd Year Student",
  "4th Year Student",
  "Fresh Graduate",
  "Trainee Engineer",
  "Junior Software Engineer"
];

export default function StudentForm() {
  const { sessionId, updateSession } = useApp();
  const navigate = useNavigate();

  // Form states
  const [name, setName] = useState('');
  const [qualification, setQualification] = useState('3rd Year Student');
  const [targetRole, setTargetRole] = useState('Software Development Engineer (SDE)');
  const [dreamCompany, setDreamCompany] = useState('Blinkit');
  const [dreamSector, setDreamSector] = useState('Quick-Commerce');
  const [freshPassout, setFreshPassout] = useState(false);
  const [branch, setBranch] = useState('');
  const [cgpa, setCgpa] = useState('');
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [githubUsername, setGithubUsername] = useState('');
  const [resumeText, setResumeText] = useState('');
  const [selectedSkills, setSelectedSkills] = useState(new Set());

  // PDF upload states
  const [pdfFile, setPdfFile] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ type: '', message: '' });

  // Handle skill toggle
  const handleToggleSkill = (skill) => {
    const updated = new Set(selectedSkills);
    if (updated.has(skill)) {
      updated.delete(skill);
    } else {
      updated.add(skill);
    }
    setSelectedSkills(updated);
  };

  // PDF File Drop & Select
  const handleFileChange = async (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf' && !file.name.endsWith('.pdf')) {
      setUploadStatus({ type: 'error', message: 'Only PDF resume files are supported for auto-parsing.' });
      return;
    }

    setPdfFile(file);
    setParsing(true);
    setUploadStatus({ type: 'info', message: 'Uploading and parsing PDF resume using pypdf...' });

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE}/api/student/parse-resume`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Failed to parse PDF on the backend.');
      }

      const data = await response.json();
      
      // Auto-populate parsed values
      if (data.name && data.name !== "SDE Candidate") setName(data.name);
      if (data.branch) setBranch(data.branch);
      if (data.cgpa) setCgpa(data.cgpa);
      
      // Populate text transcripts
      const fullText = `Parsed Resume Text:\n\nEducation:\n${data.education || ''}\n\nSkills Found:\n${(data.skills_raw || []).join(', ')}`;
      setResumeText(fullText);

      // Pre-select extracted skills
      const parsedSkills = new Set(selectedSkills);
      if (data.skills_raw) {
        data.skills_raw.forEach(s => {
          const matched = SKILLS_LIST.find(k => k.toLowerCase() === s.toLowerCase());
          if (matched) parsedSkills.add(matched);
        });
      }
      setSelectedSkills(parsedSkills);

      setUploadStatus({ type: 'success', message: '✓ Resume parsed! Review pre-filled details below.' });
    } catch (err) {
      console.error(err);
      setUploadStatus({ type: 'error', message: 'Failed to extract text. You can still paste text or fill manually.' });
    } finally {
      setParsing(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Reset current active session to initiate fresh analysis sequence
    localStorage.removeItem('session_id');
    localStorage.removeItem('student_id');
    localStorage.removeItem('career_plan');
    localStorage.removeItem('session_status');

    const onboardingData = {
      name,
      qualification,
      known_skills: Array.from(selectedSkills),
      branch,
      cgpa: parseFloat(cgpa) || 8.0,
      dream_company: dreamCompany,
      dream_sector: dreamSector,
      fresh_passout: freshPassout,
      target_role: targetRole,
      linkedin_url: linkedinUrl,
      github_username: githubUsername,
      resume_text: resumeText
    };

    localStorage.setItem('pending_onboarding', JSON.stringify(onboardingData));
    navigate('/profile-analysis');
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.15 }}
      className="form-card-container"
    >
      <div className="form-title-section">
        <h1>Career Goal Configuration</h1>
        <p className="subtitle">Initiate onboarding parameters to formulate your customized career roadmap path.</p>
      </div>

      <form onSubmit={handleSubmit} className="student-intake-form glass-panel">
        
        {/* Row 1: Personal Details */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="name">Full Name</label>
            <input 
              type="text" 
              id="name" 
              required 
              placeholder="e.g. Rahul Sharma" 
              className="form-input"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>
          
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="qualification">Current Qualification</label>
            <select 
              id="qualification" 
              className="form-input" 
              value={qualification}
              onChange={e => setQualification(e.target.value)}
            >
              {QUALIFICATIONS.map(q => <option key={q} value={q}>{q}</option>)}
            </select>
          </div>
        </div>

        {/* Row 2: Target Targets */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="target_role">Target Role</label>
            <select 
              id="target_role" 
              className="form-input" 
              value={targetRole}
              onChange={e => setTargetRole(e.target.value)}
            >
              {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>

          <div className="form-group flex-1">
            <label className="form-label" htmlFor="dream_company">Target Company</label>
            <select 
              id="dream_company" 
              className="form-input" 
              value={dreamCompany}
              onChange={e => setDreamCompany(e.target.value)}
            >
              {COMPANIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="dream_sector">Target Sector</label>
            <select 
              id="dream_sector" 
              className="form-input" 
              value={dreamSector}
              onChange={e => setDreamSector(e.target.value)}
            >
              {SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        {/* Checkbox Fast Track */}
        <div className="form-checkbox-group">
          <input 
            type="checkbox" 
            id="fresh_passout" 
            checked={freshPassout}
            onChange={e => setFreshPassout(e.target.checked)}
            className="custom-checkbox"
          />
          <label htmlFor="fresh_passout" className="checkbox-label">
            I am a Fresh Passout looking for immediate jobs (Fast-Track Prep Mode)
          </label>
        </div>

        {/* Row 3: Branch & CGPA */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="branch">Degree Field / Branch</label>
            <input 
              type="text" 
              id="branch" 
              required 
              placeholder="e.g. Computer Science" 
              className="form-input"
              value={branch}
              onChange={e => setBranch(e.target.value)}
            />
          </div>

          <div className="form-group flex-1">
            <label className="form-label" htmlFor="cgpa">Current CGPA</label>
            <input 
              type="number" 
              id="cgpa" 
              step="0.01" 
              min="0" 
              max="10" 
              required 
              placeholder="e.g. 8.50" 
              className="form-input"
              value={cgpa}
              onChange={e => setCgpa(e.target.value)}
            />
          </div>
        </div>

        {/* Drag and Drop Resume PDF zone */}
        <div className="form-group">
          <label className="form-label">Resume PDF Upload (Auto-fill profile)</label>
          <div 
            className={`file-drop-zone ${dragOver ? 'dragover' : ''} ${pdfFile ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {parsing ? (
              <div className="drop-zone-loader">
                <div className="loader-circle animate-spin"></div>
                <span>Analyzing and extracting resume skills...</span>
              </div>
            ) : pdfFile ? (
              <div className="drop-zone-success">
                <FileText className="file-icon success" />
                <span className="file-name">{pdfFile.name}</span>
                <span className="file-size">({(pdfFile.size / 1024).toFixed(1)} KB)</span>
                <button type="button" className="remove-file-btn" onClick={() => { setPdfFile(null); setUploadStatus({type:'', message:''}); }}>Remove</button>
              </div>
            ) : (
              <label htmlFor="pdf-upload" className="drop-zone-label-trigger">
                <Upload className="upload-icon" />
                <span>Drag & drop your Resume PDF here or <strong className="trigger-text">browse files</strong></span>
                <span className="drop-zone-hint">Supports standard PDFs up to 5MB</span>
                <input 
                  type="file" 
                  id="pdf-upload" 
                  accept=".pdf" 
                  onChange={e => handleFileChange(e.target.files[0])}
                  style={{ display: 'none' }}
                />
              </label>
            )}
          </div>

          {uploadStatus.message && (
            <div className={`upload-status-alert status-${uploadStatus.type}`}>
              {uploadStatus.type === 'error' ? <AlertCircle size={14} /> : <Check size={14} />}
              <span>{uploadStatus.message}</span>
            </div>
          )}
        </div>

        {/* Optional Social URLs */}
        <div className="form-row">
          <div className="form-group flex-1">
            <label className="form-label" htmlFor="linkedin_url">LinkedIn Profile URL (Optional)</label>
            <input 
              type="text" 
              id="linkedin_url" 
              placeholder="e.g. https://linkedin.com/in/username" 
              className="form-input"
              value={linkedinUrl}
              onChange={e => setLinkedinUrl(e.target.value)}
            />
          </div>

          <div className="form-group flex-1">
            <label className="form-label" htmlFor="github_username">GitHub Username (Optional)</label>
            <input 
              type="text" 
              id="github_username" 
              placeholder="e.g. username" 
              className="form-input"
              value={githubUsername}
              onChange={e => setGithubUsername(e.target.value)}
            />
          </div>
        </div>

        {/* Resume Text transcript content (for analysis overrides) */}
        <div className="form-group">
          <label className="form-label" htmlFor="resume_text">Extracted Resume Transcript Content (Optional)</label>
          <textarea 
            id="resume_text" 
            className="form-input custom-textarea" 
            placeholder="Paste your resume transcript content details here to align vector mappings manually..."
            value={resumeText}
            onChange={e => setResumeText(e.target.value)}
          />
        </div>

        {/* Skills Taxonomy Mapping */}
        <div className="form-group">
          <label className="form-label">SDE Skill Taxonomy Tags</label>
          <div className="skills-tags-selector">
            {SKILLS_LIST.map(skill => {
              const isSelected = selectedSkills.has(skill);
              return (
                <button 
                  type="button" 
                  key={skill} 
                  onClick={() => handleToggleSkill(skill)}
                  className={`skill-tag-badge ${isSelected ? 'selected' : ''}`}
                >
                  {skill}
                </button>
              );
            })}
          </div>
        </div>

        <button type="submit" className="btn-primary form-submit-btn">
          <span>Assemble Career Roadmap</span>
          <ArrowRight size={18} />
        </button>

      </form>
    </motion.div>
  );
}
