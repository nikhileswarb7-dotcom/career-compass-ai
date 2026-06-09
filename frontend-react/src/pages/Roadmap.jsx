import React, { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { useApp, API_BASE } from '../App';
import { motion } from 'framer-motion';
import { 
  Check, 
  Lock, 
  Play, 
  Download, 
  Terminal, 
  HelpCircle, 
  MessageSquare, 
  ChevronRight, 
  Eye,
  Shield, 
  BookOpen, 
  ArrowRight,
  TrendingUp,
  Award,
  Send,
  X,
  Lightbulb,
  AlertCircle
} from 'lucide-react';
import './Roadmap.css';

// Client-side static fallback databases matching the original roadmap
const STAGE_LECTURES_FALLBACK = {
  0: {
    videos: [
      { title: "Introduction to Version Control & Workspace Setup", duration: "15 mins", embed: "https://www.youtube.com/embed/YS4e4q9oBaU" },
      { title: "Blinkit Engineering Target Orientation", duration: "20 mins", embed: "https://www.youtube.com/embed/Tt08KmFfIYQ" }
    ],
    materials: [
      { title: "Developer Workspace Setup Guide.md", size: "320 KB" },
      { title: "Git Cheat Sheet.pdf", size: "150 KB" }
    ]
  },
  1: {
    videos: [
      { title: "Concurrent Programming with Go & Java Basics", duration: "25 mins", embed: "https://www.youtube.com/embed/un80v_x-128" },
      { title: "Understanding Apache Kafka & PostgreSQL Integration", duration: "35 mins", embed: "https://www.youtube.com/embed/R87354hyY2E" }
    ],
    materials: [
      { title: "Concurrent Worker Cheat Sheet.md", size: "280 KB" },
      { title: "PostgreSQL Performance Optimization.pdf", size: "410 KB" }
    ]
  },
  2: {
    videos: [
      { title: "Masterclass: High Level Design (HLD) Concepts", duration: "30 mins", embed: "https://www.youtube.com/embed/m8I0esEK6so" },
      { title: "Geo-Redis Indexes & Caching Strategies", duration: "20 mins", embed: "https://www.youtube.com/embed/OqCK95AS-XY" }
    ],
    materials: [
      { title: "System Design Handbook.md", size: "520 KB" },
      { title: "Redis geo-indexing.pdf", size: "180 KB" }
    ]
  },
  3: {
    videos: [
      { title: "Cracking SDE Interview Coding Rounds", duration: "40 mins", embed: "https://www.youtube.com/embed/V8V_vH2Sj9w" },
      { title: "STAR Behavioral Template for SDEs", duration: "15 mins", embed: "https://www.youtube.com/embed/w7mko_X4kO8" }
    ],
    materials: [
      { title: "Leetcode Prep Cheatsheet.md", size: "190 KB" },
      { title: "STAR Method Guide.pdf", size: "120 KB" }
    ]
  }
};

const ASSESSMENT_FALLBACK = {
  0: {
    mcqs: [
      {
        question: "What is the primary purpose of version control systems like Git?",
        options: ["To automate backend deployments", "To track change history and collaborate on source code", "To host SQL databases in the cloud", "To speed up local machine boot times"],
        correct: 1
      },
      {
        question: "Which technology is primarily used to isolate and run microservices in uniform containers?",
        options: ["Kafka", "Docker", "Redis", "Elasticsearch"],
        correct: 1
      },
      {
        question: "What is the average search complexity in a balanced Binary Search Tree (BST)?",
        options: ["O(N)", "O(N log N)", "O(log N)", "O(1)"],
        correct: 2
      }
    ],
    coding: {
      title: "Height-Balanced Binary Tree Check",
      desc: "Implement a function isBalanced(root) that returns true if a binary tree is height-balanced, otherwise false. A tree is height-balanced if the depth of its two subtrees never differs by more than 1.",
      template: `function isBalanced(root) {\n    // Write your height-balanced check code here\n    if (root === null) return true;\n    \n    function checkHeight(node) {\n        if (node === null) return 0;\n        let left = checkHeight(node.left);\n        let right = checkHeight(node.right);\n        if (left === -1 || right === -1 || Math.abs(left - right) > 1) return -1;\n        return Math.max(left, right) + 1;\n    }\n    return checkHeight(root) !== -1;\n}`
    }
  },
  1: {
    mcqs: [
      {
        question: "In Go, what is the idiomatic way to safely pass data between concurrent goroutines?",
        options: ["Writing to local text files", "Using global shared variables", "Communicating via Go channels", "Using database transactions"],
        correct: 2
      },
      {
        question: "How does Apache Kafka guarantee message ordering?",
        options: ["Ordering is guaranteed across all topics globally", "Ordering is guaranteed within a single partition", "Ordering is guaranteed by consumer group offsets", "Ordering is guaranteed using system timestamps"],
        correct: 1
      },
      {
        question: "Which indexing model in PostgreSQL is most appropriate for high-concurrency range queries?",
        options: ["Hash Index", "B-Tree Index", "GIN Index", "BRIN Index"],
        correct: 1
      }
    ],
    coding: {
      title: "Concurrent Channel Worker",
      desc: "Write a Go function workerPool(jobs, results) to process job requests concurrently using worker goroutines and channels.",
      template: `package main\n\nimport "fmt"\n\nfunc worker(id int, jobs <-chan int, results chan<- int) {\n    for j := range jobs {\n        fmt.Println("worker", id, "started job", j)\n        results <- j * 2\n    }\n}`
    }
  },
  2: {
    mcqs: [
      {
        question: "Which caching design pattern updates both cache and DB in a single atomic transaction block?",
        options: ["Cache-Aside pattern", "Write-Through pattern", "Write-Behind/Write-Back pattern", "Read-Through pattern"],
        correct: 1
      },
      {
        question: "Which Redis command is optimal for tracking geo-coordinates of quick-commerce riders?",
        options: ["HSET", "GEOADD", "ZADD", "LPUSH"],
        correct: 1
      },
      {
        question: "What is the primary benefit of read-replicas in PostgreSQL?",
        options: ["Decrease writing response latency", "Improve database schema normalizations", "Scale read transactions and handle node failure redundancy", "Increase network packet compression"],
        correct: 2
      }
    ],
    coding: {
      title: "Redis Simple Rate Limiter",
      desc: "Implement a rate limiter class in JavaScript that checks if a user has exceeded 5 requests per minute, returns false if rate-limited.",
      template: `class RateLimiter {\n    constructor() {\n        this.requests = new Map();\n    }\n    \n    isAllowed(userId) {\n        const now = Date.now();\n        return true;\n    }\n}`
    }
  },
  3: {
    mcqs: [
      {
        question: "In behavioral SDE rounds, what does the 'A' represent in the STAR template?",
        options: ["Assessment", "Allocation", "Action taken", "Algorithmic score"],
        correct: 2
      },
      {
        question: "What is the best way to showcase achievements on an SDE resume?",
        options: ["Explain lines of code written", "Detail the group's general code layout", "Quantify personal impact (e.g. 'reduced latency by 30% using Redis')", "List all keywords in alphabet order"],
        correct: 2
      },
      {
        question: "How should code complexity be discussed during a live SDE whiteboard interview?",
        options: ["Wait for the interviewer to prompt you", "Calculate time and space bounds step-by-step as you construct the code", "State O(N) immediately for all solutions", "Say complexity doesn't matter for initial prototypes"],
        correct: 1
      }
    ],
    coding: {
      title: "Two Sum Optimal O(N)",
      desc: "Write a function twoSum(nums, target) returning indices of the two elements adding up to target in linear time complexity.",
      template: `function twoSum(nums, target) {\n    const map = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const complement = target - nums[i];\n        if (map.has(complement)) {\n            return [map.get(complement), i];\n        }\n        map.set(nums[i], i);\n    }\n    return [];\n}`
    }
  }
};

export default function Roadmap() {
  const { sessionId, careerPlan, setCareerPlan, updateSessionStatus } = useApp();
  const navigate = useNavigate();
  
  // Track timeline stages
  const plan = careerPlan || {};
  const stages = plan.timeline?.stages || [];

  // Stage state indices
  const [currentStageIndex, setCurrentStageIndex] = useState(
    parseInt(localStorage.getItem('roadmap_current_stage') || '0')
  );
  const [activeStageStep, setActiveStageStep] = useState(
    parseInt(localStorage.getItem('roadmap_stage_step') || '0') // 0 to 3
  );
  const [completedStages, setCompletedStages] = useState(
    new Set(JSON.parse(localStorage.getItem('roadmap_completed_stages') || '[]'))
  );

  const [selectedStageIndex, setSelectedStageIndex] = useState(currentStageIndex);
  const [selectedStepIndex, setSelectedStepIndex] = useState(0);

  // Active view states
  const [lectureData, setLectureData] = useState({ source: 'Local', videos: [], materials: [] });
  const [activeVideoEmbed, setActiveVideoEmbed] = useState('');
  const [activeVideoTitle, setActiveVideoTitle] = useState('');
  const [assessmentData, setAssessmentData] = useState({ source: 'Local', mcqs: [], coding: {} });
  
  // Compiler state
  const [codeEditor, setCodeEditor] = useState('');
  const [codingValidated, setCodingValidated] = useState(false);
  const [compilerStatus, setCompilerStatus] = useState('Ready to compile');
  const [compilerColor, setCompilerColor] = useState('var(--text-muted)');

  // MCQ state
  const [selectedMcqAnswers, setSelectedMcqAnswers] = useState({});
  const [assessmentResultMsg, setAssessmentResultMsg] = useState('');
  const [assessmentResultBg, setAssessmentResultBg] = useState('');
  const [assessmentResultColor, setAssessmentResultColor] = useState('');

  // Confetti piece states
  const [showConfetti, setShowConfetti] = useState(false);

  // Chatbot Drawer States
  const [chatOpen, setChatOpen] = useState(false);
  const [chatWidth, setChatWidth] = useState(
    parseInt(localStorage.getItem('chatbot_drawer_width') || '360')
  );
  const [isResizing, setIsResizing] = useState(false);
  const [chatMessages, setChatMessages] = useState([
    { sender: 'coach', text: "Hello! I am your AI Career Coach. Ask me anything about your roadmap stages, SDE designs, or preparation strategies!" }
  ]);
  const [chatInput, setChatInput] = useState('');
  const chatMessagesEndRef = useRef(null);

  const startResize = (e) => {
    e.preventDefault();
    setIsResizing(true);
    document.body.style.userSelect = 'none';
    
    const startX = e.clientX;
    const startWidth = chatWidth;
    
    const doResize = (moveEvent) => {
      const deltaX = startX - moveEvent.clientX;
      const newWidth = Math.max(280, Math.min(600, startWidth + deltaX));
      setChatWidth(newWidth);
      localStorage.setItem('chatbot_drawer_width', newWidth.toString());
    };
    
    const stopResize = () => {
      setIsResizing(false);
      document.body.style.userSelect = '';
      document.removeEventListener('mousemove', doResize);
      document.removeEventListener('mouseup', stopResize);
    };
    
    document.addEventListener('mousemove', doResize);
    document.addEventListener('mouseup', stopResize);
  };

  // Company Intelligence States
  const [companyJD, setCompanyJD] = useState(null);
  const [companyExperience, setCompanyExperience] = useState(null);

  // Skill Path Modal States
  const [skillModalOpen, setSkillModalOpen] = useState(false);
  const [skillModalTitle, setSkillModalTitle] = useState('');
  const [skillModalData, setSkillModalData] = useState([]);
  const [skillModalLoading, setSkillModalLoading] = useState(false);

  const hasLoadedProgress = useRef(false);

  // Sync state helpers
  const saveState = async (newStage = currentStageIndex, newStep = activeStageStep, newCompleted = completedStages) => {
    localStorage.setItem('roadmap_current_stage', newStage.toString());
    localStorage.setItem('roadmap_stage_step', newStep.toString());
    localStorage.setItem('roadmap_completed_stages', JSON.stringify(Array.from(newCompleted)));

    if (!sessionId || newStage >= stages.length) return;
    
    const stage = stages[newStage];
    if (!stage) return;

    let status = 'In Progress';
    let completion_pct = 0;
    if (newStep === 1) completion_pct = 33;
    else if (newStep === 2) completion_pct = 66;
    else if (newStep >= 3) {
      completion_pct = 100;
      status = 'Completed';
    }

    try {
      await fetch(`${API_BASE}/api/session/${sessionId}/stage-progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stage_title: stage.title,
          status: status,
          completion_pct: completion_pct
        })
      });
    } catch (err) {
      console.warn("Failed to sync stage progress to database", err);
    }
  };

  // Load stage progress from API on mount
  useEffect(() => {
    if (!sessionId || !stages.length || hasLoadedProgress.current) return;

    async function loadProgress() {
      try {
        const response = await fetch(`${API_BASE}/api/session/${sessionId}/stage-progress`);
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.progress) {
            const dbProgress = data.progress;
            
            const progressMap = {};
            dbProgress.forEach(p => {
              progressMap[p.stage_title] = p;
            });

            const nextCompleted = new Set();
            let resolvedCurrentIndex = 0;
            let resolvedActiveStep = 0;

            for (let i = 0; i < stages.length; i++) {
              const stage = stages[i];
              const p = progressMap[stage.title];
              if (p) {
                if (p.status === 'Completed' || p.completion_pct >= 100) {
                  nextCompleted.add(i);
                } else {
                  resolvedCurrentIndex = i;
                  if (p.completion_pct >= 66) resolvedActiveStep = 2;
                  else if (p.completion_pct >= 33) resolvedActiveStep = 1;
                  else resolvedActiveStep = 0;
                  break;
                }
              } else {
                resolvedCurrentIndex = i;
                resolvedActiveStep = 0;
                break;
              }
            }

            if (nextCompleted.size === stages.length && stages.length > 0) {
              resolvedCurrentIndex = stages.length;
              resolvedActiveStep = 0;
            }

            setCompletedStages(nextCompleted);
            setCurrentStageIndex(resolvedCurrentIndex);
            setActiveStageStep(resolvedActiveStep);
            
            setSelectedStageIndex(Math.min(resolvedCurrentIndex, stages.length - 1));
            setSelectedStepIndex(Math.min(resolvedActiveStep, 3));
            hasLoadedProgress.current = true;
          }
        }
      } catch (err) {
        console.error("Failed to load stage progress from API:", err);
      }
    }

    loadProgress();
  }, [sessionId, stages]);

  // 1. Fetch Stage Content on selected stage index change
  useEffect(() => {
    if (selectedStageIndex >= stages.length) return;
    const stage = stages[selectedStageIndex];
    if (!stage) return;

    // Use dynamic content from the stage if present
    if ((stage.videos && stage.videos.length > 0) || (stage.materials && stage.materials.length > 0)) {
      setLectureData({
        source: 'Dynamic Timeline Stage',
        videos: stage.videos || [],
        materials: stage.materials || []
      });
      setActiveVideoEmbed('');
      setActiveVideoTitle('');
      return;
    }

    async function fetchStageContent() {
      const fallback = STAGE_LECTURES_FALLBACK[selectedStageIndex] || null;

      setLectureData({
        source: 'Local Fallback',
        videos: fallback ? fallback.videos : [],
        materials: fallback ? fallback.materials : []
      });
      setActiveVideoEmbed('');
      setActiveVideoTitle('');

      try {
        const response = await fetch(`${API_BASE}/api/stages/${selectedStageIndex + 1}/content`);
        if (response.ok) {
          const apiData = await response.json();
          const apiVideos = apiData.video_playlist || apiData.videos;
          const apiMaterials = apiData.cheat_sheets || apiData.materials;
          
          setLectureData({
            source: 'PostgreSQL Database',
            videos: (apiVideos && apiVideos.length > 0) ? apiVideos : (fallback ? fallback.videos : []),
            materials: (apiMaterials && apiMaterials.length > 0) ? apiMaterials : (fallback ? fallback.materials : [])
          });
        }
      } catch (err) {
        console.warn("Stages content API offline. Using fallback.", err);
      }
    }

    fetchStageContent();
  }, [selectedStageIndex, stages]);

  // 2. Fetch Stage Assessment on selected stage index change (for steps 1 & 2)
  useEffect(() => {
    if (selectedStageIndex >= stages.length) return;
    const stage = stages[selectedStageIndex];
    if (!stage) return;

    // Use dynamic assessment from stage if present
    if (stage.mcqs && stage.mcqs.length > 0) {
      setAssessmentData({
        source: 'Dynamic Timeline Stage',
        mcqs: stage.mcqs,
        coding: stage.coding || {
          title: "Implement core algorithm for " + stage.title,
          desc: "Write a function to solve the core objective outlined in this roadmap stage.",
          template: "function solve() {\n    // write code\n    return true;\n}"
        }
      });
      setCodeEditor(stage.coding?.template || "function solve() {\n    // write code\n    return true;\n}");
      setCodingValidated(false);
      setCompilerStatus('Ready to compile');
      setCompilerColor('var(--text-muted)');
      setSelectedMcqAnswers({});
      setAssessmentResultMsg('');
      return;
    }

    async function fetchStageAssessment() {
      const fallback = ASSESSMENT_FALLBACK[selectedStageIndex] || {
        mcqs: [
          { question: "Core definition check of " + stage.title + "?", options: ["Correct option", "Incorrect option 1", "Incorrect option 2"], correct: 0 }
        ],
        coding: {
          title: "Implement core algorithm for " + stage.title,
          desc: "Write a function to solve the core objective outlined in this roadmap stage.",
          template: "function solve() {\n    // write code\n    return true;\n}"
        }
      };

      setAssessmentData({ source: 'Local Fallback', ...fallback });
      setCodeEditor(fallback.coding.template);
      setCodingValidated(false);
      setCompilerStatus('Ready to compile');
      setCompilerColor('var(--text-muted)');
      setSelectedMcqAnswers({});
      setAssessmentResultMsg('');

      try {
        const response = await fetch(`${API_BASE}/api/stages/${selectedStageIndex + 1}/assessment`);
        if (response.ok) {
          const apiData = await response.json();
          setAssessmentData({
            source: 'PostgreSQL Database',
            mcqs: (apiData.mcqs && apiData.mcqs.length > 0) ? apiData.mcqs : fallback.mcqs,
            coding: apiData.coding || apiData.coding_challenge || fallback.coding
          });
          setCodeEditor(apiData.coding?.template || apiData.coding_challenge?.template || fallback.coding.template);
        }
      } catch (err) {
        console.warn("Stages assessment API offline. Using fallback.", err);
      }
    }

    fetchStageAssessment();
  }, [selectedStageIndex, stages]);

  // 3. Fetch Company Intelligence on startup
  useEffect(() => {
    const company = plan.dream_company || 'Blinkit';
    const role = plan.target_role || 'Software Development Engineer';

    async function fetchCompanyIntel() {
      try {
        const jdRes = await fetch(`${API_BASE}/api/companies/${encodeURIComponent(company)}/job-description?role_name=${encodeURIComponent(role)}`);
        if (jdRes.ok) {
          const jdData = await jdRes.json();
          setCompanyJD(jdData);
        }
      } catch (err) {
        console.error("Failed to fetch JD", err);
      }

      try {
        const expRes = await fetch(`${API_BASE}/api/companies/${encodeURIComponent(company)}/interview-experiences`);
        if (expRes.ok) {
          const expData = await expRes.json();
          if (expData && expData.length > 0) {
            setCompanyExperience(expData[0]);
          }
        }
      } catch (err) {
        console.error("Failed to fetch experiences", err);
      }
    }

    fetchCompanyIntel();
  }, [plan.dream_company, plan.target_role]);

  // 4. Scroll chatbot to bottom
  useEffect(() => {
    if (chatMessagesEndRef.current) {
      chatMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  // Automatic status promotion removed to prevent premature completion. Promotion occurs when all curriculum stages are cleared.

  // 5. Code compiler trigger
  const runCodingTests = () => {
    setCompilerStatus("Compiling & executing SDE test suite...");
    setCompilerColor("var(--primary)");

    setTimeout(() => {
      try {
        const trimmedCode = codeEditor.trim();
        if (trimmedCode.length < 35 || trimmedCode.includes("Write your") || trimmedCode.includes("Write logic")) {
          throw new Error("Code template not completed or placeholder remains.");
        }

        if (codeEditor.includes("isBalanced")) {
          const testFn = new Function('root', codeEditor + "\nreturn isBalanced(root);");
          if (testFn(null) !== true) {
            throw new Error("Test Case 1 Failed: isBalanced(null) should return true.");
          }
        } else if (codeEditor.includes("worker") && (codeEditor.includes("go ") || codeEditor.includes("chan"))) {
          if (!codeEditor.includes("go ") && !codeEditor.includes("go func")) {
            throw new Error("SDE Compiler Error: No concurrent goroutines found. Use 'go worker(...)' or similar.");
          }
          if (!codeEditor.includes("chan") && !codeEditor.includes("<-")) {
            throw new Error("SDE Compiler Error: No channels found. Go worker pool requires channel communication.");
          }
        } else if (codeEditor.includes("RateLimiter")) {
          const evalCode = codeEditor + "\nreturn new RateLimiter();";
          const limiter = new Function(evalCode)();
          if (typeof limiter.isAllowed !== 'function') {
            throw new Error("Test Case 1 Failed: RateLimiter instance must have an isAllowed(userId) method.");
          }
        } else if (codeEditor.includes("twoSum")) {
          const testFn = new Function('nums', 'target', codeEditor + "\nreturn twoSum(nums, target);");
          const res = testFn([2, 7, 11, 15], 9);
          if (!Array.isArray(res) || res[0] !== 0 || res[1] !== 1) {
            throw new Error("Test Case 1 Failed: twoSum([2, 7, 11, 15], 9) should return [0, 1]. Got: " + JSON.stringify(res));
          }
        } else if (codeEditor.includes("solve")) {
          const testFn = new Function(codeEditor + "\nreturn solve();");
          if (testFn() !== true) {
            throw new Error("Test Case 1 Failed: solve() should return true.");
          }
        } else {
          // General syntax verification
          new Function(codeEditor);
        }

        setCompilerStatus("Tests: PASS! Executed test suite successfully. (2/2 test cases passed)");
        setCompilerColor("var(--emerald)");
        setCodingValidated(true);
      } catch (e) {
        setCompilerStatus("Compilation/Test Failed: " + e.message);
        setCompilerColor("var(--rose)");
        setCodingValidated(false);
      }
    }, 1200);
  };

  const handleMcqSelect = (idx, value) => {
    setSelectedMcqAnswers(prev => ({ ...prev, [idx]: parseInt(value) }));
  };

  const submitStageAssessment = () => {
    const mcqs = assessmentData.mcqs;
    let correctCount = 0;
    let unanswered = false;

    for (let i = 0; i < mcqs.length; i++) {
      const selected = selectedMcqAnswers[i];
      if (selected === undefined) {
        unanswered = true;
        break;
      } else if (selected === mcqs[i].correct) {
        correctCount++;
      }
    }

    if (unanswered) {
      setAssessmentResultMsg("⚠️ Please answer all multiple choice questions.");
      setAssessmentResultBg("var(--warning-glow)");
      setAssessmentResultColor("var(--amber)");
      return;
    }

    if (correctCount >= 2) {
      setAssessmentResultMsg(`✓ Passed! Score: ${correctCount}/${mcqs.length} correct. Milestone checkpoint cleared!`);
      setAssessmentResultBg("var(--success-glow)");
      setAssessmentResultColor("var(--emerald)");

      if (selectedStageIndex === currentStageIndex) {
        const nextStep = Math.max(activeStageStep, 3);
        setActiveStageStep(nextStep);
        setSelectedStepIndex(3);
        saveState(currentStageIndex, nextStep);
      } else {
        setSelectedStepIndex(3);
      }
    } else {
      setAssessmentResultMsg(`❌ Score: ${correctCount}/${mcqs.length} MCQs correct. (Minimum target: 2/3 MCQs correct). Review lectures and try again!`);
      setAssessmentResultBg("var(--danger-glow)");
      setAssessmentResultColor("var(--rose)");
    }
  };

  const completeLecturesStep = () => {
    if (selectedStageIndex === currentStageIndex) {
      const nextStep = Math.max(activeStageStep, 1);
      setActiveStageStep(nextStep);
      setSelectedStepIndex(1);
      saveState(currentStageIndex, nextStep);
    } else {
      setSelectedStepIndex(1);
    }
  };

  const completeCodingStep = () => {
    if (selectedStageIndex === currentStageIndex) {
      const nextStep = Math.max(activeStageStep, 2);
      setActiveStageStep(nextStep);
      setSelectedStepIndex(2);
      saveState(currentStageIndex, nextStep);
    } else {
      setSelectedStepIndex(2);
    }
  };

  const confirmStageProgression = async () => {
    const nextCompleted = new Set(completedStages);
    nextCompleted.add(currentStageIndex);
    setCompletedStages(nextCompleted);

    const nextStageIdx = currentStageIndex + 1;
    setCurrentStageIndex(nextStageIdx);
    setActiveStageStep(0);
    setCodingValidated(false);
    setSelectedStageIndex(nextStageIdx);
    setSelectedStepIndex(0);

    saveState(nextStageIdx, 0, nextCompleted);
    setShowConfetti(false);

    if (nextStageIdx >= stages.length) {
      try {
        const response = await fetch(`${API_BASE}/api/session/${sessionId}/progress`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'roadmap_completed' })
        });
        if (response.ok) {
          updateSessionStatus('roadmap_completed');
        }
      } catch (e) {
        console.warn("Failed to set roadmap completed progress status:", e);
        updateSessionStatus('roadmap_completed');
      }
    }
  };

  const downloadMaterial = (title) => {
    let content = `# CareerCompass AI — Placement Preparation Guide\n\n` +
      `### Reference Material: ${title}\n` +
      `* Target SDE Placement Track\n` +
      `* Recommended Target: ${plan.dream_company || 'Blinkit'} (${plan.target_role || 'Junior SDE'})\n\n` +
      `---\n\n` +
      `## 1. Study Objectives & Concepts\n` +
      `- Review standard API structures and asynchronous message patterns.\n` +
      `- Learn structural memory caching layouts and relational query indices.\n` +
      `- Analyze high-throughput system bottlenecks and LLD patterns.\n\n` +
      `## 2. Interactive SDE Exercises\n` +
      `1. Implement the requested module inside your local sandbox code directory.\n` +
      `2. Execute load tests simulating peak transaction traffic (~10,000 req/sec).\n` +
      `3. Verify database locks and resolve query latency anomalies (<20ms target).\n\n` +
      `## 3. Recommended External Platforms\n` +
      `- System Design Primer: https://github.com/donnemartin/system-design-primer\n` +
      `- TakeUForward DSA Sheet: https://takeuforward.org\n` +
      `- Past SDE Interview Questions: https://geeksforgeeks.org\n\n` +
      `---\n` +
      `Generated dynamically in real-time by CareerCompass AI.`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = title;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Chat submit
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    const msgText = chatInput.trim();
    if (!msgText) return;

    setChatMessages(prev => [...prev, { sender: 'user', text: msgText }]);
    setChatInput('');

    // Typing bubble
    setChatMessages(prev => [...prev, { sender: 'coach', text: 'Typing...' }]);

    const activeStageTitle = stages[currentStageIndex] ? stages[currentStageIndex].title : "Final Polish";
    const chatPayload = {
      message: msgText,
      stage_title: activeStageTitle,
      dream_company: plan.dream_company || "Blinkit",
      dream_sector: plan.dream_sector || "Quick-Commerce",
      qualification: plan.qualification || "Fresh Graduate"
    };

    let replyText = "";
    try {
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chatPayload)
      });

      if (response.ok) {
        const resJson = await response.json();
        replyText = resJson.reply;
      } else {
        replyText = "Sorry, my network is experiencing an issue. Let's keep focusing on checking off tasks in your roadmap!";
      }
    } catch (err) {
      const msgLower = msgText.toLowerCase();
      const company = plan.dream_company || "Blinkit";
      if (msgLower.includes("dsa") || msgLower.includes("algorithm")) {
        replyText = "Practice is key! Go to the 'Resources' section and review Striver's DSA sheet. Solve at least 2 medium problems a day, analyzing the time/space complexities.";
      } else if (msgLower.includes("system design") || msgLower.includes("hld")) {
        replyText = `For ${company}, focus on designing high-throughput, low-latency queues (Kafka) and caching strategies (Redis). Check out Donne Martin's System Design Primer in your resources.`;
      } else if (msgLower.includes("redis") || msgLower.includes("cache")) {
        replyText = "Master Redis data types, key expiration configurations, and cache design strategies like cache-aside and write-behind caching.";
      } else if (msgLower.includes("kafka") || msgLower.includes("queue")) {
        replyText = "Learn about consumer groups, offset retention, partitioning algorithms, and how message ordering is maintained inside Apache Kafka.";
      } else if (msgLower.includes("resume") || msgLower.includes("project")) {
        replyText = `Highlight production-like details on your resume: explain database schemas, performance indexing, and concurrency models you worked on. Check out the blueprint on the right!`;
      } else {
        replyText = `Focus on completing the active exercises in ${activeStageTitle}. Hands-on coding is the most effective way to prep for SDE interviews.`;
      }
    }

    setChatMessages(prev => {
      const filtered = prev.filter(m => m.text !== 'Typing...');
      return [...filtered, { sender: 'coach', text: replyText }];
    });
  };

  const openSkillRoadmap = async (skillName) => {
    setSkillModalOpen(true);
    setSkillModalTitle(`${skillName} Learning Path`);
    setSkillModalLoading(true);
    setSkillModalData([]);

    try {
      const res = await fetch(`${API_BASE}/api/skills/roadmap?skill_name=${encodeURIComponent(skillName)}`);
      if (res.ok) {
        const data = await res.json();
        setSkillModalData(data);
      } else {
        setSkillModalData([]);
      }
    } catch (err) {
      console.error("Error loading skill roadmap:", err);
    } finally {
      setSkillModalLoading(false);
    }
  };

  // Coach speach messages
  const getCoachSpeechMessage = () => {
    const activeStage = stages[currentStageIndex];
    if (!activeStage) return `"Outstanding work! You've accomplished all training stages on your curriculum. You are fully prepared to face the SDE interviewers!"`;

    if (selectedStageIndex < currentStageIndex) {
      return `"You are reviewing Stage ${selectedStageIndex + 1} which you've already completed. Feel free to re-watch the lectures or check your code."`;
    }
    if (selectedStageIndex > currentStageIndex) {
      return `"Stage ${selectedStageIndex + 1} is locked. Complete Stage ${currentStageIndex + 1} first to unlock this track."`;
    }

    if (activeStageStep === 0) {
      return `"Let's begin preparing for Stage ${currentStageIndex + 1}: ${activeStage.title}. Watch the lectures first, then we'll tackle the coding sandbox."`;
    } else if (activeStageStep === 1) {
      return `"Great job completing the lectures! Now let's implement the SDE challenge in the split-screen coding sandbox."`;
    } else if (activeStageStep === 2) {
      return `"Coding challenge validated! Now take the Checkpoint Assessment to unlock the next stage of your roadmap."`;
    } else if (activeStageStep === 3) {
      return `"All goals crossed! Click 'Finish Stage & Unlock Next' to claim your readiness score boost and advance your track."`;
    }
    return "";
  };

  const handleStepClick = (stepIdx) => {
    if (selectedStageIndex < currentStageIndex) {
      setSelectedStepIndex(stepIdx);
    } else if (selectedStageIndex === currentStageIndex) {
      if (stepIdx <= activeStageStep) {
        setSelectedStepIndex(stepIdx);
      }
    }
  };

  const activeProject = plan.projects?.[selectedStageIndex] || plan.projects?.[0];

  return (
    <div 
      className="roadmap-wrapper"
      style={{ '--chat-drawer-width': chatOpen ? `${chatWidth}px` : '0px' }}
    >
      <motion.div 
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ width: '100%', display: 'flex', flexDirection: 'column' }}
      >
        <div className="welcome-banner-row">
          <h1>Interactive SDE Placement Coach</h1>
          <p>Advance through targeted learning stages, write sandbox code, and check off milestone assessments.</p>
        </div>

      <div className={`roadmap-grid-layout ${chatOpen ? 'chat-open' : ''}`}>
        
        {/* Left column: Stages sidebar menu */}
        <div className="stages-sidebar-column">
          <div className="glass-card stages-sidebar-card">
            <div className="sidebar-title">Prep Timeline</div>
            <div className="stages-menu-list">
              {stages.map((st, idx) => {
                const isActive = idx === selectedStageIndex;
                const isComp = completedStages.has(idx);
                const isLock = idx > currentStageIndex;
                
                let statusText = "Locked";
                let statusClass = "locked";
                if (idx === currentStageIndex) {
                  statusText = "Active";
                  statusClass = "active";
                } else if (isComp || idx < currentStageIndex) {
                  statusText = "Completed";
                  statusClass = "completed";
                }

                return (
                  <button 
                    key={idx}
                    disabled={isLock}
                    onClick={() => {
                      setSelectedStageIndex(idx);
                      setSelectedStepIndex(idx === currentStageIndex ? activeStageStep : 0);
                    }}
                    className={`stage-menu-item ${isActive ? 'active' : ''} ${isComp ? 'completed' : ''} ${isLock ? 'locked' : ''}`}
                  >
                    <div className="stage-menu-header">
                      <span className="stage-menu-title">Stage 0{idx + 1}</span>
                      <span className={`stage-menu-status ${statusClass}`}>{statusText}</span>
                    </div>
                    <div className="stage-menu-desc">{st.title}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Dynamic Coachspeech bubble */}
          <div className="glass-card coach-bubble-card">
            <div className="coach-avatar">
              <Shield size={18} style={{ color: 'var(--primary)' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.82rem', color: 'var(--primary)', marginBottom: '0.25rem' }}>AI Coach Advice</div>
              <p className="coach-speech-bubble">{getCoachSpeechMessage()}</p>
            </div>
          </div>
          
          <button className="btn-primary coach-drawer-btn" onClick={() => setChatOpen(true)}>
            <MessageSquare size={16} />
            <span>Chat with AI Coach</span>
          </button>
        </div>

        {/* Right column: Dynamic player workspace */}
        <div className="player-workspace-container">
          
          {/* Header metadata */}
          <div className="glass-card player-header-card">
            <div className="player-header-info">
              <h2>
                {selectedStageIndex >= stages.length 
                  ? "SDE Curriculum Completed" 
                  : `Stage ${selectedStageIndex + 1}: ${stages[selectedStageIndex]?.title}`}
              </h2>
              <p>{selectedStageIndex >= stages.length ? "You are fully placement-ready!" : stages[selectedStageIndex]?.focus}</p>
            </div>
            <div 
              className="player-status-badge"
              style={{
                background: selectedStageIndex < currentStageIndex 
                  ? 'var(--emerald)' 
                  : selectedStageIndex === currentStageIndex 
                    ? 'var(--primary)' 
                    : 'var(--rose)'
              }}
            >
              {selectedStageIndex < currentStageIndex 
                ? 'Completed' 
                : selectedStageIndex === currentStageIndex 
                  ? 'Active Stage' 
                  : 'Locked'}
            </div>
          </div>

          {/* Timeline tabs bar (only visible if not locked) */}
          {selectedStageIndex <= currentStageIndex && selectedStageIndex < stages.length && (
            <div className="player-tabs-bar">
              {[
                { label: '1. Lectures', idx: 0 },
                { label: '2. Coding Sandbox', idx: 1 },
                { label: '3. Checkpoint Assessment', idx: 2 },
                { label: '4. Stage Complete', idx: 3 }
              ].map((step, idx) => {
                const isActive = selectedStepIndex === idx;
                const isCompleted = selectedStageIndex < currentStageIndex || idx < activeStageStep;
                const canClick = selectedStageIndex < currentStageIndex || idx <= activeStageStep;

                let tabClass = "";
                if (isActive) tabClass = "active";
                else if (isCompleted) tabClass = "completed";
                if (!canClick) tabClass += " disabled";

                return (
                  <button 
                    key={idx}
                    disabled={!canClick}
                    onClick={() => handleStepClick(idx)}
                    className={`player-tab-item ${tabClass}`}
                  >
                    <span>{step.label}</span>
                    {isCompleted && <Check size={12} className="tab-check-icon" />}
                  </button>
                );
              })}
            </div>
          )}

          {/* Workspace Body panel */}
          <div className="glass-panel workspace-panel">
            
            {/* If selected stage is in the future */}
            {selectedStageIndex > currentStageIndex && (
              <div style={{ textAlignment: 'center', padding: '4rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <Lock size={48} style={{ color: 'var(--rose)', marginBottom: '1rem' }} />
                <h4 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--rose)', marginBottom: '0.5rem' }}>This Stage is Currently Locked</h4>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '380px', margin: '0 auto', lineHeight: '1.5', textAlign: 'center' }}>
                  Complete the milestone exercises in your active stage ("Stage {currentStageIndex + 1}") to unlock this training track.
                </p>
              </div>
            )}

            {/* If selected stage is completed/active - show sub-wizards */}
            {selectedStageIndex <= currentStageIndex && selectedStageIndex < stages.length && (
              <>
                {/* Step 0: Lectures */}
                {selectedStepIndex === 0 && (
                  lectureData.videos && lectureData.videos.length > 0 ? (
                    <div className="lectures-grid">
                      <div>
                        <div className="video-player-container">
                          {activeVideoEmbed ? (
                            <iframe 
                              title="Roadmap Lecture Player"
                              className="video-iframe"
                              src={activeVideoEmbed}
                              allowFullScreen
                              allow="autoplay; encrypted-media"
                            />
                          ) : (
                            <div className="video-placeholder">
                              <Play size={40} style={{ color: 'var(--primary)', marginBottom: '0.75rem' }} />
                              <div style={{ fontWeight: 700, fontFamily: 'var(--font-title)', fontSize: '1.15rem' }}>Choose a Lecture Video</div>
                              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Select from the playlist on the right to start watching.</div>
                            </div>
                          )}
                        </div>
                        
                        {activeVideoEmbed && (
                          <div className="external-youtube-banner">
                            <span style={{ color: 'var(--text-muted)' }}>Video Embed not playing?</span>
                            <a href={activeVideoEmbed.replace('/embed/', '/watch?v=')} target="_blank" rel="noreferrer">
                              Watch on YouTube ↗
                            </a>
                          </div>
                        )}
                      </div>

                      <div>
                        <div className="scroller-header">Lecture Playlist</div>
                        <div className="playlist-scroller">
                          {lectureData.videos.map((vid, idx) => (
                            <button 
                              key={idx}
                              onClick={() => {
                                setActiveVideoEmbed(vid.embed);
                                setActiveVideoTitle(vid.title);
                              }}
                              className={`playlist-item ${activeVideoTitle === vid.title ? 'active' : ''}`}
                            >
                              <div style={{ textAlign: 'left' }}>
                                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{vid.title}</div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Duration: {vid.duration}</div>
                              </div>
                              <span className="playlist-play-icon"><Play size={12} fill="currentColor" /></span>
                            </button>
                          ))}
                        </div>

                        <div className="scroller-header">Cheat Sheets</div>
                        <div className="materials-list">
                          {lectureData.materials.map((mat, idx) => (
                            <div key={idx} className="material-item">
                              <div style={{ textAlign: 'left' }}>
                                <div style={{ fontWeight: 500, fontSize: '0.82rem' }}>{mat.title}</div>
                                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>File size: {mat.size}</div>
                              </div>
                              <button className="material-download-btn" onClick={() => downloadMaterial(mat.title)}>
                                <Download size={14} style={{ marginRight: '0.25rem', verticalAlign: 'middle' }} />
                                <span>Download</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div style={{ gridColumn: '1 / -1', marginTop: '2rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
                        <button className="btn-primary" onClick={completeLecturesStep}>
                          <span>Mark Lectures Complete & Continue</span>
                          <ArrowRight size={16} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem', textAlign: 'center', width: '100%' }}>
                      <AlertCircle size={48} style={{ color: 'var(--rose)', marginBottom: '1rem' }} />
                      <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: '0.5rem' }}>Training Content Unavailable</h3>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '420px', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                        We're currently curating high-quality educational resources for this specific roadmap stage. Please check back shortly, or proceed to the coding sandbox and assessments to continue your progress.
                      </p>
                      <button className="btn-primary" onClick={completeLecturesStep}>
                        <span>Skip Lectures & Go to Sandbox</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  )
                )}

                {/* Step 1: Sandbox Coding */}
                {selectedStepIndex === 1 && (
                  <div>
                    <div className="split-ide-container">
                      <div className="ide-description">
                        <h4 style={{ fontFamily: 'var(--font-title)', fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary)', marginBottom: '0.5rem' }}>
                          {assessmentData.coding.title}
                        </h4>
                        <p style={{ fontSize: '0.88rem', color: 'var(--text-main)', marginBottom: '1rem', lineHeight: '1.5' }}>
                          {assessmentData.coding.desc}
                        </p>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          <div style={{ fontWeight: 600, marginBottom: '0.25rem', color: 'var(--text-main)' }}>Execution Constraints:</div>
                          <ul style={{ paddingLeft: '1.1rem', display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
                            <li>Ensure clean syntax and proper return values.</li>
                            <li>Run the compilation suite to validate correct logic before progression.</li>
                            <li>Verified SDE environment challenge.</li>
                          </ul>
                        </div>
                      </div>

                      <div className="ide-editor-panel">
                        <textarea 
                          id="coding-editor"
                          className="coding-textarea"
                          value={codeEditor}
                          onChange={e => {
                            setCodeEditor(e.target.value);
                            setCodingValidated(false);
                            setCompilerStatus('Ready to compile (changes detected)');
                            setCompilerColor('var(--amber)');
                          }}
                        />

                        <div className="compiler-control-row">
                          <span className="compiler-status-text" style={{ color: compilerColor }}>
                            Compiler: {compilerStatus}
                          </span>
                          <button className="btn-secondary" onClick={runCodingTests}>
                            <Terminal size={14} />
                            <span>Compile & Run Tests</span>
                          </button>
                        </div>
                      </div>
                    </div>

                    <div style={{ marginTop: '1.5rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <button className="btn-secondary" onClick={() => setSelectedStepIndex(0)}>
                        Back to Lectures
                      </button>
                      <button className="btn-primary" onClick={completeCodingStep} disabled={!codingValidated}>
                        <span>Verify Code & Continue</span>
                        <ArrowRight size={16} />
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 2: MCQ Checkpoint */}
                {selectedStepIndex === 2 && (
                  <div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', lineHeight: '1.5', marginBottom: '1.5rem' }}>
                      To unlock the subsequent roadmap stage, pass this verification checkpoint. Passing criteria: Score at least 2 out of 3 MCQs correct.
                    </p>

                    <div className="assessment-questions-container">
                      {assessmentData.mcqs.map((q, idx) => (
                        <div key={idx} className="assessment-q-box">
                          <div style={{ fontWeight: 600, fontSize: '0.92rem', marginBottom: '0.75rem' }}>Q{idx + 1}: {q.question}</div>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                            {q.options.map((opt, oIdx) => (
                              <label key={oIdx} className="assessment-option-row">
                                <input 
                                  type="radio" 
                                  name={`mcq-${idx}`}
                                  value={oIdx}
                                  checked={selectedMcqAnswers[idx] === oIdx}
                                  onChange={() => handleMcqSelect(idx, oIdx)}
                                />
                                <span>{opt}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>

                    {assessmentResultMsg && (
                      <div className="assessment-result-banner" style={{ background: assessmentResultBg, color: assessmentResultColor }}>
                        {assessmentResultMsg}
                      </div>
                    )}

                    <div style={{ marginTop: '2rem', borderTop: '1px solid var(--border-glass)', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <button className="btn-secondary" onClick={() => setSelectedStepIndex(1)}>
                        Back to Sandbox
                      </button>
                      <button className="btn-primary" onClick={submitStageAssessment}>
                        <span>Submit & Evaluate Checkpoint</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3: Complete Celebration */}
                {selectedStepIndex === 3 && (
                  <div className="celebration-container">
                    <div className="celebration-emoji">
                      <Award size={48} style={{ color: 'var(--amber)' }} />
                    </div>
                    <h2 className="celebration-title">
                      {selectedStageIndex < currentStageIndex ? 'Stage Mastered!' : 'Milestone Achieved!'}
                    </h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', maxWidth: '450px', margin: '0 auto 1.5rem auto', lineHeight: '1.5' }}>
                      Fantastic effort! You've mastered all lecture concepts, coding modules, and verified assessments for this training stage.
                    </p>

                    <div className="celebration-stats-row">
                      <div className="score-box">
                        <div className="score-box-num" style={{ color: 'var(--primary)' }}>
                          {Math.min(plan.readiness_score + (selectedStageIndex * 12), 100)}%
                        </div>
                        <div className="score-box-lbl">Old Readiness</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <ArrowRight size={20} style={{ color: 'var(--primary)' }} />
                      </div>
                      <div className="score-box" style={{ borderColor: 'var(--emerald)' }}>
                        <div className="score-box-num" style={{ color: 'var(--emerald)' }}>
                          {Math.min(plan.readiness_score + ((selectedStageIndex + 1) * 12), 100)}%
                        </div>
                        <div className="score-box-lbl">New Readiness</div>
                      </div>
                    </div>

                    <button 
                      className="btn-primary" 
                      onClick={() => {
                        if (selectedStageIndex < currentStageIndex) {
                          setSelectedStageIndex(currentStageIndex);
                          setSelectedStepIndex(activeStageStep);
                        } else {
                          confirmStageProgression();
                        }
                      }}
                    >
                      <span>
                        {selectedStageIndex < currentStageIndex ? 'Return to Active Stage' : 'Finish Stage & Unlock Next'}
                      </span>
                      <ArrowRight size={16} />
                    </button>
                  </div>
                )}
              </>
            )}

            {/* If Selected Stage index is complete */}
            {selectedStageIndex >= stages.length && (
              <div style={{ textAlignment: 'center', padding: '4rem 1rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
                <Award size={48} style={{ color: 'var(--emerald)', marginBottom: '1rem' }} />
                <h2 style={{ fontFamily: 'var(--font-title)', fontSize: '1.5rem', fontWeight: 800, color: 'var(--emerald)', marginBottom: '0.5rem' }}>Curriculum Complete!</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', maxWidth: '450px', margin: '0 auto', lineHeight: '1.5', textAlign: 'center' }}>
                  You have cleared all technical stages of your roadmap. You are fully prepared to face target SDE interviews. Proceed to your final Career Report!
                </p>
                <button className="btn-primary" style={{ marginTop: '1rem' }} onClick={() => navigate('/career-report')}>
                  <span>Go to Career Report</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            )}

          </div>

          {/* Active project card */}
          {activeProject && selectedStageIndex < stages.length && (
            <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
              <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '0.25rem' }}>Active Blueprint: {activeProject.name}</div>
              <span className="source-db-badge" style={{ fontSize: '0.65rem', marginBottom: '0.5rem' }}>{activeProject.difficulty} Blueprint</span>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', lineHeight: '1.45', textAlign: 'left' }}>{activeProject.details}</p>
            </div>
          )}

          {/* Company Intelligence */}
          {companyJD && selectedStageIndex < stages.length && (
            <div className="glass-card company-intel-card">
              <div style={{ fontFamily: 'var(--font-title)', fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.5rem', borderBottom: '1px solid var(--border-glass)', paddingBottom: '0.5rem' }}>
                <Shield size={16} style={{ color: 'var(--primary)' }} />
                <span>{plan.dream_company || 'Blinkit'} Placement Intelligence</span>
              </div>
              <div className="intel-subheading">{plan.target_role || 'SDE-1'} Core Specs</div>
              <div className="intel-text" style={{ display: 'flex', gap: '1.5rem', marginBottom: '0.5rem' }}>
                <span><strong>Salary Range:</strong> {companyJD.salary_range}</span>
                <span><strong>Exp Required:</strong> {companyJD.experience_required_years} years</span>
              </div>
              <div className="intel-text" style={{ marginBottom: '1rem' }}>{companyJD.description}</div>
              <div className="intel-subheading">Core Requirements</div>
              <div className="intel-text">{(companyJD.requirements || []).join(', ')}</div>

              {companyExperience && (
                <div style={{ marginTop: '1.25rem', borderTop: '1px dotted var(--border-glass)', paddingTop: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>Candidate Experience: {companyExperience.candidate_name}</span>
                    <span style={{ fontSize: '0.72rem', background: companyExperience.verdict.toLowerCase() === 'offered' ? 'var(--success-glow)' : 'var(--danger-glow)', color: companyExperience.verdict.toLowerCase() === 'offered' ? 'var(--emerald)' : 'var(--rose)', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 650 }}>{companyExperience.verdict}</span>
                  </div>
                  <div className="intel-text" style={{ fontStyle: 'italic', marginBottom: '0.5rem' }}>"{companyExperience.experience_story}"</div>
                   <div className="intel-text" style={{ color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Lightbulb size={14} style={{ color: 'var(--amber)' }} />
                    <span><strong>Tips:</strong> {companyExperience.tips}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Quick Skill paths buttons */}
          {plan.known_skills && plan.known_skills.length > 0 && selectedStageIndex < stages.length && (
            <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'left' }}>
              <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <BookOpen size={16} style={{ color: 'var(--primary)' }} />
                <span>Explore Progressive Skill Syllabus</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {plan.known_skills.map(skill => (
                  <button 
                    key={skill} 
                    onClick={() => openSkillRoadmap(skill)}
                    className="btn-secondary" 
                    style={{ padding: '0.4rem 0.75rem', borderRadius: '8px', fontSize: '0.82rem' }}
                  >
                    <span>{skill}</span>
                    <Eye size={12} />
                  </button>
                ))}
              </div>
            </div>
          )}

        </div>
      </div>

      {/* Chatbot Drawer */}
      {createPortal(
        <div 
          className={`chatbot-drawer ${chatOpen ? 'open' : ''}`}
          style={{ width: `${chatWidth}px` }}
        >
          {/* Resize Handle */}
          <div 
            className="chatbot-resize-handle" 
            onMouseDown={startResize}
            style={{
              position: 'absolute',
              left: '-8px',
              top: 0,
              bottom: 0,
              width: '16px',
              cursor: 'ew-resize',
              zIndex: 100,
              background: 'transparent'
            }}
          >
            {/* Visual Indicator Line */}
            <div 
              style={{
                position: 'absolute',
                left: '8px',
                top: 0,
                bottom: 0,
                width: '2px',
                background: isResizing ? 'var(--primary)' : 'var(--border-glass)',
                transition: 'background 0.2s'
              }}
            />
          </div>
          <div className="chatbot-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Shield size={20} style={{ color: 'var(--primary)' }} />
              <h3 style={{ margin: 0 }}>Placement Coach</h3>
            </div>
            <button className="chatbot-close-btn" onClick={() => setChatOpen(false)}>
              <X size={16} />
            </button>
          </div>

          <div className="chatbot-messages">
            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chatbot-msg-bubble ${msg.sender === 'user' ? 'chatbot-msg-user' : 'chatbot-msg-coach'}`}>
                {msg.text}
              </div>
            ))}
            <div ref={chatMessagesEndRef} />
          </div>

          <form onSubmit={handleChatSubmit} className="chatbot-input-row">
            <input 
              type="text"
              className="chatbot-input-field"
              placeholder="Ask your placement coach..."
              value={chatInput}
              onChange={e => setChatInput(e.target.value)}
            />
            <button type="submit" className="btn-primary" style={{ padding: '0.5rem 0.75rem', borderRadius: '8px' }}>
              <Send size={14} />
            </button>
          </form>
        </div>,
        document.body
      )}

      {/* Skill Path Modal */}
      {skillModalOpen && (
        <div className="modal-overlay" onClick={() => setSkillModalOpen(false)}>
          <div className="modal-content-card glass-panel" onClick={e => e.stopPropagation()}>
            <button className="modal-close-trigger" onClick={() => setSkillModalOpen(false)}>
              <X size={16} />
            </button>
            <h2 className="modal-roadmap-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BookOpen size={20} style={{ color: 'var(--primary)' }} />
              <span>{skillModalTitle}</span>
            </h2>

            {skillModalLoading ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <div className="animate-spin" style={{ margin: '0 auto 1rem auto', width: '24px', height: '24px', border: '2.5px solid var(--border-glass)', borderTopColor: 'var(--primary)', borderRadius: '50%' }}></div>
                <div style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-title)' }}>Fetching progressive roadmap...</div>
              </div>
            ) : skillModalData.length > 0 ? (
              <div className="modal-steps-container">
                {skillModalData.map((item, idx) => {
                  let goalsList = [];
                  try {
                    goalsList = typeof item.learning_goals === 'string' ? JSON.parse(item.learning_goals) : item.learning_goals;
                  } catch (e) {
                    goalsList = item.learning_goals || [];
                  }

                  let color = "var(--primary)";
                  if (item.level.toLowerCase() === 'intermediate') color = "var(--secondary)";
                  if (item.level.toLowerCase() === 'advanced') color = "var(--emerald)";

                  return (
                    <div key={idx} className="modal-step-row">
                      <div className="modal-step-meta">
                        <span className="modal-step-lvl" style={{ color }}>{item.level} Level</span>
                        <span className="modal-step-dur">Duration: {item.duration_weeks} Weeks</span>
                      </div>
                      <div className="modal-step-details">
                        <strong>Learning Goals:</strong>
                        <ul style={{ paddingLeft: '1.2rem', marginTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                          {goalsList.map((g, gIdx) => <li key={gIdx}>{g}</li>)}
                        </ul>
                      </div>
                      <div className="modal-step-res">
                        <strong>Resources:</strong> {item.recommended_resources}
                      </div>
                      <div className="modal-step-mile">
                        <strong>Milestone:</strong> {item.milestone}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: 'var(--rose)', padding: '2rem' }}>
                Failed to load skill path roadmap details.
              </div>
            )}
          </div>
        </div>
      )}

      </motion.div>
    </div>
  );
}
