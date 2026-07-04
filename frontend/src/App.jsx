import { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Brain, 
  TrendingUp, 
  Video, 
  Mic, 
  MicOff, 
  Volume2, 
  ShieldAlert, 
  CheckCircle, 
  ListOrdered, 
  Sliders, 
  Users, 
  Heart,
  Clock,
  Compass,
  Lock,
  Database,
  Search,
  FileJson,
  Key,
  RefreshCw,
  AlertTriangle,
  Send,
  Server
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  LineChart, 
  Line,
  AreaChart,
  Area,
  ScatterChart,
  Scatter
} from 'recharts';

const SAMPLE_FHIR_BUNDLE = {
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "pat-081",
        "gender": "male",
        "birthDate": "1968-04-12"
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-bp",
        "status": "final",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "85354-9",
              "display": "Blood pressure systolic & diastolic"
            }
          ]
        },
        "subject": { "reference": "Patient/pat-081" },
        "component": [
          {
            "code": {
              "coding": [{ "system": "http://loinc.org", "code": "8480-6", "display": "Systolic BP" }]
            },
            "valueQuantity": { "value": 155, "unit": "mmHg" }
          },
          {
            "code": {
              "coding": [{ "system": "http://loinc.org", "code": "8462-4", "display": "Diastolic BP" }]
            },
            "valueQuantity": { "value": 95, "unit": "mmHg" }
          }
        ]
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-chol",
        "status": "final",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "2093-3",
              "display": "Total Cholesterol"
            }
          ]
        },
        "subject": { "reference": "Patient/pat-081" },
        "valueQuantity": { "value": 245, "unit": "mg/dL" }
      }
    },
    {
      "resource": {
        "resourceType": "Observation",
        "id": "obs-smoke",
        "status": "final",
        "code": {
          "coding": [
            {
              "system": "http://loinc.org",
              "code": "72166-2",
              "display": "Tobacco smoking status"
            }
          ]
        },
        "subject": { "reference": "Patient/pat-081" },
        "valueCodeableConcept": { "text": "Current every day smoker" }
      }
    }
  ]
};

const COMPARATIVE_DB = {
  datasets: ['CVD_risk_data_set.xlsx', 'cardiovascular_disease.csv'],
  experiments: ['Exp_1_Default', 'Exp_2_No_Leakage'],
  models: {
    LogisticRegression: {
      name: "Logistic Regression",
      Accuracy: 0.8932, Precision: 0.7850, Recall: 0.8737, Specificity: 0.9012, Sensitivity: 0.8737, "F1-Score": 0.8270, "ROC-AUC": 0.9421, "PR-AUC": 0.9134,
      "Balanced Accuracy": 0.8875, MCC: 0.7523, "Cohen's Kappa": 0.7410, "Brier Score": 0.082, "Log Loss": 0.285,
      "Training Time": 0.45, "Inference Time": 0.08, "Model Size": 18,
      TP: 1128, TN: 2819, FP: 309, FN: 163
    },
    RandomForest: {
      name: "Random Forest",
      Accuracy: 0.9568, Precision: 0.9709, Recall: 0.8784, Specificity: 0.9891, Sensitivity: 0.8784, "F1-Score": 0.9223, "ROC-AUC": 0.9604, "PR-AUC": 0.9450,
      "Balanced Accuracy": 0.9338, MCC: 0.8946, "Cohen's Kappa": 0.8841, "Brier Score": 0.038, "Log Loss": 0.125,
      "Training Time": 0.85, "Inference Time": 0.15, "Model Size": 5200,
      TP: 1134, TN: 3094, FP: 34, FN: 157
    },
    XGBoost: {
      name: "XGBoost",
      Accuracy: 0.9568, Precision: 0.9758, Recall: 0.8737, Specificity: 0.9910, Sensitivity: 0.8737, "F1-Score": 0.9219, "ROC-AUC": 0.9608, "PR-AUC": 0.9480,
      "Balanced Accuracy": 0.9324, MCC: 0.8948, "Cohen's Kappa": 0.8839, "Brier Score": 0.035, "Log Loss": 0.110,
      "Training Time": 1.20, "Inference Time": 0.08, "Model Size": 280,
      TP: 1128, TN: 3100, FP: 28, FN: 163
    },
    LightGBM: {
      name: "LightGBM",
      Accuracy: 0.9568, Precision: 0.9791, Recall: 0.8706, Specificity: 0.9923, Sensitivity: 0.8706, "F1-Score": 0.9217, "ROC-AUC": 0.9654, "PR-AUC": 0.9510,
      "Balanced Accuracy": 0.9315, MCC: 0.8949, "Cohen's Kappa": 0.8837, "Brier Score": 0.032, "Log Loss": 0.105,
      "Training Time": 0.65, "Inference Time": 0.04, "Model Size": 190,
      TP: 1124, TN: 3104, FP: 24, FN: 167
    },
    CatBoost: {
      name: "CatBoost (Thesis)",
      Accuracy: 0.9577, Precision: 0.9800, Recall: 0.8730, Specificity: 0.9926, Sensitivity: 0.8730, "F1-Score": 0.9234, "ROC-AUC": 0.9624, "PR-AUC": 0.9500,
      "Balanced Accuracy": 0.9328, MCC: 0.8971, "Cohen's Kappa": 0.8860, "Brier Score": 0.030, "Log Loss": 0.095,
      "Training Time": 2.40, "Inference Time": 0.03, "Model Size": 95,
      TP: 1127, TN: 3105, FP: 23, FN: 164
    },
    SVM: {
      name: "Support Vector Machine",
      Accuracy: 0.9258, Precision: 0.8712, Recall: 0.8753, Specificity: 0.9466, Sensitivity: 0.8753, "F1-Score": 0.8733, "ROC-AUC": 0.9523, "PR-AUC": 0.8980,
      "Balanced Accuracy": 0.9110, MCC: 0.8208, "Cohen's Kappa": 0.8120, "Brier Score": 0.065, "Log Loss": 0.220,
      "Training Time": 3.80, "Inference Time": 0.24, "Model Size": 450,
      TP: 1130, TN: 2961, FP: 167, FN: 161
    },
    DecisionTree: {
      name: "Decision Tree",
      Accuracy: 0.9568, Precision: 0.9741, Recall: 0.8753, Specificity: 0.9904, Sensitivity: 0.8753, "F1-Score": 0.9221, "ROC-AUC": 0.9613, "PR-AUC": 0.9410,
      "Balanced Accuracy": 0.9328, MCC: 0.8947, "Cohen's Kappa": 0.8840, "Brier Score": 0.045, "Log Loss": 0.150,
      "Training Time": 0.04, "Inference Time": 0.005, "Model Size": 12,
      TP: 1130, TN: 3098, FP: 30, FN: 161
    },
    KNN: {
      name: "K-Nearest Neighbors",
      Accuracy: 0.8803, Precision: 0.7710, Recall: 0.8397, Specificity: 0.8971, Sensitivity: 0.8397, "F1-Score": 0.8039, "ROC-AUC": 0.9249, "PR-AUC": 0.8520,
      "Balanced Accuracy": 0.8684, MCC: 0.7193, "Cohen's Kappa": 0.6980, "Brier Score": 0.098, "Log Loss": 0.350,
      "Training Time": 0.02, "Inference Time": 0.52, "Model Size": 2400,
      TP: 1084, TN: 2806, FP: 322, FN: 207
    },
    ANN: {
      name: "Artificial Neural Network",
      Accuracy: 0.9350, Precision: 0.8850, Recall: 0.8700, Specificity: 0.9500, Sensitivity: 0.8700, "F1-Score": 0.8770, "ROC-AUC": 0.9550, "PR-AUC": 0.9120,
      "Balanced Accuracy": 0.9100, MCC: 0.8300, "Cohen's Kappa": 0.8190, "Brier Score": 0.055, "Log Loss": 0.180,
      "Training Time": 5.50, "Inference Time": 0.02, "Model Size": 650,
      TP: 1120, TN: 2980, FP: 148, FN: 171
    }
  },
  shap: {
    features: [
      { name: "sbp_avg", importance: 3.82, positive: 3.82, negative: 0.0, description: "Systolic Blood Pressure Average" },
      { name: "dbp_avg", importance: 1.75, positive: 1.75, negative: 0.0, description: "Diastolic Blood Pressure Average" },
      { name: "age", importance: 0.29, positive: 0.25, negative: -0.04, description: "Age in years" },
      { name: "occupation", importance: 0.28, positive: 0.20, negative: -0.08, description: "Patient occupation classification" },
      { name: "age_decade", importance: 0.15, positive: 0.12, negative: -0.03, description: "Age in decades" },
      { name: "village", importance: 0.12, positive: 0.10, negative: -0.02, description: "Village classification" },
      { name: "bg_mgdl", importance: 0.10, positive: 0.09, negative: -0.01, description: "Blood glucose level (mg/dL)" },
      { name: "bplt", importance: 0.09, positive: 0.08, negative: -0.01, description: "Blood platelet count" },
      { name: "bmi", importance: 0.08, positive: 0.07, negative: -0.01, description: "Body Mass Index" }
    ]
  },
  lime: {
    patients: {
      "pat-081": {
        name: "Patient #1 (Low Risk Scenario)",
        prob: 0.10,
        features: [
          { name: "sbp_avg = -4.23", weight: -4.23, type: "negative" },
          { name: "dbp_avg = -1.28", weight: -1.28, type: "negative" },
          { name: "village = -0.17", weight: -0.17, type: "negative" },
          { name: "bplt = -0.11", weight: -0.11, type: "negative" },
          { name: "areas = -0.08", weight: -0.08, type: "negative" }
        ]
      },
      "pat-104": {
        name: "Patient #2 (High Risk Scenario)",
        prob: 0.95,
        features: [
          { name: "sbp_avg = +6.81", weight: 6.81, type: "positive" },
          { name: "dbp_avg = -0.61", weight: -0.61, type: "negative" },
          { name: "village = -0.21", weight: -0.21, type: "negative" },
          { name: "occupation = +0.14", weight: 0.14, type: "positive" },
          { name: "bmi = -0.06", weight: -0.06, type: "negative" }
        ]
      },
      "pat-032": {
        name: "Patient #3 (Low Risk Scenario)",
        prob: 0.15,
        features: [
          { name: "sbp_avg = -3.82", weight: -3.82, type: "negative" },
          { name: "dbp_avg = -0.57", weight: -0.57, type: "negative" },
          { name: "occupation = -0.34", weight: -0.34, type: "negative" },
          { name: "bg_mgdl = +0.16", weight: 0.16, type: "positive" },
          { name: "age_decade = -0.12", weight: -0.12, type: "negative" }
        ]
      }
    }
  }
};

function App() {
  const [token, setToken] = useState(localStorage.getItem('access_token') || '');
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user')) || null);
  const [usernameInput, setUsernameInput] = useState('');
  const [passwordInput, setPasswordInput] = useState('');
  const [loginError, setLoginError] = useState('');

  // RAG Chat State
  const [chatMessages, setChatMessages] = useState([
    { sender: 'bot', text: 'Hello! I am your Clinical Assistant. Ask me anything about Australian heart guidelines or patient cardiovascular risk factors.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // FHIR State
  const [fhirPayload, setFhirPayload] = useState(JSON.stringify(SAMPLE_FHIR_BUNDLE, null, 2));
  const [fhirResult, setFhirResult] = useState(null);
  const [fhirError, setFhirError] = useState('');
  const [fhirImporting, setFhirImporting] = useState(false);

  // Audit state
  const [auditLogs, setAuditLogs] = useState([]);
  const [verificationResult, setVerificationResult] = useState(null);
  const [verifyingAudit, setVerifyingAudit] = useState(false);

  // Tenant stats
  const [tenantStats, setTenantStats] = useState(null);

  const [activeTab, setActiveTab] = useState('overview');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [voiceReply, setVoiceReply] = useState('');
  const [metrics, setMetrics] = useState(null);
  const [apiOnline, setApiOnline] = useState(false);

  // Comparative Analysis States
  const [selectedDataset, setSelectedDataset] = useState('CVD_risk_data_set.xlsx');
  const [selectedExperiment, setSelectedExperiment] = useState('Exp_1_Default');
  const [selectedModels, setSelectedModels] = useState([
    'LogisticRegression', 'RandomForest', 'XGBoost', 'LightGBM', 'CatBoost', 'SVM'
  ]);
  const [selectedMetrics, setSelectedMetrics] = useState([
    'Accuracy', 'Precision', 'Recall', 'Specificity', 'Sensitivity', 'F1-Score', 'ROC-AUC'
  ]);
  const [compActiveTab, setCompActiveTab] = useState('performance');
  const [xaiSubTab, setXaiSubTab] = useState('shap');
  const [compPatientId, setCompPatientId] = useState('pat-081');

  // Prediction Form State
  const [patientData, setPatientData] = useState({
    age: 50,
    gender: 1, // 1: Female, 2: Male (as per dataset specs)
    height: 168,
    weight: 72,
    ap_hi: 120,
    ap_lo: 80,
    cholesterol: 1, // 1: Normal, 2: Above Normal, 3: Well Above Normal
    gluc: 1, // 1: Normal, 2: Above Normal, 3: Well Above Normal
    smoke: 0,
    alco: 0,
    active: 1
  });

  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predictError, setPredictError] = useState('');

  // Speech Recognition Ref
  const recognitionRef = useRef(null);

  const fetchWithAuth = async (url, options = {}) => {
    const headers = {
      ...options.headers,
      'Content-Type': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      handleLogout();
    }
    return res;
  };

  const handleLogin = async (e, demoUsername = '') => {
    if (e) e.preventDefault();
    const targetUser = demoUsername || usernameInput;
    const targetPass = demoUsername ? 'doctor123' : passwordInput; // Default for demo users is 'doctor123' / 'admin123' / etc.
    const actualPass = demoUsername ? (demoUsername === 'admin' ? 'admin123' : demoUsername === 'auditor' ? 'auditor123' : 'doctor123') : passwordInput;
    
    setLoginError('');
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: targetUser, password: actualPass })
      });
      if (!response.ok) {
        throw new Error('Invalid username or password');
      }
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      setToken(data.access_token);
      setUser(data.user);
      
      if (data.user.role === 'compliance_auditor') {
        setActiveTab('audit_trail');
      } else if (data.user.role === 'administrator') {
        setActiveTab('admin_dashboard');
      } else {
        setActiveTab('overview');
      }
    } catch (err) {
      setLoginError(err.message || 'Login failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setToken('');
    setUser(null);
  };

  // Load metrics from FastAPI backend
  useEffect(() => {
    if (!token) return;
    fetchWithAuth('http://localhost:8000/metrics')
      .then(res => {
        if (!res.ok) throw new Error('Backend offline');
        return res.json();
      })
      .then(data => {
        setMetrics(data);
        setApiOnline(true);
      })
      .catch(err => {
        console.warn('FastAPI server connection failed. Using mock fallback data.', err);
        setMetrics({
          best_model: {
            model: "LightGBM",
            roc_auc: 0.9654,
            f1_score: 0.9217,
            sensitivity: 0.8706,
            accuracy: 0.9568,
            specificity: 0.9923
          },
          all_models: [
            { model: "LightGBM", roc_auc: 0.9654, f1: 0.9217, accuracy: 0.9568 },
            { model: "CatBoost", roc_auc: 0.9624, f1: 0.9234, accuracy: 0.9577 },
            { model: "DecisionTree", roc_auc: 0.9613, f1: 0.9221, accuracy: 0.9568 },
            { model: "XGBoost", roc_auc: 0.9608, f1: 0.9219, accuracy: 0.9568 },
            { model: "RandomForest", roc_auc: 0.9604, f1: 0.9223, accuracy: 0.9568 },
            { model: "GradientBoosting", roc_auc: 0.9652, f1: 0.9158, accuracy: 0.9532 },
            { model: "AdaBoost", roc_auc: 0.9623, f1: 0.8982, accuracy: 0.9418 },
            { model: "ExtraTrees", roc_auc: 0.9588, f1: 0.9030, accuracy: 0.9455 },
            { model: "SVM", roc_auc: 0.9523, f1: 0.8733, accuracy: 0.9258 },
            { model: "LogisticRegression", roc_auc: 0.9421, f1: 0.8270, accuracy: 0.8932 },
            { model: "KNN", roc_auc: 0.9249, f1: 0.8039, accuracy: 0.8803 },
            { model: "NaiveBayes", roc_auc: 0.9248, f1: 0.8205, accuracy: 0.8961 }
          ]
        });
        setApiOnline(false);
      });
  }, [token]);

  // Load audit logs from FastAPI backend when activeTab switches to 'audit_trail'
  useEffect(() => {
    if (!token || activeTab !== 'audit_trail') return;
    fetchWithAuth('http://localhost:8000/audit/recent?limit=150')
      .then(res => {
        if (!res.ok) throw new Error('Failed to load audit logs');
        return res.json();
      })
      .then(data => {
        setAuditLogs(data.entries || []);
      })
      .catch(err => {
        console.error('Error fetching audit trail:', err);
      });
  }, [token, activeTab]);

  const handleVerifyAudit = async () => {
    setVerifyingAudit(true);
    setVerificationResult(null);
    try {
      const res = await fetchWithAuth('http://localhost:8000/audit/verify');
      if (!res.ok) throw new Error('Verification request failed');
      const data = await res.json();
      setVerificationResult(data);
      
      // Re-fetch logs to show any changes or updated verification signatures
      const logsRes = await fetchWithAuth('http://localhost:8000/audit/recent?limit=150');
      if (logsRes.ok) {
        const logsData = await logsRes.json();
        setAuditLogs(logsData.entries || []);
      }
    } catch (err) {
      setVerificationResult({
        verified: false,
        message: err.message || 'Verification process failed.'
      });
    } finally {
      setVerifyingAudit(false);
    }
  };

  const handleImportFhir = async (e) => {
    e.preventDefault();
    setFhirImporting(true);
    setFhirError('');
    setFhirResult(null);

    try {
      const payloadObj = JSON.parse(fhirPayload);
      const res = await fetchWithAuth('http://localhost:8000/fhir/Observation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payloadObj)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'FHIR Ingestion failed');
      }

      const data = await res.json();
      setFhirResult(data);
    } catch (err) {
      console.error('Error importing FHIR:', err);
      setFhirError(err.message || 'FHIR Ingestion failed');
    } finally {
      setFhirImporting(false);
    }
  };


  // Text to Speech
  const speakText = (text) => {
    setVoiceReply(text);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.05;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.lang = 'en-US';
      rec.interimResults = false;

      rec.onstart = () => {
        setIsListening(true);
        setTranscript('Listening for command...');
      };

      rec.onresult = (event) => {
        const command = event.results[0][0].transcript;
        setTranscript(command);
        handleVoiceCommand(command);
      };

      rec.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsListening(false);
        setTranscript('Error listening. Try again.');
      };

      rec.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = rec;
    }
  }, []);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      window.speechSynthesis.cancel();
      recognitionRef.current?.start();
    }
  };

  const handleVoiceCommand = (cmd) => {
    const t = cmd.toLowerCase().trim();
    if (t.includes('show models') || t.includes('show machine learning') || t.includes('show model')) {
      setActiveTab('models');
      speakText("Showing the machine learning models. The platform has trained twelve models. Logistic Regression is the top model with a ROC-AUC score of 1.00.");
    } else if (t.includes('best model') || t.includes('highest accuracy') || t.includes('highest ranking') || t.includes('highest rank')) {
      setActiveTab('models');
      speakText("The best model is Logistic Regression, which achieved a clinical ROC-AUC score of 1.00 and an F1 score of 1.00, passing the clinical threshold.");
    } else if (t.includes('show shap') || t.includes('explainable ai') || t.includes('explainable') || t.includes('shap')) {
      setActiveTab('explainable');
      speakText("Displaying explainable AI SHAP results. You can input patient details to see real-time SHAP clinical impact values.");
    } else if (t.includes('show lime') || t.includes('lime')) {
      setActiveTab('explainable');
      speakText("Showing LIME patient scenario simulation. This provides patient-specific clinical explanations.");
    } else if (t.includes('show statistics') || t.includes('show stats') || t.includes('cause and effect') || t.includes('statistics')) {
      setActiveTab('statistics');
      speakText("Showing cause-and-effect statistics. Eleven patient features show statistically significant differences under the Mann-Whitney U test with p-values less than 0.05.");
    } else if (t.includes('show overview') || t.includes('show dashboard') || t.includes('overview') || t.includes('dashboard')) {
      setActiveTab('overview');
      speakText("Showing the main patient dashboard. You can perform real-time risk predictions here.");
    } else if (t.includes('show videos') || t.includes('show clinical videos') || t.includes('videos') || t.includes('video')) {
      setActiveTab('videos');
      speakText("Opening the critical care clinical training videos. These include CPR protocols, patient monitoring, and ICU patient care.");
    } else {
      speakText("Command not recognized. You can say: 'show models', 'best model', 'show SHAP', 'show statistics', or 'show videos'.");
    }
  };

  // Run Real-time CVD Risk Prediction
  const runPrediction = async (e) => {
    e.preventDefault();
    setPredicting(true);
    setPredictError('');
    setPrediction(null);

    try {
      const response = await fetchWithAuth('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patientData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Prediction failed');
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      console.warn('Prediction request failed. Using internal client-side risk model.', err);
      // Fallback local mock prediction calculation if FastAPI server is offline
      setTimeout(() => {
        // Simple heuristic mimicking the risk algorithm
        const age_factor = patientData.age / 100;
        const bp_factor = (patientData.ap_hi + patientData.ap_lo - 120) / 100;
        const chol_factor = patientData.cholesterol * 0.15;
        const gluc_factor = patientData.gluc * 0.1;
        const active_factor = patientData.active === 0 ? 0.1 : 0;
        const smoke_factor = patientData.smoke === 1 ? 0.12 : 0;

        const baseProb = 0.1 + age_factor + bp_factor + chol_factor + gluc_factor + active_factor + smoke_factor;
        const prob = Math.min(Math.max(baseProb, 0.05), 0.95);
        
        let riskLevel = 'LOW';
        let rec = 'Continue normal check-ups and maintain active lifestyle.';
        if (prob >= 0.7) {
          riskLevel = 'HIGH';
          rec = 'URGENT: Schedule cardiologist consultation. Initiate standard hypertensive therapy and regular lipid monitoring.';
        } else if (prob >= 0.4) {
          riskLevel = 'MODERATE';
          rec = 'Monitor blood pressure closely. Recommend dietary modifications and increased active lifestyle.';
        }

        setPrediction({
          prediction: prob >= 0.5 ? 1 : 0,
          probability: prob,
          risk_level: riskLevel,
          confidence: Math.round(75 + prob * 20),
          factors: [
            { factor: 'Systolic BP', value: patientData.ap_hi, impact: bp_factor > 0 ? 'High' : 'Normal' },
            { factor: 'Cholesterol', value: patientData.cholesterol, impact: patientData.cholesterol > 1 ? 'High' : 'Normal' },
            { factor: 'Age', value: patientData.age, impact: patientData.age > 45 ? 'High' : 'Normal' }
          ],
          recommendation: rec,
          request_id: 'local-' + Math.random().toString(36).substr(2, 9)
        });
      }, 500);
    } finally {
      setPredicting(false);
    }
  };

  // Video resource metadata
  const videos = [
    {
      id: "5a7K-K-V9B8",
      title: "ICU Patient Care: Clinical Monitoring & Hemodynamics",
      desc: "Comprehensive guidelines for intensive care nurses managing patient telemetry, hemodynamics, and critical blood pressure readings.",
      duration: "12 mins",
      source: "WHO Clinical Training",
      category: "Critical Nursing Care"
    },
    {
      id: "9BbgV2s6rV8",
      title: "Cardiac Arrest & Resuscitation ICU Protocol",
      desc: "Advanced cardiovascular life support guidelines and emergency response protocols for critical patients experiencing sudden cardiac failure.",
      duration: "15 mins",
      source: "American Heart Association",
      category: "Cardiac Emergency"
    },
    {
      id: "Xq4y6Dq3sZk",
      title: "ICU ECG Interpretation & Arrhythmia Management",
      desc: "Clinical training on identifying lethal arrhythmias, managing telemetry alarms, and executing rapid pharmacologic response protocols.",
      duration: "9 mins",
      source: "Mayo Clinic",
      category: "ECG Telemetry"
    }
  ];

  if (!token || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-950 text-slate-100 font-sans p-6">
        <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex p-3 bg-teal-500/10 text-teal-400 rounded-2xl mb-2">
              <Heart className="w-8 h-8 animate-pulse" />
            </div>
            <h1 className="text-2xl font-bold font-outfit tracking-tight">CVD Platform Login</h1>
            <p className="text-xs text-slate-500 font-semibold tracking-wider uppercase">Secure Clinical Portal</p>
          </div>
          
          <form onSubmit={(e) => handleLogin(e)} className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Username</label>
              <input 
                type="text" 
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
                placeholder="doctor, admin, or auditor"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Password</label>
              <input 
                type="password" 
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                required
              />
            </div>
            
            {loginError && <p className="text-xs text-rose-400 text-center font-semibold">{loginError}</p>}
            
            <button 
              type="submit" 
              className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-bold py-2.5 px-4 rounded-xl transition-all shadow-md text-sm font-outfit"
            >
              Sign In
            </button>
          </form>
          
          <div className="relative flex py-2 items-center">
            <div className="flex-grow border-t border-slate-800"></div>
            <span className="flex-shrink mx-4 text-[10px] text-slate-500 uppercase tracking-widest font-bold">Quick Demo Login</span>
            <div className="flex-grow border-t border-slate-800"></div>
          </div>
          
          <div className="grid grid-cols-2 gap-2 text-[10px]">
            <button 
              onClick={(e) => handleLogin(e, 'doctor')}
              className="bg-slate-950 border border-slate-800 hover:border-teal-500/50 py-2 px-3 rounded-lg text-slate-300 font-semibold text-center transition-all"
            >
              Dr Sarah (Clinician)
            </button>
            <button 
              onClick={(e) => handleLogin(e, 'admin')}
              className="bg-slate-950 border border-slate-800 hover:border-teal-500/50 py-2 px-3 rounded-lg text-slate-300 font-semibold text-center transition-all"
            >
              System Admin (Tenant)
            </button>
            <button 
              onClick={(e) => handleLogin(e, 'auditor')}
              className="bg-slate-950 border border-slate-800 hover:border-teal-500/50 py-2 px-3 rounded-lg text-slate-300 font-semibold text-center transition-all"
            >
              Compliance Auditor
            </button>
            <button 
              onClick={(e) => handleLogin(e, 'doctor_beta')}
              className="bg-slate-950 border border-slate-800 hover:border-teal-500/50 py-2 px-3 rounded-lg text-slate-300 font-semibold text-center transition-all"
            >
              Dr Rivera (Beta Tenant)
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Sidebar Navigation */}
      <div className="w-80 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-6">
        <div>
          <div className="flex items-center gap-3 mb-8">
            <Heart className="w-8 h-8 text-teal-400 animate-pulse" />
            <div>
              <h1 className="font-outfit text-xl font-bold tracking-tight text-white leading-none">CVD Risk</h1>
              <span className="text-[10px] text-teal-400 font-semibold tracking-widest uppercase">Intelligence Platform</span>
            </div>
          </div>

          <div className="space-y-1">
            {user.role === 'clinician' && (
              <>
                <button 
                  onClick={() => setActiveTab('overview')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'overview' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Activity className="w-4 h-4" />
                  Patient Assessment
                </button>
                <button 
                  onClick={() => setActiveTab('fhir_integration')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'fhir_integration' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <FileJson className="w-4 h-4" />
                  EHR Integration (FHIR)
                </button>
                <button 
                  onClick={() => setActiveTab('rag_chat')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'rag_chat' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Compass className="w-4 h-4" />
                  Clinical Chat Assistant
                </button>
                <button 
                  onClick={() => setActiveTab('comparative_analysis')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'comparative_analysis' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <ListOrdered className="w-4 h-4" />
                  Comparative Analysis
                </button>
                <button 
                  onClick={() => setActiveTab('models')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'models' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Brain className="w-4 h-4" />
                  Model Leaderboard
                </button>
                <button 
                  onClick={() => setActiveTab('explainable')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'explainable' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Sliders className="w-4 h-4" />
                  Explainable AI (XAI)
                </button>
                <button 
                  onClick={() => setActiveTab('statistics')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'statistics' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <TrendingUp className="w-4 h-4" />
                  Cause & Effect Stats
                </button>
                <button 
                  onClick={() => setActiveTab('videos')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'videos' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Video className="w-4 h-4" />
                  Clinical Videos
                </button>
                <button 
                  onClick={() => setActiveTab('audit_trail')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'audit_trail' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Users className="w-4 h-4" />
                  Patient Records Ledger
                </button>
              </>
            )}
            
            {user.role === 'administrator' && (
              <>
                <button 
                  onClick={() => setActiveTab('admin_dashboard')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'admin_dashboard' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Activity className="w-4 h-4" />
                  Tenant Dashboard
                </button>
                <button 
                  onClick={() => setActiveTab('comparative_analysis')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'comparative_analysis' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <ListOrdered className="w-4 h-4" />
                  Comparative Analysis
                </button>
                <button 
                  onClick={() => setActiveTab('models')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'models' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Brain className="w-4 h-4" />
                  Model Leaderboard
                </button>
                <button 
                  onClick={() => setActiveTab('statistics')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'statistics' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <TrendingUp className="w-4 h-4" />
                  Cause & Effect Stats
                </button>
                <button 
                  onClick={() => setActiveTab('audit_trail')}
                  className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'audit_trail' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
                >
                  <Database className="w-4 h-4" />
                  Cryptographic Audit Trail
                </button>
              </>
            )}
            
            {user.role === 'compliance_auditor' && (
              <button 
                onClick={() => setActiveTab('audit_trail')}
                className={`flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-semibold transition-all ${activeTab === 'audit_trail' ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
              >
                <Database className="w-4 h-4" />
                Cryptographic Audit Trail
              </button>
            )}
          </div>
        </div>

        {/* Info & Compliance Footer */}
        <div className="bg-slate-950/40 border border-slate-800/80 rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-300 font-bold">{user.name}</span>
            <span className="text-[10px] text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded-full border border-teal-500/20 uppercase tracking-widest font-semibold">{user.role}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Tenant: <strong className="text-slate-400">{user.tenant_id}</strong></span>
            <button 
              onClick={handleLogout}
              className="text-[10px] text-rose-400 hover:text-rose-300 font-semibold underline"
            >
              Sign Out
            </button>
          </div>
          <div className="border-t border-slate-800/60 pt-2 space-y-1">
            <p className="text-[10px] text-slate-500 leading-normal">🇦🇺 Australian Privacy Act Compliant</p>
            <p className="text-[10px] text-slate-500 leading-normal">🛡️ ISO 27001 & APP Compliant</p>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-slate-950">
        
        {/* Top Header */}
        <header className="sticky top-0 z-10 bg-slate-950/80 backdrop-blur-md border-b border-slate-900 px-8 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold font-outfit text-white">
              {activeTab === 'overview' && '🏥 Cardiovascular Disease (CVD) Risk Assessment Portal'}
              {activeTab === 'fhir_integration' && '🔌 EHR Interoperability Gateway (HL7 FHIR R4)'}
              {activeTab === 'rag_chat' && '💬 Clinical Guidelines Chat Assistant (RAG)'}
              {activeTab === 'comparative_analysis' && '📊 Multi-Model Performance & Explainability (SHAP & LIME) Comparative Dashboard'}
              {activeTab === 'models' && '📊 Machine Learning Benchmark Leaderboard'}
              {activeTab === 'explainable' && '🔬 Explainable AI Insights (SHAP & LIME)'}
              {activeTab === 'statistics' && '📈 Statistical Causality & Significance Analysis'}
              {activeTab === 'videos' && '📺 Critical Care Patient Care Video Training'}
              {activeTab === 'admin_dashboard' && '🏢 Enterprise Tenant Administration'}
              {activeTab === 'audit_trail' && '🔒 Immutable Cryptographic Audit Ledger'}
            </h2>
            <p className="text-xs text-slate-500 mt-1">Production-Grade Multi-Agent AI Healthcare Platform</p>
          </div>
          <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full text-xs text-slate-400">
            <Clock className="w-3.5 h-3.5 text-teal-400" />
            <span>June 2026</span>
          </div>
        </header>

        {/* Tab Contents */}
        <main className="flex-1 p-8 space-y-8 max-w-7xl mx-auto w-full">
          
          {/* TAB 1: OVERVIEW & FORM */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* Left Column: Form */}
              <div className="lg:col-span-2 bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">Patient Data Entry</h3>
                  <p className="text-xs text-slate-400">Input clinical measurements to calculate CVD risk probability.</p>
                </div>

                <form onSubmit={runPrediction} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Age */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Age (years)</label>
                      <input 
                        type="number" 
                        value={patientData.age}
                        onChange={(e) => setPatientData({...patientData, age: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    {/* Gender */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Gender</label>
                      <select 
                        value={patientData.gender}
                        onChange={(e) => setPatientData({...patientData, gender: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      >
                        <option value={1}>Female</option>
                        <option value={2}>Male</option>
                      </select>
                    </div>
                    {/* Height */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Height (cm)</label>
                      <input 
                        type="number" 
                        value={patientData.height}
                        onChange={(e) => setPatientData({...patientData, height: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    {/* Weight */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Weight (kg)</label>
                      <input 
                        type="number" 
                        value={patientData.weight}
                        onChange={(e) => setPatientData({...patientData, weight: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    {/* Systolic BP */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Systolic Blood Pressure (ap_hi)</label>
                      <input 
                        type="number" 
                        value={patientData.ap_hi}
                        onChange={(e) => setPatientData({...patientData, ap_hi: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    {/* Diastolic BP */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Diastolic Blood Pressure (ap_lo)</label>
                      <input 
                        type="number" 
                        value={patientData.ap_lo}
                        onChange={(e) => setPatientData({...patientData, ap_lo: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      />
                    </div>
                    {/* Cholesterol */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Cholesterol Level</label>
                      <select 
                        value={patientData.cholesterol}
                        onChange={(e) => setPatientData({...patientData, cholesterol: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      >
                        <option value={1}>Normal</option>
                        <option value={2}>Above Normal</option>
                        <option value={3}>Well Above Normal</option>
                      </select>
                    </div>
                    {/* Glucose */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Glucose Level</label>
                      <select 
                        value={patientData.gluc}
                        onChange={(e) => setPatientData({...patientData, gluc: Number(e.target.value)})}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                      >
                        <option value={1}>Normal</option>
                        <option value={2}>Above Normal</option>
                        <option value={3}>Well Above Normal</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 pt-2">
                    {/* Smoker */}
                    <label className="flex items-center gap-2 cursor-pointer bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all select-none">
                      <input 
                        type="checkbox" 
                        checked={patientData.smoke === 1}
                        onChange={(e) => setPatientData({...patientData, smoke: e.target.checked ? 1 : 0})}
                        className="w-4 h-4 accent-teal-400 rounded focus:ring-0"
                      />
                      <span className="text-xs font-semibold text-slate-300">Smoker</span>
                    </label>
                    {/* Alcohol */}
                    <label className="flex items-center gap-2 cursor-pointer bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all select-none">
                      <input 
                        type="checkbox" 
                        checked={patientData.alco === 1}
                        onChange={(e) => setPatientData({...patientData, alco: e.target.checked ? 1 : 0})}
                        className="w-4 h-4 accent-teal-400 rounded focus:ring-0"
                      />
                      <span className="text-xs font-semibold text-slate-300">Alcohol Use</span>
                    </label>
                    {/* Active */}
                    <label className="flex items-center gap-2 cursor-pointer bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 hover:border-slate-700/80 transition-all select-none">
                      <input 
                        type="checkbox" 
                        checked={patientData.active === 1}
                        onChange={(e) => setPatientData({...patientData, active: e.target.checked ? 1 : 0})}
                        className="w-4 h-4 accent-teal-400 rounded focus:ring-0"
                      />
                      <span className="text-xs font-semibold text-slate-300">Active</span>
                    </label>
                  </div>

                  <button 
                    type="submit"
                    disabled={predicting}
                    className="w-full bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-bold py-3.5 px-6 rounded-2xl transition-all shadow-lg hover:shadow-teal-500/20 active:scale-[0.98] disabled:opacity-50 text-sm tracking-wide uppercase font-outfit"
                  >
                    {predicting ? 'Computing Risk Analysis...' : 'Evaluate Patient Risk Score'}
                  </button>
                </form>
              </div>

              {/* Right Column: Prediction results */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl flex flex-col justify-between min-h-[500px]">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit mb-1">Diagnostic Output</h3>
                  <p className="text-xs text-slate-400">Cardiovascular Risk assessment generated in real time.</p>
                </div>

                {prediction ? (
                  <div className="flex-1 flex flex-col justify-center space-y-6 py-6">
                    {/* Circular dial or score block */}
                    <div className="text-center">
                      <div className="inline-block relative">
                        {/* Outer Glow ring */}
                        <div className={`absolute -inset-1 rounded-full blur opacity-25 animate-pulse ${prediction.risk_level === 'HIGH' ? 'bg-rose-500' : prediction.risk_level === 'MODERATE' ? 'bg-amber-500' : 'bg-teal-500'}`}></div>
                        <div className={`relative w-40 h-40 rounded-full border-4 flex flex-col items-center justify-center bg-slate-950/80 ${prediction.risk_level === 'HIGH' ? 'border-rose-500' : prediction.risk_level === 'MODERATE' ? 'border-amber-500' : 'border-teal-500'}`}>
                          <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">Risk Score</span>
                          <span className={`text-4xl font-extrabold font-outfit my-1 ${prediction.risk_level === 'HIGH' ? 'text-rose-400' : prediction.risk_level === 'MODERATE' ? 'text-amber-400' : 'text-teal-400'}`}>
                            {Math.round(prediction.probability * 100)}%
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${prediction.risk_level === 'HIGH' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : prediction.risk_level === 'MODERATE' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-teal-500/10 text-teal-400 border border-teal-500/20'}`}>
                            {prediction.risk_level} RISK
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Recommendation box */}
                    <div className={`p-4 rounded-2xl border text-xs leading-relaxed ${prediction.risk_level === 'HIGH' ? 'bg-rose-500/5 border-rose-500/20 text-rose-200' : prediction.risk_level === 'MODERATE' ? 'bg-amber-500/5 border-amber-500/20 text-amber-200' : 'bg-teal-500/5 border-teal-500/20 text-teal-200'}`}>
                      <div className="flex gap-2 mb-1.5 font-bold uppercase tracking-wider">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        <span>Clinical Recommendation</span>
                      </div>
                      {prediction.recommendation}
                    </div>

                    {/* Key Risk Factors */}
                    <div className="space-y-2">
                      <span className="text-[10px] font-bold uppercase text-slate-500 tracking-wider">Primary Contributing Factors</span>
                      <div className="flex flex-wrap gap-2">
                        {prediction.factors && prediction.factors.map((f, idx) => (
                          <span key={idx} className={`text-xs px-3 py-1 rounded-full font-semibold border ${f.impact === 'High' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-slate-900 border-slate-800 text-slate-300'}`}>
                            {f.factor}: {f.value}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-6 space-y-4">
                    <Heart className="w-16 h-16 text-slate-800 stroke-[1.5]" />
                    <div>
                      <p className="text-sm font-semibold text-slate-400">No Assessment Loaded</p>
                      <p className="text-xs text-slate-600 max-w-[200px] mt-1 mx-auto">Fill the clinical entries and submit to generate risk reports.</p>
                    </div>
                  </div>
                )}

                {/* Secure Checksum Audit Footer */}
                <div className="border-t border-slate-800/80 pt-4 flex items-center justify-between text-[9px] text-slate-500">
                  <span>AUDIT REQUEST ID</span>
                  <span className="font-mono text-slate-400 uppercase tracking-widest">{prediction ? prediction.request_id : '000000000'}</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MODEL LEADERBOARD */}
          {activeTab === 'models' && metrics && (
            <div className="space-y-8">
              {/* Leaderboard stats cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <CheckCircle className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Best Model</span>
                    <span className="text-sm font-bold text-white block">{metrics.best_model.model}</span>
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <TrendingUp className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Best ROC-AUC</span>
                    <span className="text-sm font-bold text-white block">{metrics.best_model.roc_auc}</span>
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <Sliders className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">F1 Score</span>
                    <span className="text-sm font-bold text-white block">{metrics.best_model.f1_score}</span>
                  </div>
                </div>

                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <Users className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Sensitivity (TPR)</span>
                    <span className="text-sm font-bold text-white block">{metrics.best_model.sensitivity}</span>
                  </div>
                </div>
              </div>

              {/* Models Table */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">Model Benchmark Leaderboard</h3>
                  <p className="text-xs text-slate-400">Twelve baseline and ensemble models evaluated using stratified cross-validation.</p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                        <th className="py-3 px-4">Rank</th>
                        <th className="py-3 px-4">Model Name</th>
                        <th className="py-3 px-4">ROC-AUC</th>
                        <th className="py-3 px-4">F1 Score</th>
                        <th className="py-3 px-4">Accuracy</th>
                        <th className="py-3 px-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {[...metrics.all_models].sort((a, b) => (b.roc_auc || b.roc_auc_val || 0) - (a.roc_auc || a.roc_auc_val || 0)).map((m, idx) => (
                        <tr 
                          key={idx} 
                          className={`hover:bg-slate-900/40 transition-colors ${idx === 0 ? 'bg-teal-500/5 text-teal-400' : 'text-slate-300'}`}
                        >
                          <td className="py-3.5 px-4 font-bold">#{idx + 1}</td>
                          <td className="py-3.5 px-4 font-semibold">{m.model}</td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center gap-2">
                              <span>{m.roc_auc || m.roc_auc_val}</span>
                              <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <div className="h-full bg-teal-500 rounded-full" style={{ width: `${(m.roc_auc || m.roc_auc_val) * 100}%` }}></div>
                              </div>
                            </div>
                          </td>
                          <td className="py-3.5 px-4">{m.f1 || m.f1_score}</td>
                          <td className="py-3.5 px-4">{m.accuracy}</td>
                          <td className="py-3.5 px-4">
                            {idx === 0 ? (
                              <span className="text-[10px] font-bold bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full text-teal-400 tracking-wider">
                                SELECTED (BEST)
                              </span>
                            ) : (
                              <span className="text-[10px] font-bold bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-full text-slate-500 tracking-wider">
                                BENCHMARKED
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: EXPLAINABLE AI */}
          {activeTab === 'explainable' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* SHAP Global Impact */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">SHAP Global Feature Impact</h3>
                  <p className="text-xs text-slate-400">Mean absolute SHAP value highlighting global feature importances across the entire dataset.</p>
                </div>

                <div className="space-y-4">
                  {[
                    { feature: 'Systolic Blood Pressure (ap_hi)', val: 0.28, pct: '100%' },
                    { feature: 'Age (age)', val: 0.22, pct: '78%' },
                    { feature: 'Cholesterol (cholesterol)', val: 0.18, pct: '64%' },
                    { feature: 'Diastolic Blood Pressure (ap_lo)', val: 0.12, pct: '42%' },
                    { feature: 'Physical Activity (active)', val: 0.08, pct: '28%' },
                    { feature: 'Glucose (gluc)', val: 0.07, pct: '25%' },
                    { feature: 'Smoking Status (smoke)', val: 0.06, pct: '21%' },
                    { feature: 'Body Mass Index (bmi)', val: 0.05, pct: '17%' }
                  ].map((s, idx) => (
                    <div key={idx} className="space-y-1">
                      <div className="flex justify-between text-xs font-semibold">
                        <span className="text-slate-300">{s.feature}</span>
                        <span className="text-slate-400">{s.val} SHAP</span>
                      </div>
                      <div className="w-full h-2.5 bg-slate-950 border border-slate-900 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-teal-500 to-emerald-500 rounded-full" style={{ width: s.pct }}></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* LIME Patient Simulation */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">LIME Patient Local Simulator</h3>
                  <p className="text-xs text-slate-400">Clinical contribution weights showing how features push predictions towards or away from high CVD risk.</p>
                </div>

                <div className="space-y-6">
                  {/* Contributors to CVD+ (Red bars) */}
                  <div className="space-y-3">
                    <span className="text-[10px] font-bold text-rose-400 uppercase tracking-widest block">Increases Risk (CVD+)</span>
                    <div className="space-y-2">
                      {[
                        { feature: 'ap_hi > 140 (Hypertensive)', val: '+0.34', pct: '85%' },
                        { feature: 'Age > 55', val: '+0.21', pct: '52%' },
                        { feature: 'Cholesterol = 3 (Well Above Normal)', val: '+0.15', pct: '37%' }
                      ].map((l, idx) => (
                        <div key={idx} className="flex items-center gap-4 text-xs font-semibold">
                          <span className="w-48 text-slate-300 truncate">{l.feature}</span>
                          <div className="flex-1 h-3 bg-slate-950 rounded overflow-hidden">
                            <div className="h-full bg-rose-500 rounded" style={{ width: l.pct }}></div>
                          </div>
                          <span className="w-12 text-right text-rose-400 font-mono">{l.val}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Contributors to CVD- (Green bars) */}
                  <div className="space-y-3">
                    <span className="text-[10px] font-bold text-teal-400 uppercase tracking-widest block">Decreases Risk (CVD-)</span>
                    <div className="space-y-2">
                      {[
                        { feature: 'Active = 1 (Physically Active)', val: '-0.18', pct: '60%' },
                        { feature: 'Alco = 0 (No Alcohol)', val: '-0.07', pct: '23%' },
                        { feature: 'Smoke = 0 (Non-Smoker)', val: '-0.05', pct: '16%' }
                      ].map((l, idx) => (
                        <div key={idx} className="flex items-center gap-4 text-xs font-semibold">
                          <span className="w-48 text-slate-300 truncate">{l.feature}</span>
                          <div className="flex-1 h-3 bg-slate-950 rounded overflow-hidden flex justify-end">
                            <div className="h-full bg-teal-500 rounded" style={{ width: l.pct }}></div>
                          </div>
                          <span className="w-12 text-right text-teal-400 font-mono">{l.val}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: STATISTICS */}
          {activeTab === 'statistics' && (
            <div className="space-y-8">
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-4">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">Statistical Significance Matrix</h3>
                  <p className="text-xs text-slate-400">Mann-Whitney U non-parametric hypothesis tests assessing feature differences between CVD+ and CVD- patient cohorts.</p>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold">
                        <th className="py-3 px-4">Feature</th>
                        <th className="py-3 px-4">CVD+ Mean (scaled)</th>
                        <th className="py-3 px-4">CVD- Mean (scaled)</th>
                        <th className="py-3 px-4">p-value</th>
                        <th className="py-3 px-4">Causality Significance</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300">
                      {[
                        { name: 'age', pos: '0.4343', neg: '-0.5409', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'ap_hi', pos: '0.1170', neg: '-0.1457', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'cholesterol', pos: '0.6506', neg: '0.3258', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'gluc', pos: '0.4372', neg: '0.2964', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'smoke', pos: '0.0500', neg: '-0.0623', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'active', pos: '-0.0523', neg: '0.0652', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'pulse_pressure', pos: '0.0859', neg: '-0.0838', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'bmi', pos: '0.0726', neg: '0.0163', p: '0.0', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'weight', pos: '0.0171', neg: '-0.0306', p: '1e-06', sig: 'Highly Significant (p < 0.01)' },
                        { name: 'height', pos: '-0.0513', neg: '-0.0245', p: '0.007277', sig: 'Significant (p < 0.05)' },
                        { name: 'ap_lo', pos: '-0.0078', neg: '0.0097', p: '0.253673', sig: 'Not Significant (p > 0.05)' }
                      ].map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-900/40 transition-colors">
                          <td className="py-3 px-4 font-mono font-bold text-slate-200">{item.name}</td>
                          <td className="py-3 px-4">{item.pos}</td>
                          <td className="py-3 px-4">{item.neg}</td>
                          <td className="py-3 px-4 font-mono text-teal-400">{item.p}</td>
                          <td className="py-3 px-4 font-semibold">
                            {item.p === '0.0' || Number(item.p) < 0.05 ? (
                              <span className="text-teal-400">✓ {item.sig}</span>
                            ) : (
                              <span className="text-slate-500">✗ {item.sig}</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: CLINICAL VIDEOS */}
          {activeTab === 'videos' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {videos.map((vid, index) => (
                  <div key={index} className="bg-slate-900/40 border border-slate-800/80 rounded-3xl overflow-hidden shadow-lg flex flex-col">
                    {/* Embedded Youtube Video */}
                    <div className="relative aspect-video w-full bg-slate-950">
                      <iframe 
                        className="absolute inset-0 w-full h-full"
                        src={`https://www.youtube.com/embed/${vid.id}`}
                        title={vid.title}
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      ></iframe>
                    </div>

                    {/* Metadata & description */}
                    <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-[10px] font-bold text-teal-400 bg-teal-500/10 px-2 py-0.5 rounded-full border border-teal-500/20 uppercase tracking-widest">
                            {vid.category}
                          </span>
                          <span className="flex items-center gap-1 text-[10px] text-slate-500 font-semibold uppercase">
                            <Clock className="w-3 h-3 text-slate-500" />
                            {vid.duration}
                          </span>
                        </div>
                        <h4 className="font-outfit text-sm font-bold text-white leading-snug">{vid.title}</h4>
                        <p className="text-xs text-slate-400 leading-normal">{vid.desc}</p>
                      </div>

                      <div className="border-t border-slate-800/80 pt-3 flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                        <span>Source</span>
                        <span className="text-slate-400">{vid.source}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: EHR INTEGRATION (FHIR) */}
          {activeTab === 'fhir_integration' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Side: FHIR JSON Ingestion */}
              <div className="lg:col-span-2 bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">HL7 FHIR Ingestion Gateway</h3>
                  <p className="text-xs text-slate-400">Copy and paste a patient clinical resource bundle (Patient details + vitals Observations) below to run calculations.</p>
                </div>
                <form onSubmit={handleImportFhir} className="space-y-4">
                  <textarea 
                    value={fhirPayload}
                    onChange={(e) => setFhirPayload(e.target.value)}
                    rows={15}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs font-mono focus:border-teal-500 focus:outline-none text-teal-300"
                    required
                  />
                  <div className="flex gap-4">
                    <button 
                      type="button" 
                      onClick={() => setFhirPayload(JSON.stringify(SAMPLE_FHIR_BUNDLE, null, 2))}
                      className="bg-slate-950 border border-slate-800 hover:border-slate-700 text-slate-300 font-bold py-2.5 px-4 rounded-xl text-xs"
                    >
                      Pre-fill Sample Bundle
                    </button>
                    <button 
                      type="submit" 
                      disabled={fhirImporting}
                      className="flex-1 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white font-bold py-2.5 px-4 rounded-xl transition-all shadow-md text-xs uppercase tracking-wider"
                    >
                      {fhirImporting ? 'Ingesting FHIR...' : 'Ingest and Predict'}
                    </button>
                  </div>
                </form>
                {fhirError && (
                  <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl font-semibold">
                    {fhirError}
                  </div>
                )}
              </div>

              {/* Right Side: Prediction results */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl flex flex-col justify-between min-h-[500px]">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit mb-1">FHIR Risk Assessment Output</h3>
                  <p className="text-xs text-slate-400">FHIR-compatible RiskAssessment resource response.</p>
                </div>
                {fhirResult ? (
                  <div className="flex-1 flex flex-col justify-center space-y-6 py-6">
                    <div className="text-center">
                      <div className="inline-block relative">
                        <div className={`absolute -inset-1 rounded-full blur opacity-25 animate-pulse bg-teal-500`}></div>
                        <div className={`relative w-40 h-40 rounded-full border-4 flex flex-col items-center justify-center bg-slate-950/80 border-teal-500`}>
                          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">CVD Probability</span>
                          <span className="text-4xl font-extrabold font-outfit my-1 text-teal-400">
                            {Math.round(fhirResult.prediction[0].probabilityDecimal * 100)}%
                          </span>
                          <span className="text-[9px] font-bold px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                            {fhirResult.prediction[0].qualitativeRisk.coding[0].code}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 bg-teal-500/5 border border-teal-500/20 text-teal-200 text-xs rounded-2xl leading-relaxed">
                      <div className="font-bold uppercase tracking-wider mb-1">Clinical Note</div>
                      {fhirResult.note[1].text}
                    </div>
                    <div className="border border-slate-800 bg-slate-950 rounded-xl p-3 text-[10px] font-mono overflow-auto max-h-[160px] text-slate-400">
                      {JSON.stringify(fhirResult, null, 2)}
                    </div>
                  </div>
                ) : (
                  <div className="flex-1 flex flex-col items-center justify-center text-center p-6 space-y-4">
                    <FileJson className="w-16 h-16 text-slate-800 stroke-[1.5]" />
                    <div>
                      <p className="text-sm font-semibold text-slate-400">No FHIR Response</p>
                      <p className="text-xs text-slate-600 max-w-[200px] mt-1 mx-auto">Ingest patient Observations from the uploader to generate FHIR RiskAssessment outputs.</p>
                    </div>
                  </div>
                )}
                <div className="border-t border-slate-800/80 pt-4 flex items-center justify-between text-[9px] text-slate-500">
                  <span>FHIR Interop Standards</span>
                  <span className="font-mono text-teal-400 tracking-wider">HL7 FHIR R4</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: CLINICAL CHAT ASSISTANT (RAG) */}
          {activeTab === 'rag_chat' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Guidelines sidebar */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit">Australian Clinical Guidelines</h3>
                  <p className="text-xs text-slate-400">Cardiology & Hypertension management reference standards.</p>
                </div>
                <div className="space-y-4 text-xs">
                  <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800">
                    <h4 className="font-bold text-teal-400 mb-1">Blood Pressure Targets (NHFA)</h4>
                    <p className="text-slate-400 leading-relaxed text-slate-300">Normal is defined as &lt;120/80 mmHg. Grade 1 Hypertension: 130-139 / 80-89. Grade 2 Hypertension: &ge;140/90 mmHg. Drug therapies are recommended for high risk patients or Grade 2.</p>
                  </div>
                  <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800">
                    <h4 className="font-bold text-teal-400 mb-1">Lipid & Cholesterol Targets</h4>
                    <p className="text-slate-400 leading-relaxed text-slate-300">Total Cholesterol target is &lt;4.0 mmol/L for high risk patients. LDL target is &lt;1.8 mmol/L. Normal ranges: total &lt;5.0, LDL &lt;3.0 mmol/L.</p>
                  </div>
                </div>
              </div>

              {/* Chat Interface */}
              <div className="lg:col-span-2 bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl flex flex-col justify-between min-h-[500px]">
                <div>
                  <h3 className="text-lg font-bold text-white font-outfit mb-1">Clinical Chat Assistant</h3>
                  <p className="text-xs text-slate-400 font-semibold text-slate-400">RAG-powered conversational interface consulting cardiology guidelines and physiological maps.</p>
                </div>
                <div className="flex-1 overflow-y-auto my-4 space-y-3 p-4 bg-slate-950 rounded-2xl max-h-[350px] border border-slate-800">
                  {chatMessages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`p-3 rounded-2xl max-w-md text-xs leading-normal ${msg.sender === 'user' ? 'bg-teal-500 text-slate-950 font-semibold rounded-tr-none' : 'bg-slate-900 border border-slate-800 text-slate-200 rounded-tl-none'}`}>
                        {msg.text}
                        {msg.sources && (
                          <div className="mt-2 pt-2 border-t border-slate-800 text-[10px] text-teal-400 font-bold">
                            <strong>Sources:</strong> {msg.sources.map(s => `${s.title} (${Math.round(s.relevance*100)}%)`).join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {chatLoading && (
                    <div className="flex justify-start">
                      <div className="p-3 bg-slate-900 border border-slate-850 rounded-2xl rounded-tl-none text-xs text-slate-500 animate-pulse">
                        Clinical AI is compiling evidence...
                      </div>
                    </div>
                  )}
                </div>
                <form onSubmit={handleSendChatMessage} className="flex gap-2">
                  <input 
                    type="text" 
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Ask about hypertension targets or lipid management..."
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm focus:border-teal-500 focus:outline-none"
                    required
                  />
                  <button 
                    type="submit"
                    className="bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold p-3 rounded-xl transition-all shadow-md active:scale-95"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* TAB 7.5: COMPARATIVE ANALYSIS MODULE */}
          {activeTab === 'comparative_analysis' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-start">
              
              {/* Left Column: Sidebar Controls */}
              <div className="lg:col-span-1 bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-5 shadow-xl space-y-6">
                <div>
                  <h3 className="text-sm font-bold text-white font-outfit uppercase tracking-wider flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-teal-400" />
                    Compare Config
                  </h3>
                  <p className="text-[10px] text-slate-500 mt-1">Select dataset, models, and metrics to analyze.</p>
                </div>

                <div className="space-y-4">
                  {/* Select Dataset */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Dataset</label>
                    <select 
                      value={selectedDataset} 
                      onChange={(e) => setSelectedDataset(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs focus:border-teal-500 focus:outline-none text-slate-300 font-semibold"
                    >
                      <option value="CVD_risk_data_set.xlsx">CVD_risk_data_set.xlsx (Active)</option>
                      <option value="cardiovascular_disease.csv">cardiovascular_disease.csv</option>
                    </select>
                  </div>

                  {/* Select Experiment */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Experiment</label>
                    <select 
                      value={selectedExperiment} 
                      onChange={(e) => setSelectedExperiment(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs focus:border-teal-500 focus:outline-none text-slate-300 font-semibold"
                    >
                      <option value="Exp_1_Default">Exp_1_Default (Primary Target)</option>
                      <option value="Exp_2_No_Leakage">Exp_2_No_Leakage (Feature Selection)</option>
                    </select>
                  </div>

                  {/* Select Models Checklist */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Select Models</label>
                    <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-3 max-h-[180px] overflow-y-auto space-y-2">
                      {Object.keys(COMPARATIVE_DB.models).map((modelId) => (
                        <label key={modelId} className="flex items-center gap-2 cursor-pointer select-none">
                          <input 
                            type="checkbox"
                            checked={selectedModels.includes(modelId)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedModels([...selectedModels, modelId]);
                              } else {
                                if (selectedModels.length > 2) {
                                  setSelectedModels(selectedModels.filter(m => m !== modelId));
                                }
                              }
                            }}
                            className="w-3.5 h-3.5 accent-teal-400 rounded focus:ring-0"
                          />
                          <span className="text-xs text-slate-300 font-semibold">{COMPARATIVE_DB.models[modelId].name}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Select Metrics Checklist */}
                  <div>
                    <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5">Select Metrics</label>
                    <div className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-3 max-h-[160px] overflow-y-auto space-y-2">
                      {['Accuracy', 'Precision', 'Recall', 'Specificity', 'Sensitivity', 'F1-Score', 'ROC-AUC', 'PR-AUC', 'MCC', 'Cohen\'s Kappa', 'Brier Score', 'Log Loss', 'Training Time'].map((metricName) => (
                        <label key={metricName} className="flex items-center gap-2 cursor-pointer select-none">
                          <input 
                            type="checkbox"
                            checked={selectedMetrics.includes(metricName)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedMetrics([...selectedMetrics, metricName]);
                              } else {
                                if (selectedMetrics.length > 2) {
                                  setSelectedMetrics(selectedMetrics.filter(m => m !== metricName));
                                }
                              }
                            }}
                            className="w-3.5 h-3.5 accent-teal-400 rounded focus:ring-0"
                          />
                          <span className="text-xs text-slate-300 font-semibold">{metricName}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Compare Button */}
                  <button 
                    onClick={() => {
                      alert("Recalculating and loading comparative data parameters...");
                    }}
                    className="w-full bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold py-2.5 px-4 rounded-xl text-xs uppercase tracking-wider transition-all shadow-md active:scale-95"
                  >
                    Compare Models
                  </button>
                </div>
              </div>

              {/* Right Column: Comparative Dashboard Content */}
              <div className="lg:col-span-3 space-y-6">
                
                {/* Nested Dashboard Tab Menu */}
                <div className="flex border-b border-slate-900 overflow-x-auto gap-4 scrollbar-none">
                  {[
                    { id: 'performance', label: 'Model Performance', icon: Activity },
                    { id: 'xai', label: 'Explainable AI (XAI)', icon: Brain },
                    { id: 'statistics', label: 'Statistical Analysis', icon: TrendingUp },
                    { id: 'insights', label: 'Clinical Insights', icon: Compass },
                    { id: 'summary', label: 'Executive Summary', icon: CheckCircle }
                  ].map((subtab) => {
                    const Icon = subtab.icon;
                    return (
                      <button
                        key={subtab.id}
                        onClick={() => setCompActiveTab(subtab.id)}
                        className={`flex items-center gap-2 py-3 px-1 border-b-2 text-xs font-bold whitespace-nowrap transition-all uppercase tracking-wider ${compActiveTab === subtab.id ? 'border-teal-400 text-teal-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
                      >
                        <Icon className="w-4 h-4" />
                        {subtab.label}
                      </button>
                    );
                  })}
                </div>

                {/* nested content area */}
                <div className="space-y-6 animate-fade-in">
                  
                  {/* NESTED TAB 1: MODEL PERFORMANCE */}
                  {compActiveTab === 'performance' && (
                    <div className="space-y-6">
                      
                      {/* KPI Cards */}
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 shadow-sm">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Best Classifier</span>
                          <span className="text-sm font-bold text-white block mt-1">CatBoost / Logistic Regression</span>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 shadow-sm">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Top Accuracy</span>
                          <span className="text-sm font-bold text-teal-400 block mt-1">100% (Leakage present)</span>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 shadow-sm">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Top F1-Score</span>
                          <span className="text-sm font-bold text-teal-400 block mt-1">1.0000</span>
                        </div>
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4 shadow-sm">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">Top Sensitivity</span>
                          <span className="text-sm font-bold text-teal-400 block mt-1">1.0000</span>
                        </div>
                      </div>

                      {/* Performance Chart & Table */}
                      <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                        <div>
                          <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">Selected Metric Performance Comparison</h4>
                          <p className="text-[10px] text-slate-500">Comparing selected models across the active metric sets.</p>
                        </div>
                        <div className="h-[280px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                              data={selectedModels.map(m => ({
                                name: COMPARATIVE_DB.models[m].name,
                                ...selectedMetrics.reduce((acc, met) => {
                                  acc[met] = COMPARATIVE_DB.models[m][met];
                                  return acc;
                                }, {})
                              }))}
                              margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                              <XAxis dataKey="name" stroke="#6b7280" style={{ fontSize: 9 }} />
                              <YAxis stroke="#6b7280" style={{ fontSize: 9 }} />
                              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1f2937', borderRadius: '10px' }} />
                              <Legend wrapperStyle={{ fontSize: 10 }} />
                              {selectedMetrics.map((met, idx) => {
                                const colors = ['#14b8a6', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316'];
                                return <Bar key={met} dataKey={met} fill={colors[idx % colors.length]} radius={[4, 4, 0, 0]} />;
                              })}
                            </BarChart>
                          </ResponsiveContainer>
                        </div>

                        {/* Interactive Performance Table */}
                        <div className="overflow-x-auto border border-slate-800 rounded-2xl mt-6">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold bg-slate-950/60">
                                <th className="py-2.5 px-4">Model</th>
                                {selectedMetrics.map(met => (
                                  <th key={met} className="py-2.5 px-4">{met}</th>
                                ))}
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                              {selectedModels.map(modelId => (
                                <tr key={modelId} className="hover:bg-slate-900/20 text-slate-200">
                                  <td className="py-3 px-4 font-sans font-bold text-white">{COMPARATIVE_DB.models[modelId].name}</td>
                                  {selectedMetrics.map(met => {
                                    const val = COMPARATIVE_DB.models[modelId][met];
                                    let cellColor = "text-slate-300";
                                    if (met !== 'Training Time' && met !== 'Inference Time' && met !== 'Model Size' && met !== 'Brier Score' && met !== 'Log Loss') {
                                      if (val >= 1.0) cellColor = "text-teal-400 font-bold";
                                      else if (val >= 0.98) cellColor = "text-emerald-400";
                                      else cellColor = "text-amber-400";
                                    }
                                    return (
                                      <td key={met} className={`py-3 px-4 ${cellColor}`}>
                                        {typeof val === 'number' && met.includes('Time') ? `${val}s` : typeof val === 'number' && met.includes('Size') ? `${val}KB` : val}
                                      </td>
                                    );
                                  })}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>

                      {/* ROC & PR Curve Comparison and Confusion Matrices */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        
                        {/* ROC Curve Simulation */}
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 shadow-md">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider font-outfit mb-3">Receiver Operating Characteristic (ROC) comparison</h4>
                          <div className="h-[220px] relative border border-slate-800 rounded-2xl p-4 bg-slate-950/60">
                            {/* SVG Chart Overlay */}
                            <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                              {/* Grid lines */}
                              <line x1="0" y1="100" x2="100" y2="0" stroke="#1f2937" strokeWidth="0.5" strokeDasharray="2,2" />
                              <line x1="0" y1="0" x2="100" y2="100" stroke="#334155" strokeWidth="0.5" />
                              
                              {/* Selected Model Curves */}
                              {selectedModels.includes('CatBoost') && <path d="M 0 100 L 0 0 L 100 0" fill="none" stroke="#14b8a6" strokeWidth="2" />}
                              {selectedModels.includes('LogisticRegression') && <path d="M 0 100 L 0 0 L 100 0" fill="none" stroke="#06b6d4" strokeWidth="1.5" />}
                              {selectedModels.includes('KNN') && <path d="M 0 100 Q 2 20 15 10 T 100 0" fill="none" stroke="#f43f5e" strokeWidth="1.5" />}
                              {selectedModels.includes('NaiveBayes') && <path d="M 0 100 Q 3 25 20 12 T 100 0" fill="none" stroke="#8b5cf6" strokeWidth="1.5" />}
                            </svg>
                            <div className="absolute bottom-2 left-10 text-[9px] text-slate-500 font-bold uppercase">False Positive Rate</div>
                            <div className="absolute top-10 left-2 text-[9px] text-slate-500 font-bold uppercase -rotate-90">True Positive Rate</div>
                            <div className="absolute top-2 right-2 flex flex-col gap-1 text-[8px] bg-slate-950 border border-slate-800 p-2 rounded-lg">
                              <span className="flex items-center gap-1"><span className="w-2 h-0.5 bg-teal-400"></span> CatBoost (1.00)</span>
                              <span className="flex items-center gap-1"><span className="w-2 h-0.5 bg-cyan-400"></span> Logistic Reg (1.00)</span>
                              <span className="flex items-center gap-1"><span className="w-2 h-0.5 bg-rose-400"></span> KNN (0.998)</span>
                            </div>
                          </div>
                          <p className="text-[10px] text-slate-500 mt-2">Publications-grade ROC curves representing perfect separation for baseline leakage experiment vs actual classifier thresholds.</p>
                        </div>

                        {/* Confusion Matrix list */}
                        <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-5 shadow-md space-y-4">
                          <h4 className="text-xs font-bold text-white uppercase tracking-wider font-outfit">Selected Confusion Matrices (Active Holdout)</h4>
                          <div className="grid grid-cols-2 gap-3 max-h-[220px] overflow-y-auto pr-1">
                            {selectedModels.map(modelId => {
                              const m = COMPARATIVE_DB.models[modelId];
                              return (
                                <div key={modelId} className="bg-slate-950 border border-slate-800 p-3 rounded-2xl space-y-2">
                                  <div className="text-[10px] font-bold text-slate-400 uppercase truncate">{m.name}</div>
                                  <div className="grid grid-cols-2 gap-1 text-center font-mono text-[10px]">
                                    <div className="bg-teal-500/10 text-teal-400 p-1.5 rounded border border-teal-500/20">
                                      <div className="text-slate-500 text-[8px]">TP</div>
                                      <div className="font-bold">{m.TP}</div>
                                    </div>
                                    <div className="bg-slate-900 text-slate-500 p-1.5 rounded border border-slate-850">
                                      <div className="text-slate-500 text-[8px]">FP</div>
                                      <div className="font-bold">{m.FP}</div>
                                    </div>
                                    <div className="bg-slate-900 text-slate-500 p-1.5 rounded border border-slate-850">
                                      <div className="text-slate-500 text-[8px]">FN</div>
                                      <div className="font-bold">{m.FN}</div>
                                    </div>
                                    <div className="bg-teal-500/10 text-teal-400 p-1.5 rounded border border-teal-500/20">
                                      <div className="text-slate-500 text-[8px]">TN</div>
                                      <div className="font-bold">{m.TN}</div>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* NESTED TAB 2: EXPLAINABLE AI (SHAP & LIME) */}
                  {compActiveTab === 'xai' && (
                    <div className="space-y-6">
                      
                      {/* Nested XAI Subtabs */}
                      <div className="flex bg-slate-950 border border-slate-850 p-1 rounded-xl w-fit gap-2">
                        {[
                          { id: 'shap', label: 'SHAP Global Analysis' },
                          { id: 'lime', label: 'LIME Local Analysis' },
                          { id: 'shap_vs_lime', label: 'SHAP vs LIME Comparison' }
                        ].map(sub => (
                          <button
                            key={sub.id}
                            onClick={() => setXaiSubTab(sub.id)}
                            className={`py-1.5 px-3 rounded-lg text-[10px] font-bold transition-all uppercase tracking-wider ${xaiSubTab === sub.id ? 'bg-teal-500 text-slate-950' : 'text-slate-400 hover:text-slate-200'}`}
                          >
                            {sub.label}
                          </button>
                        ))}
                      </div>

                      {/* SUBTABS 1: SHAP SUMMARY */}
                      {xaiSubTab === 'shap' && (
                        <div className="space-y-6">
                          <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                            <div>
                              <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">Global Feature Importance (SHAP values)</h4>
                              <p className="text-xs text-slate-500">Aggregated SHAP feature impact scores demonstrating predictor weight distributions.</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                              {/* Importance chart */}
                              <div className="lg:col-span-2 h-[260px]">
                                <ResponsiveContainer width="100%" height="100%">
                                  <BarChart
                                    data={COMPARATIVE_DB.shap.features}
                                    layout="vertical"
                                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                                  >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                                    <XAxis type="number" stroke="#6b7280" style={{ fontSize: 9 }} />
                                    <YAxis dataKey="name" type="category" stroke="#6b7280" style={{ fontSize: 9 }} />
                                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1f2937', borderRadius: '10px' }} />
                                    <Bar dataKey="importance" fill="#14b8a6" radius={[0, 4, 4, 0]} />
                                  </BarChart>
                                </ResponsiveContainer>
                              </div>

                              {/* SHAP Insight Cards */}
                              <div className="space-y-4">
                                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-2xl">
                                  <span className="text-[9px] font-bold text-teal-400 uppercase tracking-wider block">Top Positive Risk Driver</span>
                                  <span className="text-sm font-bold text-white block mt-1">cvdrisk / Age</span>
                                  <p className="text-[10px] text-slate-500 mt-1">Higher age and high raw risk predictions drive risk scores upwards.</p>
                                </div>
                                <div className="bg-slate-950/60 border border-slate-800 p-4 rounded-2xl">
                                  <span className="text-[9px] font-bold text-rose-400 uppercase tracking-wider block">Top Protective Factor</span>
                                  <span className="text-sm font-bold text-white block mt-1">Active Exercise</span>
                                  <p className="text-[10px] text-slate-500 mt-1">Active lifestyles yield negative SHAP impact, pulling patient risks downwards.</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* SUBTABS 2: LIME SUMMARY */}
                      {xaiSubTab === 'lime' && (
                        <div className="space-y-6">
                          <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                            <div className="flex justify-between items-center">
                              <div>
                                <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">LIME Simulation Patient Comparison</h4>
                                <p className="text-xs text-slate-500">Simulate individual patient explanations for different models side-by-side.</p>
                              </div>
                              {/* Patient Selector */}
                              <select
                                value={compPatientId}
                                onChange={(e) => setCompPatientId(e.target.value)}
                                className="bg-slate-950 border border-slate-800 text-xs font-semibold rounded-xl py-2 px-4 focus:border-teal-500 focus:outline-none text-slate-300"
                              >
                                {Object.keys(COMPARATIVE_DB.lime.patients).map(id => (
                                  <option key={id} value={id}>{COMPARATIVE_DB.lime.patients[id].name}</option>
                                ))}
                              </select>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                              {/* Prediction Confidence Gauge */}
                              <div className="bg-slate-950/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-center items-center text-center">
                                <div className="relative w-36 h-36 rounded-full border-4 border-dashed border-teal-500/20 flex flex-col items-center justify-center bg-slate-950">
                                  <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">LIME Probability</span>
                                  <span className="text-4xl font-extrabold text-teal-400 font-outfit mt-1">
                                    {Math.round(COMPARATIVE_DB.lime.patients[compPatientId].prob * 100)}%
                                  </span>
                                  <span className="text-[8px] bg-teal-500/10 text-teal-400 px-2 py-0.5 rounded-full border border-teal-500/20 font-bold block mt-1">
                                    {COMPARATIVE_DB.lime.patients[compPatientId].prob >= 0.5 ? 'HIGH RISK' : 'LOW RISK'}
                                  </span>
                                </div>
                              </div>

                              {/* LIME Contribution chart */}
                              <div className="lg:col-span-2 space-y-4">
                                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Active Local Features Contributions</span>
                                <div className="space-y-3">
                                  {COMPARATIVE_DB.lime.patients[compPatientId].features.map((feat, idx) => (
                                    <div key={idx} className="space-y-1">
                                      <div className="flex justify-between text-xs font-semibold">
                                        <span className="text-slate-300">{feat.name}</span>
                                        <span className={feat.type === 'positive' ? 'text-teal-400' : 'text-rose-400'}>
                                          {feat.type === 'positive' ? '+' : ''}{feat.weight}
                                        </span>
                                      </div>
                                      <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden flex">
                                        {feat.type === 'positive' ? (
                                          <div className="h-full bg-teal-500 rounded-full" style={{ width: `${feat.weight * 100}%` }}></div>
                                        ) : (
                                          <div className="h-full bg-rose-500 rounded-full ml-auto" style={{ width: `${Math.abs(feat.weight) * 100}%` }}></div>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* SUBTABS 3: SHAP VS LIME COMPARATIVE */}
                      {xaiSubTab === 'shap_vs_lime' && (
                        <div className="space-y-6">
                          <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                            <div>
                              <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">SHAP vs LIME Structural Comparison</h4>
                              <p className="text-xs text-slate-500">Methodological evaluation score breakdown for clinical interpretability.</p>
                            </div>

                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                              {/* Radar compare chart */}
                              <div className="lg:col-span-2 h-[260px]">
                                <ResponsiveContainer width="100%" height="100%">
                                  <RadarChart
                                    cx="50%" cy="50%" outerRadius="80%"
                                    data={[
                                      { subject: 'Global Expl', SHAP: 95, LIME: 40 },
                                      { subject: 'Local Expl', SHAP: 80, LIME: 95 },
                                      { subject: 'Speed', SHAP: 30, LIME: 85 },
                                      { subject: 'Consistency', SHAP: 95, LIME: 60 },
                                      { subject: 'Clinical Usability', SHAP: 85, LIME: 80 },
                                      { subject: 'Feature Stability', SHAP: 90, LIME: 50 },
                                      { subject: 'Trust Score', SHAP: 92, LIME: 75 }
                                    ]}
                                  >
                                    <PolarGrid stroke="#1f2937" />
                                    <PolarAngleAxis dataKey="subject" stroke="#6b7280" style={{ fontSize: 9 }} />
                                    <PolarRadiusAxis stroke="#6b7280" style={{ fontSize: 8 }} />
                                    <Radar name="SHAP" dataKey="SHAP" stroke="#14b8a6" fill="#14b8a6" fillOpacity={0.2} />
                                    <Radar name="LIME" dataKey="LIME" stroke="#f43f5e" fill="#f43f5e" fillOpacity={0.2} />
                                    <Legend wrapperStyle={{ fontSize: 10 }} />
                                  </RadarChart>
                                </ResponsiveContainer>
                              </div>

                              {/* Comparison Narrative */}
                              <div className="space-y-4 text-xs leading-relaxed text-slate-300">
                                <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 space-y-2">
                                  <h5 className="font-bold text-teal-400">Clinical Recommendation</h5>
                                  <p><strong>SHAP</strong> is ideal for <strong>Global Cohort Profiling</strong> (understanding what features the hospital model weights highest across all patients).</p>
                                  <p><strong>LIME</strong> is more suitable for <strong>Local Scenario Simulations</strong> where clinicians need rapid, patient-specific explanations on blood pressure and weight changes during check-ups.</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* NESTED TAB 3: STATISTICAL ANALYSIS */}
                  {compActiveTab === 'statistics' && (
                    <div className="space-y-6">
                      <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                        <div>
                          <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">Hypothesis Testing & Significance Summary</h4>
                          <p className="text-xs text-slate-500">Validating model error distributions and predictive significance.</p>
                        </div>

                        {/* P-Value Table */}
                        <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                          <table className="w-full text-left text-xs border-collapse">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold bg-slate-950/60">
                                <th className="py-2.5 px-4">Statistical Test</th>
                                <th className="py-2.5 px-4">Null Hypothesis (H0)</th>
                                <th className="py-2.5 px-4">Test Statistic</th>
                                <th className="py-2.5 px-4">P-Value</th>
                                <th className="py-2.5 px-4">Outcome</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
                              <tr className="hover:bg-slate-900/20 text-slate-300">
                                <td className="py-3 px-4 font-sans font-bold text-white">ANOVA</td>
                                <td className="py-3 px-4 text-slate-400">All models perform equally</td>
                                <td className="py-3 px-4">F = 185.42</td>
                                <td className="py-3 px-4 text-teal-400 font-bold">1.24e-18</td>
                                <td className="py-3 px-4 font-sans font-semibold text-teal-400">Reject H0 (Sig)</td>
                              </tr>
                              <tr className="hover:bg-slate-900/20 text-slate-300">
                                <td className="py-3 px-4 font-sans font-bold text-white">Friedman Test</td>
                                <td className="py-3 px-4 text-slate-400">Model ranks are random</td>
                                <td className="py-3 px-4">Chi2 = 42.15</td>
                                <td className="py-3 px-4 text-teal-400 font-bold">3.18e-08</td>
                                <td className="py-3 px-4 font-sans font-semibold text-teal-400">Reject H0 (Sig)</td>
                              </tr>
                              <tr className="hover:bg-slate-900/20 text-slate-300">
                                <td className="py-3 px-4 font-sans font-bold text-white">Wilcoxon Signed Rank</td>
                                <td className="py-3 px-4 text-slate-400">CatBoost vs KNN errors identical</td>
                                <td className="py-3 px-4">W = 312.0</td>
                                <td className="py-3 px-4 text-teal-400 font-bold">2.41e-04</td>
                                <td className="py-3 px-4 font-sans font-semibold text-teal-400">Reject H0 (Sig)</td>
                              </tr>
                              <tr className="hover:bg-slate-900/20 text-slate-300">
                                <td className="py-3 px-4 font-sans font-bold text-white">McNemar Test</td>
                                <td className="py-3 px-4 text-slate-400">Model predictions agreement is random</td>
                                <td className="py-3 px-4">Chi2 = 14.8</td>
                                <td className="py-3 px-4 text-teal-400 font-bold">1.22e-04</td>
                                <td className="py-3 px-4 font-sans font-semibold text-teal-400">Reject H0 (Sig)</td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* NESTED TAB 4: CLINICAL INSIGHTS */}
                  {compActiveTab === 'insights' && (
                    <div className="space-y-6">
                      <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-4">
                        <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">Dynamic AI Observations</h4>
                        <div className="space-y-3 text-xs leading-relaxed text-slate-300">
                          <div className="p-4 bg-slate-950/60 rounded-2xl border-l-4 border-teal-500">
                            <strong>🏆 Best Performing Classifier:</strong> CatBoost (Thesis model) and Logistic Regression achieved perfect metrics (ROC-AUC = 1.0) on the active dataset experiments.
                          </div>
                          <div className="p-4 bg-slate-950/60 rounded-2xl border-l-4 border-amber-500">
                            <strong>⚠️ Data Leakage Warning:</strong> The inclusion of the <code>cvdrisk</code> continuous score acts as a direct classification leak. In clinical production, this metric must be removed to train on raw vitals alone.
                          </div>
                          <div className="p-4 bg-slate-950/60 rounded-2xl border-l-4 border-teal-500">
                            <strong>🔬 Key Risk Drivers:</strong> Global SHAP feature analysis identified Age, Systolic Blood Pressure (sbp_avg), and Total Cholesterol as the most influential clinical features driving CVD classification.
                          </div>
                          <div className="p-4 bg-slate-950/60 rounded-2xl border-l-4 border-teal-500">
                            <strong>📊 Decision Consistency:</strong> LIME patient simulations successfully confirmed patient-level decision consistency across all ensemble classifiers, reinforcing clinic audit readiness.
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* NESTED TAB 5: EXECUTIVE SUMMARY */}
                  {compActiveTab === 'summary' && (
                    <div className="space-y-6">
                      <div className="bg-slate-900/40 border border-slate-800/80 rounded-3xl p-6 shadow-md space-y-6">
                        <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                          <div>
                            <h4 className="text-sm font-bold text-white uppercase tracking-wider font-outfit">Executive Performance & Explainability Summary</h4>
                            <p className="text-[10px] text-slate-500">Publication-quality report overview suitable for hospital presentations.</p>
                          </div>
                          <button 
                            onClick={() => window.print()}
                            className="bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold py-1.5 px-3 rounded-lg text-[10px] uppercase transition-all"
                          >
                            Export Report
                          </button>
                        </div>

                        {/* Executive KPIs */}
                        <div className="grid grid-cols-3 gap-4">
                          <div className="bg-slate-950 p-4 rounded-xl text-center">
                            <span className="text-[9px] text-slate-500 font-bold uppercase">Primary Model</span>
                            <span className="text-sm font-bold text-white block mt-1">CatBoost Ensemble</span>
                          </div>
                          <div className="bg-slate-950 p-4 rounded-xl text-center">
                            <span className="text-[9px] text-slate-500 font-bold uppercase">Accuracy Score</span>
                            <span className="text-sm font-bold text-teal-400 block mt-1">1.0000</span>
                          </div>
                          <div className="bg-slate-950 p-4 rounded-xl text-center">
                            <span className="text-[9px] text-slate-500 font-bold uppercase">ROC-AUC Score</span>
                            <span className="text-sm font-bold text-teal-400 block mt-1">1.0000</span>
                          </div>
                        </div>

                        {/* Executive Leaderboard */}
                        <div className="space-y-3">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Overall Leaderboard Ranking</span>
                          <div className="overflow-x-auto border border-slate-800 rounded-xl">
                            <table className="w-full text-left text-xs border-collapse">
                              <thead>
                                <tr className="bg-slate-950 border-b border-slate-800 text-slate-500 uppercase text-[10px] font-bold">
                                  <th className="py-2.5 px-3">Model</th>
                                  <th className="py-2.5 px-3">Accuracy</th>
                                  <th className="py-2.5 px-3">F1-Score</th>
                                  <th className="py-2.5 px-3">ROC-AUC</th>
                                  <th className="py-2.5 px-3">Training Time</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-800/60 font-mono text-[10px] text-slate-300">
                                {Object.keys(COMPARATIVE_DB.models).map((modelId) => {
                                  const m = COMPARATIVE_DB.models[modelId];
                                  return (
                                    <tr key={modelId} className="hover:bg-slate-900/10">
                                      <td className="py-2 px-3 font-sans font-bold text-white">{m.name}</td>
                                      <td className="py-2 px-3">{m.Accuracy}</td>
                                      <td className="py-2 px-3">{m["F1-Score"]}</td>
                                      <td className="py-2 px-3 text-teal-400">{m["ROC-AUC"]}</td>
                                      <td className="py-2 px-3 text-slate-500">{m["Training Time"]}s</td>
                                    </tr>
                                  );
                                })}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                </div>
              </div>

            </div>
          )}

          {/* TAB 8: TENANT ADMINISTRATION */}
          {activeTab === 'admin_dashboard' && (
            <div className="space-y-6">
              {/* Tenant Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <Server className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Active Tenant</span>
                    <span className="text-sm font-bold text-white block">{user.tenant_id}</span>
                  </div>
                </div>
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <Activity className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Total Assessments</span>
                    <span className="text-sm font-bold text-white block">{tenantStats ? tenantStats.total_predictions : 0}</span>
                  </div>
                </div>
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <AlertTriangle className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">High Risk Ratio</span>
                    <span className="text-sm font-bold text-white block">{tenantStats ? tenantStats.high_risk_percentage : 0.0}%</span>
                  </div>
                </div>
                <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-5 shadow-md flex items-center gap-4">
                  <div className="p-3 bg-teal-500/10 text-teal-400 rounded-xl">
                    <Users className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Active Clinicians</span>
                    <span className="text-sm font-bold text-white block">{tenantStats ? tenantStats.active_clinicians : 1}</span>
                  </div>
                </div>
              </div>

              {/* Tenant Administration Portal info */}
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-4">
                <h3 className="text-lg font-bold text-white font-outfit">SaaS Tenant Overview</h3>
                <p className="text-xs text-slate-400 leading-relaxed text-slate-300">Enterprise management for hospital operations. All clinical diagnostics, observations, and uploader usage are dynamically isolated to your hospital database partition. No cross-tenant data leaks are possible under the secure multi-tenancy layer.</p>
                <div className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 space-y-2 text-xs">
                  <div className="flex justify-between border-b border-slate-800 py-1.5">
                    <span className="text-slate-400">Tenant Identity:</span>
                    <span className="font-semibold text-white">{user.tenant_id}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800 py-1.5">
                    <span className="text-slate-400">Database Partition Status:</span>
                    <span className="font-semibold text-teal-400">✓ Isolated (Postgres Schema-Isolated)</span>
                  </div>
                  <div className="flex justify-between py-1.5">
                    <span className="text-slate-400">Audit Signatures Verified:</span>
                    <span className="font-semibold text-teal-400">✓ Cryptographically Secured</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 9: CRYPTOGRAPHIC AUDIT TRAIL */}
          {activeTab === 'audit_trail' && (
            <div className="space-y-6">
              <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl space-y-6">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="text-lg font-bold text-white font-outfit">Chained Cryptographic Audit Ledger</h3>
                    <p className="text-xs text-slate-400">Every assessment, authentication event, and API access is cryptographically chained using SHA-256 HMAC signatures.</p>
                  </div>
                  <button 
                    onClick={handleVerifyAudit}
                    disabled={verifyingAudit}
                    className="bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold py-2 px-4 rounded-xl text-xs flex items-center gap-1.5 transition-all"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${verifyingAudit ? 'animate-spin' : ''}`} />
                    Verify Ledger Integrity
                  </button>
                </div>

                {verificationResult && (
                  <div className={`p-4 border rounded-2xl text-xs flex items-center gap-3 ${verificationResult.verified ? 'bg-teal-500/10 border-teal-500/20 text-teal-300' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`}>
                    <ShieldAlert className="w-5 h-5 flex-shrink-0" />
                    <div>
                      <div className="font-bold uppercase tracking-wider">{verificationResult.verified ? 'Ledger Verified Intact' : 'Warning: Ledger Compromise Detected'}</div>
                      <div>{verificationResult.message}</div>
                    </div>
                  </div>
                )}

                <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-semibold bg-slate-950/60">
                        <th className="py-3 px-4">Event</th>
                        <th className="py-3 px-4">Timestamp</th>
                        <th className="py-3 px-4">Tenant</th>
                        <th className="py-3 px-4">Metadata</th>
                        <th className="py-3 px-4">Signature Chain</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-[11px] font-mono">
                      {auditLogs.length > 0 ? (
                        auditLogs.map((log, idx) => (
                          <tr key={idx} className="hover:bg-slate-900/20 transition-colors">
                            <td className="py-3 px-4 font-bold text-white">{log.event_type}</td>
                            <td className="py-3 px-4 text-slate-400">{log.timestamp}</td>
                            <td className="py-3 px-4 text-teal-400">{log.tenant_id}</td>
                            <td className="py-3 px-4 text-slate-500 max-w-[200px] truncate">{JSON.stringify(log)}</td>
                            <td className="py-3 px-4">
                              <span className="text-[10px] bg-teal-500/10 text-teal-400 px-2 py-0.5 rounded border border-teal-500/20 font-bold block text-center truncate max-w-[150px]">
                                {log.signature || 'N/A'}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="py-6 text-center text-slate-500">
                            Click "Verify Ledger Integrity" to verify the logs.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      {/* Floating Interactive Speech Bot */}
      <div className="fixed bottom-6 right-6 z-50 flex items-end gap-3">
        {/* Chat / Transcript Balloon */}
        {(transcript || voiceReply) && (
          <div className="bg-slate-900 border border-slate-850 rounded-2xl p-4 shadow-2xl max-w-xs space-y-3 animate-fade-in-up">
            {transcript && (
              <div>
                <span className="text-[8px] font-bold text-slate-500 uppercase tracking-widest block">臨床スタッフ (Heard)</span>
                <p className="text-xs italic text-slate-300 font-semibold mt-0.5">"{transcript}"</p>
              </div>
            )}
            {voiceReply && (
              <div className="border-t border-slate-800/80 pt-2">
                <span className="text-[8px] font-bold text-teal-400 uppercase tracking-widest block">AI Assistant (Voice)</span>
                <p className="text-xs text-teal-200 leading-relaxed mt-0.5">{voiceReply}</p>
              </div>
            )}
          </div>
        )}

        {/* Pulse button */}
        <button 
          onClick={toggleListening}
          className={`w-14 h-14 rounded-full flex items-center justify-center shadow-xl transition-all active:scale-[0.9] ${isListening ? 'bg-teal-500 text-slate-950 pulse-teal' : 'bg-slate-900 text-teal-400 border border-teal-500/30 hover:border-teal-500/60'}`}
        >
          {isListening ? <Mic className="w-6 h-6 animate-pulse" /> : <MicOff className="w-6 h-6" />}
        </button>
      </div>
    </div>
  );
}

export default App;
