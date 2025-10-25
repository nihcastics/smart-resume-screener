import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, Target, LogOut, Sparkles, TrendingUp, Award, CheckCircle, XCircle, AlertCircle, Clock, History, User, Zap, Brain, Code, BarChart3, TrendingDown, Plus, Minus } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { analysisAPI } from '../services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [file, setFile] = useState(null);
  const [resumeText, setResumeText] = useState(''); // NEW: Direct text input
  const [inputMode, setInputMode] = useState('pdf'); // 'pdf' or 'text'
  const [jdText, setJdText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState('analyze'); // 'analyze' or 'recent'
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loadingRecent, setLoadingRecent] = useState(false);

  // Load recent analyses when tab changes
  useEffect(() => {
    if (activeTab === 'recent') {
      loadRecentAnalyses();
    }
  }, [activeTab]);

  const loadRecentAnalyses = async () => {
    setLoadingRecent(true);
    try {
      const response = await analysisAPI.getAnalyses();
      console.log('Recent analyses response:', response.data);
      setRecentAnalyses(response.data.analyses || []);
    } catch (error) {
      console.error('Failed to load recent analyses:', error);
      alert('Failed to load recent analyses. Please try again.');
    } finally {
      setLoadingRecent(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    // Validate inputs based on mode
    if (inputMode === 'pdf' && !file) {
      alert('Please upload a resume PDF');
      return;
    }
    if (inputMode === 'text' && !resumeText.trim()) {
      alert('Please enter resume text');
      return;
    }
    if (!jdText.trim()) {
      alert('Please enter job description');
      return;
    }

    setAnalyzing(true);
    setResults(null);

    try {
      const formData = new FormData();
      
      // Add resume based on input mode
      if (inputMode === 'pdf') {
        formData.append('file', file);
      } else {
        formData.append('resume_text', resumeText);
      }
      
      formData.append('jd_text', jdText);

      const response = await analysisAPI.analyze(formData);
      setResults(response.data.results);
      
      // Refresh recent analyses after successful analysis
      if (activeTab === 'recent') {
        loadRecentAnalyses();
      }
    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setResults(null);
    setFile(null);
    setResumeText('');
    setJdText('');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'from-emerald-500 to-green-500';
    if (score >= 60) return 'from-blue-500 to-cyan-500';
    if (score >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  };

  const getScoreBadge = (score) => {
    if (score >= 80) return { text: 'Excellent Match', icon: Award, color: 'emerald' };
    if (score >= 60) return { text: 'Good Match', icon: TrendingUp, color: 'blue' };
    if (score >= 40) return { text: 'Fair Match', icon: AlertCircle, color: 'yellow' };
    return { text: 'Poor Match', icon: XCircle, color: 'red' };
  };

  const scoreBreakdown = results?.score_breakdown || {};
  const scoreTier = scoreBreakdown.tier || results?.score_tier || '';
  const scorePercent = typeof scoreBreakdown.final_score_percent === 'number'
    ? scoreBreakdown.final_score_percent
    : (typeof results?.final_score === 'number' ? results.final_score * 10 : 0);
  const scoreOutOfTen = typeof scoreBreakdown.final_score_out_of_10 === 'number'
    ? scoreBreakdown.final_score_out_of_10
    : (typeof results?.final_score === 'number' ? results.final_score : scorePercent / 10);
  const semanticPercent = typeof scoreBreakdown.semantic_match_percent === 'number'
    ? scoreBreakdown.semantic_match_percent
    : Math.round((results?.global_score || 0) * 100);
  const coveragePercent = typeof scoreBreakdown.requirement_coverage_percent === 'number'
    ? scoreBreakdown.requirement_coverage_percent
    : Math.round((results?.coverage_score || 0) * 100);
  const mustCoveragePercent = typeof scoreBreakdown.must_have_coverage_percent === 'number'
    ? scoreBreakdown.must_have_coverage_percent
    : (typeof results?.must_have_coverage === 'number' ? results.must_have_coverage : coveragePercent);
  const niceCoveragePercent = typeof scoreBreakdown.nice_to_have_coverage_percent === 'number'
    ? scoreBreakdown.nice_to_have_coverage_percent
    : (typeof results?.nice_to_have_coverage === 'number' ? results.nice_to_have_coverage : 0);
  const missingRequirements = Array.isArray(results?.missing_requirements) ? results.missing_requirements : [];
  
  // New data
  const semanticDetails = results?.semantic_details || {};
  const skillsAnalysis = results?.skills_analysis || {};

  return (
    <div className="min-h-screen">
      <motion.nav initial={{ y: -100 }} animate={{ y: 0 }} className="backdrop-blur-xl bg-white/5 border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center"><Target className="w-6 h-6 text-white" /></div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Resume Screener</h1>
            </motion.div>
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-4">
              <div className="text-right"><p className="text-sm text-slate-400">Welcome back,</p><p className="font-medium text-slate-200">{user?.email}</p></div>
              <button onClick={logout} className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all flex items-center gap-2"><LogOut className="w-4 h-4" />Logout</button>
            </motion.div>
          </div>
          
          {/* Tab Navigation */}
          <div className="flex items-center gap-2 border-b border-white/10">
            <button
              onClick={() => { setActiveTab('analyze'); setResults(null); }}
              className={`px-6 py-3 font-medium transition-all flex items-center gap-2 relative ${
                activeTab === 'analyze'
                  ? 'text-purple-400'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              <span>New Analysis</span>
              {activeTab === 'analyze' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500"
                />
              )}
            </button>
            <button
              onClick={() => setActiveTab('recent')}
              className={`px-6 py-3 font-medium transition-all flex items-center gap-2 relative ${
                activeTab === 'recent'
                  ? 'text-purple-400'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Recent Analyses</span>
              {recentAnalyses.length > 0 && (
                <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-300">
                  {recentAnalyses.length}
                </span>
              )}
              {activeTab === 'recent' && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500"
                />
              )}
            </button>
          </div>
        </div>
      </motion.nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {activeTab === 'analyze' ? (
          !results ? (
          <>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-16">
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: "spring" }} className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30 mb-6">
                <Sparkles className="w-4 h-4 text-purple-400" /><span className="text-sm text-purple-300 font-medium">AI-Powered Analysis</span>
              </motion.div>
              <h2 className="text-6xl font-black mb-4 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">Smart Resume Screening</h2>
              <p className="text-xl text-slate-400 max-w-2xl mx-auto">Upload a resume and job description for instant AI-powered compatibility analysis</p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-8 mb-12">
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="glass-card hover:shadow-purple-500/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center"><FileText className="w-5 h-5 text-white" /></div>
                  <h3 className="text-xl font-bold text-slate-200">Job Description</h3>
                </div>
                <textarea value={jdText} onChange={(e) => setJdText(e.target.value)} className="input-glass h-96 resize-none font-mono text-sm" placeholder="Paste the job description here..." />
              </motion.div>

              <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="glass-card hover:shadow-pink-500/20">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center"><Upload className="w-5 h-5 text-white" /></div>
                  <h3 className="text-xl font-bold text-slate-200">Resume Input</h3>
                </div>
                
                {/* Input Mode Toggle */}
                <div className="flex items-center gap-2 mb-4 p-1 bg-white/5 rounded-lg">
                  <button
                    onClick={() => setInputMode('pdf')}
                    className={`flex-1 px-4 py-2 rounded-md font-medium transition-all ${
                      inputMode === 'pdf'
                        ? 'bg-purple-500 text-white'
                        : 'text-slate-400 hover:text-slate-300'
                    }`}
                  >
                    <Upload className="w-4 h-4 inline mr-2" />
                    Upload PDF
                  </button>
                  <button
                    onClick={() => setInputMode('text')}
                    className={`flex-1 px-4 py-2 rounded-md font-medium transition-all ${
                      inputMode === 'text'
                        ? 'bg-purple-500 text-white'
                        : 'text-slate-400 hover:text-slate-300'
                    }`}
                  >
                    <FileText className="w-4 h-4 inline mr-2" />
                    Paste Text
                  </button>
                </div>

                {inputMode === 'pdf' ? (
                  <div onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all ${dragActive ? 'border-purple-500 bg-purple-500/10' : 'border-white/20 hover:border-purple-500/50 hover:bg-white/5'}`}>
                    <input type="file" onChange={handleFileChange} accept=".pdf,.txt,.doc,.docx" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                    {!file ? (
                      <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }} className="space-y-4">
                        <motion.div animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                          <Upload className="w-10 h-10 text-purple-400" />
                        </motion.div>
                        <div><p className="text-lg font-semibold text-slate-200 mb-2">Drop your resume here</p><p className="text-sm text-slate-400">or click to browse</p><p className="text-xs text-slate-500 mt-2">PDF, TXT, DOC, DOCX • Max 10MB</p></div>
                      </motion.div>
                    ) : (
                      <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="space-y-4">
                        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-emerald-500/20 to-green-500/20 border border-emerald-500/30"><CheckCircle className="w-10 h-10 text-emerald-400" /></div>
                        <div><p className="text-lg font-semibold text-emerald-300 mb-1">{file.name}</p><p className="text-sm text-slate-400">{(file.size / 1024).toFixed(1)} KB</p></div>
                        <button onClick={(e) => { e.stopPropagation(); setFile(null); }} className="text-sm text-red-400 hover:text-red-300 transition-colors">Remove file</button>
                      </motion.div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-3">
                    <textarea 
                      value={resumeText} 
                      onChange={(e) => setResumeText(e.target.value)} 
                      className="input-glass h-80 resize-none font-mono text-sm" 
                      placeholder="Paste resume text here...&#10;&#10;John Doe&#10;Software Engineer&#10;john@example.com | +1-234-567-8900&#10;&#10;EXPERIENCE&#10;Senior Developer at TechCorp (2020-2023)&#10;- Led team of 5 developers&#10;- Built scalable microservices...&#10;&#10;SKILLS&#10;Python, JavaScript, React, AWS, Docker, PostgreSQL..." 
                    />
                    {resumeText && (
                      <div className="flex items-center gap-2 text-sm text-slate-400">
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                        <span>{resumeText.split('\n').filter(l => l.trim()).length} lines, {resumeText.length} characters</span>
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            </div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="text-center">
              <button 
                onClick={handleAnalyze} 
                disabled={analyzing || (inputMode === 'pdf' ? !file : !resumeText.trim()) || !jdText.trim()} 
                className="btn-gradient text-lg px-12 py-5 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-3 group">
                {analyzing ? (
                  <><motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }} className="w-6 h-6 border-4 border-white border-t-transparent rounded-full" /><span>Analyzing Resume...</span></>
                ) : (
                  <><Sparkles className="w-6 h-6 group-hover:rotate-12 transition-transform" /><span>Analyze Resume</span></>
                )}
              </button>
            </motion.div>
          </>
        ) : (
          <AnimatePresence>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-8">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", delay: 0.2 }} className="inline-block mb-8">
                  <div className="relative">
                    <motion.div 
                      className={`w-56 h-56 rounded-full bg-gradient-to-br ${getScoreColor(scorePercent)} p-1.5 shadow-2xl`}
                      animate={{ rotate: 360 }} 
                      transition={{ duration: 2, ease: "easeInOut" }}
                    >
                      <div className="w-full h-full rounded-full bg-slate-900 flex flex-col items-center justify-center relative overflow-hidden">
                        <motion.div
                          className="absolute inset-0 opacity-20"
                          animate={{
                            background: [
                              'radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.4) 0%, transparent 50%)',
                              'radial-gradient(circle at 80% 50%, rgba(236, 72, 153, 0.4) 0%, transparent 50%)',
                              'radial-gradient(circle at 20% 50%, rgba(168, 85, 247, 0.4) 0%, transparent 50%)',
                            ],
                          }}
                          transition={{ duration: 3, repeat: Infinity }}
                        />
                        <motion.div 
                          initial={{ opacity: 0, scale: 0 }} 
                          animate={{ opacity: 1, scale: 1 }} 
                          transition={{ delay: 0.5 }}
                          className="text-7xl font-black text-white relative z-10"
                        >
                          {scoreOutOfTen.toFixed(1)}
                        </motion.div>
                        <div className="text-slate-300 text-sm font-bold uppercase tracking-wider relative z-10">out of 10</div>
                        <div className="text-xs text-slate-500 mt-2 font-medium relative z-10">{Math.round(scorePercent)}% Match</div>
                      </div>
                    </motion.div>
                    <motion.div 
                      initial={{ scale: 0, rotate: -180 }} 
                      animate={{ scale: 1, rotate: 0 }} 
                      transition={{ delay: 0.7, type: "spring", bounce: 0.6 }}
                      className="absolute -bottom-6 left-1/2 -translate-x-1/2 z-10"
                    >
                      {(() => {
                        const badge = getScoreBadge(scorePercent);
                        const Icon = badge.icon;
                        return (
                          <div className={`px-6 py-3 rounded-2xl bg-gradient-to-r ${getScoreColor(scorePercent)} shadow-xl backdrop-blur-sm flex items-center gap-3`}>
                            <Icon className="w-5 h-5 text-white" />
                            <span className="text-base font-bold text-white">{badge.text}</span>
                            {scoreTier && (
                              <span className="px-2 py-1 text-xs uppercase tracking-widest rounded-lg bg-white/20 text-white font-black">
                                {scoreTier}
                              </span>
                            )}
                          </div>
                        );
                      })()}
                    </motion.div>
                  </div>
                </motion.div>
              </motion.div>

              {/* Score Breakdown */}
              {(results && (results.global_score !== undefined || results.coverage_score !== undefined)) && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }} className="glass-card">
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <h3 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                      <TrendingUp className="w-5 h-5 text-purple-400" />
                      Score Breakdown
                    </h3>
                    {scoreTier && <span className="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs uppercase tracking-wide text-slate-300">Tier: {scoreTier}</span>}
                  </div>
                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                      <p className="text-sm text-blue-300 mb-1">Semantic Match</p>
                      <p className="text-3xl font-bold text-blue-400">{Math.round(semanticPercent)}%</p>
                      <p className="text-xs text-slate-400 mt-1">Resume language alignment with JD</p>
                    </div>
                    <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
                      <p className="text-sm text-purple-300 mb-1">Requirement Coverage</p>
                      <p className="text-3xl font-bold text-purple-400">{Math.round(coveragePercent)}%</p>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <span className="text-xs px-2 py-0.5 rounded bg-purple-500/20 text-purple-200">Must-have: {Math.round(mustCoveragePercent)}%</span>
                        <span className="text-xs px-2 py-0.5 rounded bg-pink-500/20 text-pink-200">Nice-to-have: {Math.round(niceCoveragePercent)}%</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">Job requirements satisfied</p>
                    </div>
                    <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                      <p className="text-sm text-pink-300 mb-1">Final Score</p>
                      <p className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">{scoreOutOfTen.toFixed(1)}/10</p>
                      <p className="text-xs text-slate-400 mt-1">Weighted AI assessment ({Math.round(scorePercent)}%)</p>
                    </div>
                  </div>
                  {scoreBreakdown.breakdown_points && (
                    <div className="mt-4">
                      <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">Score composition</p>
                      <div className="flex flex-wrap gap-2">
                        {['coverage_points', 'semantic_points', 'must_points', 'nice_points'].map((key) => {
                          const value = scoreBreakdown.breakdown_points?.[key];
                          if (value === undefined || value === null) return null;
                          const label = key.replace('_', ' ').replace('points', '');
                          return (
                            <span key={key} className="text-xs px-2 py-1 rounded bg-white/5 border border-white/10 text-slate-300">
                              {label.trim()}: {Number(value).toFixed(1)} pts
                            </span>
                          );
                        })}
                      </div>
                      {(scoreBreakdown.breakdown_points?.penalties?.length || scoreBreakdown.breakdown_points?.bonuses?.length) && (
                        <div className="flex flex-wrap gap-4 mt-3 text-xs text-slate-400">
                          {Array.isArray(scoreBreakdown.breakdown_points?.bonuses) && scoreBreakdown.breakdown_points.bonuses.length > 0 && (
                            <div>
                              <p className="text-emerald-300 mb-1">Bonuses</p>
                              <ul className="list-disc list-inside space-y-1">
                                {scoreBreakdown.breakdown_points.bonuses.map((bonus, idx) => (
                                  <li key={`bonus-${idx}`}>{bonus}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {Array.isArray(scoreBreakdown.breakdown_points?.penalties) && scoreBreakdown.breakdown_points.penalties.length > 0 && (
                            <div>
                              <p className="text-red-300 mb-1">Penalties</p>
                              <ul className="list-disc list-inside space-y-1">
                                {scoreBreakdown.breakdown_points.penalties.map((penalty, idx) => (
                                  <li key={`penalty-${idx}`}>{penalty}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              )}

              {/* Semantic Matching Details */}
              {semanticDetails && Object.keys(semanticDetails).length > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  transition={{ delay: 0.27 }} 
                  className="glass-card"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                      <Brain className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-cyan-300">Semantic Analysis</h3>
                  </div>
                  <div className="grid md:grid-cols-2 gap-4">
                    <motion.div 
                      whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(6, 182, 212, 0.3)" }}
                      className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 transition-all"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Zap className="w-4 h-4 text-cyan-400" />
                        <p className="text-sm text-cyan-300 font-medium">Overall Similarity</p>
                      </div>
                      <p className="text-3xl font-black bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                        {semanticDetails.overall_similarity || 0}%
                      </p>
                      <p className="text-xs text-slate-400 mt-1">Language alignment score</p>
                    </motion.div>
                    <motion.div 
                      whileHover={{ scale: 1.02, boxShadow: "0 20px 25px -5px rgba(6, 182, 212, 0.3)" }}
                      className="p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 transition-all"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <BarChart3 className="w-4 h-4 text-blue-400" />
                        <p className="text-sm text-blue-300 font-medium">JD-Resume Alignment</p>
                      </div>
                      <p className="text-2xl font-bold text-blue-400">{semanticDetails.jd_resume_alignment || 'N/A'}</p>
                      <p className="text-xs text-slate-400 mt-1">Context relevance: {semanticDetails.context_relevance || 0}%</p>
                    </motion.div>
                  </div>
                </motion.div>
              )}

              {/* Skills Analysis */}
              {skillsAnalysis && skillsAnalysis.resume_skills_count > 0 && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  transition={{ delay: 0.28 }} 
                  className="glass-card"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                      <Code className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-2xl font-bold text-indigo-300">Skills Comparison</h3>
                  </div>
                  
                  <div className="grid md:grid-cols-3 gap-4 mb-6">
                    <motion.div 
                      whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(99, 102, 241, 0.3)" }}
                      className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-green-500/10 border border-emerald-500/20"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Plus className="w-4 h-4 text-emerald-400" />
                        <p className="text-sm text-emerald-300 font-medium">Matched Skills</p>
                      </div>
                      <p className="text-4xl font-black text-emerald-400">{skillsAnalysis.matched_skills_count || 0}</p>
                      <p className="text-xs text-slate-400 mt-1">Match rate: {skillsAnalysis.skill_match_rate || 0}%</p>
                    </motion.div>
                    <motion.div 
                      whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(239, 68, 68, 0.3)" }}
                      className="p-4 rounded-xl bg-gradient-to-br from-red-500/10 to-pink-500/10 border border-red-500/20"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Minus className="w-4 h-4 text-red-400" />
                        <p className="text-sm text-red-300 font-medium">Missing from JD</p>
                      </div>
                      <p className="text-4xl font-black text-red-400">{skillsAnalysis.missing_skills_count || 0}</p>
                      <p className="text-xs text-slate-400 mt-1">Skills to acquire</p>
                    </motion.div>
                    <motion.div 
                      whileHover={{ y: -4, boxShadow: "0 20px 25px -5px rgba(168, 85, 247, 0.3)" }}
                      className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20"
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Plus className="w-4 h-4 text-purple-400" />
                        <p className="text-sm text-purple-300 font-medium">Additional Skills</p>
                      </div>
                      <p className="text-4xl font-black text-purple-400">{skillsAnalysis.additional_skills_count || 0}</p>
                      <p className="text-xs text-slate-400 mt-1">Bonus capabilities</p>
                    </motion.div>
                  </div>

                  <div className="space-y-4">
                    {skillsAnalysis.matched_skills?.length > 0 && (
                      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/20">
                        <div className="flex items-center gap-2 mb-3">
                          <CheckCircle className="w-4 h-4 text-emerald-400" />
                          <p className="text-sm font-semibold text-emerald-300 uppercase tracking-wide">Matched Skills</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {skillsAnalysis.matched_skills.map((skill, i) => (
                            <motion.span 
                              key={i}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.05 * i }}
                              whileHover={{ scale: 1.1, boxShadow: "0 0 20px rgba(16, 185, 129, 0.4)" }}
                              className="px-3 py-1.5 text-sm rounded-full bg-gradient-to-r from-emerald-500/20 to-green-500/20 border border-emerald-500/30 text-emerald-200 font-medium"
                            >
                              {skill}
                            </motion.span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {skillsAnalysis.missing_skills?.length > 0 && (
                      <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
                        <div className="flex items-center gap-2 mb-3">
                          <XCircle className="w-4 h-4 text-red-400" />
                          <p className="text-sm font-semibold text-red-300 uppercase tracking-wide">Missing Skills from JD</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {skillsAnalysis.missing_skills.map((skill, i) => (
                            <motion.span 
                              key={i}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.05 * i }}
                              whileHover={{ scale: 1.1, boxShadow: "0 0 20px rgba(239, 68, 68, 0.4)" }}
                              className="px-3 py-1.5 text-sm rounded-full bg-gradient-to-r from-red-500/20 to-pink-500/20 border border-red-500/30 text-red-200 font-medium"
                            >
                              {skill}
                            </motion.span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {skillsAnalysis.additional_skills?.length > 0 && (
                      <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-500/20">
                        <div className="flex items-center gap-2 mb-3">
                          <Plus className="w-4 h-4 text-purple-400" />
                          <p className="text-sm font-semibold text-purple-300 uppercase tracking-wide">Additional Skills (Bonus)</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {skillsAnalysis.additional_skills.map((skill, i) => (
                            <motion.span 
                              key={i}
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.05 * i }}
                              whileHover={{ scale: 1.1, boxShadow: "0 0 20px rgba(168, 85, 247, 0.4)" }}
                              className="px-3 py-1.5 text-sm rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 text-purple-200 font-medium"
                            >
                              {skill}
                            </motion.span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              <div className="grid md:grid-cols-2 gap-8">
                {missingRequirements.length > 0 && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28 }} className="glass-card md:col-span-2">
                    <div className="flex items-center gap-3 mb-4">
                      <AlertCircle className="w-5 h-5 text-amber-400" />
                      <h3 className="text-2xl font-bold text-amber-300">Missing Must-Haves</h3>
                    </div>
                    <p className="text-sm text-slate-400 mb-4">Focus on these requirements to strengthen the resume against the job description.</p>
                    <div className="space-y-3">
                      {missingRequirements.map((item, idx) => (
                        <div key={idx} className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <p className="font-semibold text-amber-200 tracking-wide">{item.requirement || 'Requirement'}</p>
                            {item.llm_confidence !== undefined && (
                              <span className="text-xs px-2 py-1 rounded bg-amber-500/20 text-amber-200">Confidence {Math.round((item.llm_confidence || 0) * 100)}%</span>
                            )}
                          </div>
                          {item.rationale && <p className="text-xs text-slate-400 mb-2">{item.rationale}</p>}
                          {Array.isArray(item.resume_evidence) && item.resume_evidence.length > 0 && (
                            <div className="mt-2 text-xs text-slate-400">
                              <p className="uppercase text-[10px] tracking-wide text-amber-300 mb-1">Closest resume evidence</p>
                              <div className="space-y-1">
                                {item.resume_evidence.slice(0, 2).map((evidence, evidenceIdx) => (
                                  <blockquote key={evidenceIdx} className="p-2 rounded bg-white/5 border border-white/10">
                                    “{evidence.text || evidence}”
                                  </blockquote>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }} className="glass-card">
                  <div className="flex items-center gap-3 mb-6"><div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-green-500 flex items-center justify-center"><CheckCircle className="w-5 h-5 text-white" /></div><h3 className="text-2xl font-bold text-emerald-300">Strengths</h3></div>
                  <div className="space-y-3">
                    {results.strengths?.map((strength, i) => (<motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 + i * 0.1 }} className="flex items-start gap-3 p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 hover:bg-emerald-500/10 transition-colors"><CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" /><span className="text-slate-200">{strength}</span></motion.div>))}
                  </div>
                </motion.div>

                <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }} className="glass-card">
                  <div className="flex items-center gap-3 mb-6"><div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-pink-500 flex items-center justify-center"><XCircle className="w-5 h-5 text-white" /></div><h3 className="text-2xl font-bold text-red-300">Gaps</h3></div>
                  <div className="space-y-3">
                    {results.gaps?.map((gap, i) => (<motion.div key={i} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.5 + i * 0.1 }} className="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/20 hover:bg-red-500/10 transition-colors"><XCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" /><span className="text-slate-200">{gap}</span></motion.div>))}
                  </div>
                </motion.div>
              </div>

              <motion.div 
                initial={{ opacity: 0, y: 20 }} 
                animate={{ opacity: 1, y: 0 }} 
                transition={{ delay: 0.6 }} 
                className="glass-card relative overflow-hidden"
              >
                {/* Animated background gradient */}
                <motion.div
                  className="absolute inset-0 opacity-10"
                  animate={{
                    background: [
                      'radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.5) 0%, transparent 50%)',
                      'radial-gradient(circle at 100% 100%, rgba(168, 85, 247, 0.5) 0%, transparent 50%)',
                      'radial-gradient(circle at 0% 100%, rgba(236, 72, 153, 0.5) 0%, transparent 50%)',
                      'radial-gradient(circle at 100% 0%, rgba(59, 130, 246, 0.5) 0%, transparent 50%)',
                      'radial-gradient(circle at 0% 0%, rgba(59, 130, 246, 0.5) 0%, transparent 50%)',
                    ],
                  }}
                  transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                />
                
                <div className="relative z-10">
                  <div className="flex items-center gap-3 mb-6">
                    <motion.div 
                      animate={{ 
                        boxShadow: [
                          "0 0 20px rgba(59, 130, 246, 0.3)",
                          "0 0 30px rgba(168, 85, 247, 0.4)",
                          "0 0 20px rgba(59, 130, 246, 0.3)",
                        ]
                      }}
                      transition={{ duration: 3, repeat: Infinity }}
                      className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg"
                    >
                      <Sparkles className="w-6 h-6 text-white" />
                    </motion.div>
                    <div>
                      <h3 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                        AI Recommendation
                      </h3>
                      <p className="text-xs text-slate-400 mt-1">Powered by advanced language models</p>
                    </div>
                  </div>
                  
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                    className="relative"
                  >
                    <div className="absolute -left-4 top-0 w-1 h-full bg-gradient-to-b from-blue-500 via-purple-500 to-pink-500 rounded-full" />
                    <div className="pl-6 pr-4 py-6 rounded-2xl bg-gradient-to-br from-blue-500/5 via-purple-500/5 to-pink-500/5 border border-blue-500/20 backdrop-blur-sm">
                      <p className="text-slate-100 text-lg leading-relaxed font-medium">
                        {results.recommendation}
                      </p>
                    </div>
                  </motion.div>
                  
                  {/* Decorative elements */}
                  <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
                    <motion.div
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      className="w-2 h-2 rounded-full bg-blue-400"
                    />
                    <span>AI-generated insights</span>
                  </div>
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }} className="text-center">
                <button onClick={resetAnalysis} className="btn-gradient px-8 py-4"><span>Analyze Another Resume</span></button>
              </motion.div>
            </motion.div>
          </AnimatePresence>
        )
        ) : (
          /* Recent Analyses Tab */
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
            <motion.div 
              initial={{ opacity: 0, y: -20 }} 
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.1, type: "spring" }}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/10 border border-purple-500/30 mb-4"
              >
                <History className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-purple-300 font-medium">Analysis History</span>
              </motion.div>
              <h2 className="text-5xl font-black mb-3 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
                Recent Analyses
              </h2>
              <p className="text-lg text-slate-400 max-w-2xl mx-auto">Review and compare your previous resume screenings</p>
            </motion.div>

            {loadingRecent ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-20"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                  className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-6"
                />
                <p className="text-lg text-slate-300 font-medium">Loading your analyses...</p>
                <p className="text-sm text-slate-500 mt-2">This won't take long</p>
              </motion.div>
            ) : recentAnalyses.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card text-center py-20"
              >
                <motion.div
                  animate={{ y: [0, -10, 0] }}
                  transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
                  className="mb-6"
                >
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-2 border-purple-500/30 flex items-center justify-center mx-auto">
                    <History className="w-12 h-12 text-purple-400" />
                  </div>
                </motion.div>
                <h3 className="text-2xl font-bold text-slate-200 mb-3">No Analyses Yet</h3>
                <p className="text-slate-400 mb-8 max-w-md mx-auto">Start screening resumes to build your analysis history. Your insights will appear here.</p>
                <button
                  onClick={() => setActiveTab('analyze')}
                  className="btn-gradient px-8 py-4 text-lg inline-flex items-center gap-3"
                >
                  <Sparkles className="w-5 h-5" />
                  <span>Start First Analysis</span>
                </button>
              </motion.div>
            ) : (
              <>
                {/* Stats Overview */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
                >
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <FileText className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-slate-200">{recentAnalyses.length}</p>
                        <p className="text-xs text-slate-400">Total Analyses</p>
                      </div>
                    </div>
                  </div>
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-green-500 flex items-center justify-center">
                        <Award className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-slate-200">
                          {recentAnalyses.filter(a => (a.final_score || 0) >= 7).length}
                        </p>
                        <p className="text-xs text-slate-400">Strong Matches (7+)</p>
                      </div>
                    </div>
                  </div>
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-slate-200">
                          {recentAnalyses.length > 0 
                            ? ((recentAnalyses.reduce((sum, a) => sum + (a.final_score || 0), 0) / recentAnalyses.length)).toFixed(1)
                            : '0.0'
                          }
                        </p>
                        <p className="text-xs text-slate-400">Average Score</p>
                      </div>
                    </div>
                  </div>
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                        <Clock className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-slate-200">
                          {recentAnalyses[0]?.created_at 
                            ? new Date(recentAnalyses[0].created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                            : 'N/A'
                          }
                        </p>
                        <p className="text-xs text-slate-400">Latest Analysis</p>
                      </div>
                    </div>
                  </div>
                </motion.div>

                {/* Analysis Cards */}
                <div className="grid gap-5">
                  {recentAnalyses.map((analysis, index) => {
                    const scorePercentLocal = typeof analysis.final_score_percent === 'number'
                      ? analysis.final_score_percent
                      : (typeof analysis.final_score === 'number' ? analysis.final_score * 10 : 0);
                    const scoreOutOfTenLocal = typeof analysis.final_score === 'number'
                      ? analysis.final_score
                      : scorePercentLocal / 10;
                    const badgeMeta = getScoreBadge(scorePercentLocal);
                    const BadgeIcon = badgeMeta.icon;
                    const semanticPercentLocal = typeof analysis.semantic_score_percent === 'number'
                      ? analysis.semantic_score_percent
                      : Math.round((analysis.semantic_score || 0) * 100);
                    const coveragePercentLocal = typeof analysis.coverage_score_percent === 'number'
                      ? analysis.coverage_score_percent
                      : Math.round((analysis.coverage_score || 0) * 100);
                    const mustPercentLocal = typeof analysis.must_coverage_percent === 'number'
                      ? analysis.must_coverage_percent
                      : coveragePercentLocal;

                    return (
                      <motion.div
                        key={analysis.analysis_id || index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="glass-card hover:shadow-xl hover:shadow-purple-500/20 transition-all group"
                      >
                        <div className="flex items-start gap-6">
                          {/* Score Circle */}
                          <motion.div
                            whileHover={{ scale: 1.05, rotate: 5 }}
                            className="flex-shrink-0"
                          >
                            <div className={`w-24 h-24 rounded-full bg-gradient-to-br ${getScoreColor(scorePercentLocal)} p-1`}>
                              <div className="w-full h-full rounded-full bg-slate-900 flex flex-col items-center justify-center">
                                <span className="text-2xl font-black text-white">{scoreOutOfTenLocal.toFixed(1)}</span>
                                <span className="text-[10px] text-slate-400 uppercase tracking-wide">Score</span>
                              </div>
                            </div>
                          </motion.div>

                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-start justify-between gap-4 mb-3">
                              <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                  <h3 className="text-xl font-bold text-slate-100 truncate">
                                    {analysis.candidate || 'Unknown Candidate'}
                                  </h3>
                                  <div className={`flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r ${getScoreColor(scorePercentLocal)} bg-opacity-20 border border-current`}>
                                    <BadgeIcon className="w-4 h-4" />
                                    <span className="text-sm font-semibold">{badgeMeta.text}</span>
                                  </div>
                                  {analysis.score_tier && (
                                    <span className="px-2 py-1 text-xs uppercase tracking-wider rounded bg-white/5 border border-white/10 text-slate-400 font-bold">
                                      {analysis.score_tier}
                                    </span>
                                  )}
                                </div>
                                
                                <div className="flex items-center gap-4 text-sm text-slate-400 mb-4">
                                  <div className="flex items-center gap-1.5">
                                    <Clock className="w-4 h-4" />
                                    <span>
                                      {analysis.created_at ? new Date(analysis.created_at).toLocaleDateString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                      }) : 'Unknown date'}
                                    </span>
                                  </div>
                                  {analysis.email && analysis.email !== 'Not found' && (
                                    <>
                                      <span className="text-slate-600">•</span>
                                      <span className="truncate">{analysis.email}</span>
                                    </>
                                  )}
                                  {analysis.phone && analysis.phone !== 'Not found' && (
                                    <>
                                      <span className="text-slate-600">•</span>
                                      <span>{analysis.phone}</span>
                                    </>
                                  )}
                                </div>
                              </div>
                            </div>
                            
                            {/* Score Metrics */}
                            <div className="grid grid-cols-3 gap-3 mb-4">
                              <div className="p-3 rounded-lg bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20">
                                <div className="flex items-center gap-2 mb-1">
                                  <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                                  <p className="text-xs text-blue-300 font-medium">Semantic</p>
                                </div>
                                <p className="text-lg font-bold text-blue-400">{Math.round(semanticPercentLocal)}%</p>
                              </div>
                              <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20">
                                <div className="flex items-center gap-2 mb-1">
                                  <div className="w-2 h-2 rounded-full bg-purple-400"></div>
                                  <p className="text-xs text-purple-300 font-medium">Coverage</p>
                                </div>
                                <p className="text-lg font-bold text-purple-400">{Math.round(coveragePercentLocal)}%</p>
                              </div>
                              <div className="p-3 rounded-lg bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 border border-emerald-500/20">
                                <div className="flex items-center gap-2 mb-1">
                                  <div className="w-2 h-2 rounded-full bg-emerald-400"></div>
                                  <p className="text-xs text-emerald-300 font-medium">Must-Have</p>
                                </div>
                                <p className="text-lg font-bold text-emerald-400">{Math.round(mustPercentLocal)}%</p>
                              </div>
                            </div>
                            
                            {/* JD Preview */}
                            {analysis.jd_preview && (
                              <div className="mb-4 p-3 rounded-lg bg-white/5 border border-white/10">
                                <p className="text-xs uppercase tracking-wide text-slate-500 mb-1.5 font-semibold">Job Description Preview</p>
                                <p className="text-sm text-slate-300 line-clamp-2">{analysis.jd_preview}</p>
                              </div>
                            )}
                            
                            {/* Top Skills */}
                            {analysis.skills && analysis.skills.length > 0 && (
                              <div className="mb-4">
                                <p className="text-xs uppercase tracking-wide text-slate-500 mb-2 font-semibold">Key Skills</p>
                                <div className="flex gap-2 flex-wrap">
                                  {analysis.skills.slice(0, 10).map((skill, i) => (
                                    <span key={i} className="px-3 py-1 text-xs rounded-full bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 text-purple-200 font-medium">
                                      {skill}
                                    </span>
                                  ))}
                                  {analysis.skills.length > 10 && (
                                    <span className="px-3 py-1 text-xs rounded-full bg-white/5 border border-white/10 text-slate-400">
                                      +{analysis.skills.length - 10} more
                                    </span>
                                  )}
                                </div>
                              </div>
                            )}

                            {/* Quick Insights */}
                            {(analysis.top_strengths?.length > 0 || analysis.improvement_areas?.length > 0) && (
                              <div className="grid md:grid-cols-2 gap-3 mb-4">
                                {analysis.top_strengths?.length > 0 && (
                                  <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                      <CheckCircle className="w-4 h-4 text-emerald-400" />
                                      <p className="text-xs font-semibold text-emerald-300">Top Strength</p>
                                    </div>
                                    <p className="text-sm text-slate-300 line-clamp-2">{analysis.top_strengths[0]}</p>
                                  </div>
                                )}
                                {analysis.improvement_areas?.length > 0 && (
                                  <div className="p-3 rounded-lg bg-amber-500/5 border border-amber-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                      <AlertCircle className="w-4 h-4 text-amber-400" />
                                      <p className="text-xs font-semibold text-amber-300">Key Gap</p>
                                    </div>
                                    <p className="text-sm text-slate-300 line-clamp-2">{analysis.improvement_areas[0]}</p>
                                  </div>
                                )}
                              </div>
                            )}
                            
                            {/* View Details Button */}
                            <button 
                              onClick={() => {
                                const semanticDecimal = typeof analysis.semantic_score === 'number'
                                  ? analysis.semantic_score
                                  : (analysis.semantic_score_percent || 0) / 100;
                                const coverageDecimal = typeof analysis.coverage_score === 'number'
                                  ? analysis.coverage_score
                                  : (analysis.coverage_score_percent || 0) / 100;
                                const finalScoreDecimal = typeof analysis.final_score === 'number'
                                  ? analysis.final_score
                                  : scoreOutOfTenLocal;
                                setResults({
                                  final_score: finalScoreDecimal,
                                  final_score_percent: scorePercentLocal,
                                  global_score: semanticDecimal,
                                  coverage_score: coverageDecimal,
                                  score_tier: analysis.score_tier,
                                  score_breakdown: analysis.score_breakdown,
                                  coverage_summary: analysis.coverage_summary,
                                  missing_requirements: analysis.missing_requirements,
                                  strengths: analysis.top_strengths || [],
                                  gaps: analysis.improvement_areas || [],
                                  recommendation: analysis.overall_comment_full || analysis.overall_comment || 'No recommendation available',
                                  skills: analysis.skills || [],
                                  must_have_coverage: analysis.must_coverage_percent,
                                  nice_to_have_coverage: analysis.nice_coverage_percent,
                                  semantic_details: analysis.semantic_details || {},
                                  skills_analysis: analysis.skills_analysis || {},
                                  candidate: {
                                    name: analysis.candidate || 'Unknown',
                                    email: analysis.email || 'Not found',
                                    phone: analysis.phone || 'Not found'
                                  }
                                });
                                setActiveTab('analyze');
                              }}
                              className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-purple-500/10 to-pink-500/10 hover:from-purple-500/20 hover:to-pink-500/20 border border-purple-500/30 hover:border-purple-500/50 transition-all text-sm font-semibold text-purple-200 flex items-center justify-center gap-2 group-hover:scale-[1.02]"
                            >
                              <Sparkles className="w-4 h-4" />
                              <span>View Full Analysis</span>
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
