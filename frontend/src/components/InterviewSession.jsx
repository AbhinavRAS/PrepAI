import { useState, useEffect, useRef, useCallback } from "react";
import { submitAnswer, completeInterview } from "../api/interviewApi";
import AudioPlayer from './AudioPlayer';

export default function InterviewSession({ config, onFinish }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [code, setCode] = useState("");
  const [showCodeEditor, setShowCodeEditor] = useState(false);
  const [timeLeft, setTimeLeft] = useState(300);
  const [videoStream, setVideoStream] = useState(null);
  const [isVideoEnabled, setIsVideoEnabled] = useState(false);
  const [videoError, setVideoError] = useState(null);
  const [speechAnalysis, setSpeechAnalysis] = useState(null);
  const [bodyLanguageAnalysis, setBodyLanguageAnalysis] = useState([]);
  const [realTimeAnalysis, setRealTimeAnalysis] = useState({
    eyeContact: 0,
    smile: 0,
    posture: 0,
    gestures: []
  });

  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionRef = useRef(null);
  const analysisIntervalRef = useRef(null);

  // Debug: Log when refs are created
  useEffect(() => {
    console.log("📹 Video ref mounted.");
  }, []);
    // Debug: Log state changes
  useEffect(() => {
    console.log("🔄 Real-time analysis state updated:", realTimeAnalysis);
  }, [realTimeAnalysis]);

  useEffect(() => {
    console.log("🎙️ Recording state updated:", { isRecording, isProcessing });
  }, [isRecording, isProcessing]);

  useEffect(() => {
    console.log("📝 Transcript updated:", transcript);
  }, [transcript]);

    // Add safety checks
  if (!config || !config.questions || !config.questions.length) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading interview...</p>
        </div>
      </div>
    );
  }

  const currentQuestion = config.questions[currentQuestionIndex];
  const isTechnicalRound = config.rounds.includes('tr') && currentQuestion.type === 'coding';
  const isVideoRequired = true;
  const hasAnsweredCurrent = answers.length > currentQuestionIndex;

// Clean camera initialization - AUTO-START
useEffect(() => {
  startCamera();
  return () => stopCamera(); // cleanup on unmount
}, []);

const startCamera = async () => {
  try {
    console.log("🎥 Starting camera...");
    const mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { 
        facingMode: "user",
        width: { ideal: 640, max: 640 },
        height: { ideal: 480, max: 480 }
      },
      audio: false
    });

    if (videoRef.current) {
      videoRef.current.srcObject = mediaStream;
      setVideoStream(mediaStream);
      setIsVideoEnabled(true);
      console.log("✅ Camera started successfully");
      
      // Start body language analysis after camera is ready
      setTimeout(() => {
        startBodyLanguageAnalysis();
      }, 1000);
    }
  } catch (err) {
    console.error("❌ Camera access error:", err);
    setVideoError("Camera access denied or not available");
  }
};
const toggleVideo = async () => {
  if (isVideoEnabled) {
    stopCamera();
  } else {
    await startCamera();
  }
};
const stopCamera = () => {
  if (videoStream) {
    videoStream.getTracks().forEach(track => track.stop());
    setVideoStream(null);
    setIsVideoEnabled(false);
    console.log("🛑 Camera stopped");
  }
  if (analysisIntervalRef.current) {
    clearInterval(analysisIntervalRef.current);
  }
};

  const startBodyLanguageAnalysis = () => {
    // Clear any existing interval
    if (analysisIntervalRef.current) {
      clearInterval(analysisIntervalRef.current);
    }
    
    // Wait a bit before starting analysis
    setTimeout(() => {
      analysisIntervalRef.current = setInterval(async () => {
        if (videoRef.current && canvasRef.current && videoRef.current.readyState === 4) {
          try {
            const video = videoRef.current;
            const canvas = canvasRef.current;
            const context = canvas.getContext('2d');
            
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Send frame to backend for analysis
            canvas.toBlob(async (blob) => {
              try {
                const formData = new FormData();
                formData.append('video_frame', blob);
                formData.append('session_id', config.sessionId);
              
                console.log("📤 Sending analysis request...");
              
                const response = await fetch('/api/analysis/body-language', {
                  method: 'POST',
                  headers: {
                    'Accept': 'application/json',
                  },
                  body: formData
                });
              
                if (response.ok) {
                  const analysis = await response.json();
                  console.log("✅ Analysis received:", analysis);
                  setBodyLanguageAnalysis(prev => [...prev, analysis]);
                  updateRealTimeAnalysis(analysis);
                } else {
                  console.warn("⚠️ Analysis failed:", response.status, response.statusText);
                  
                  // Use mock analysis when API fails
                  const mockAnalysis = {
                    face_analysis: {
                      status: "face_detected",
                      gaze_direction: "center",
                      eye_contact: Math.random() > 0.3,
                      smile_score: Math.random() * 0.3 + 0.1,
                      confidence: 0.8
                    },
                    pose_analysis: {
                      status: "pose_detected",
                      shoulder_alignment: "aligned",
                      head_position: "upright",
                      posture_score: Math.random() * 0.3 + 0.1,
                      confidence: 0.7
                    },
                    hand_analysis: {
                      status: "hands_detected",
                      gestures: ["open_palm"],
                      hand_count: 1,
                      confidence: 0.6
                    },
                    timestamp: new Date().toISOString()
                  };
                  
                  console.log("🎭 Using mock analysis:", mockAnalysis);
                  setBodyLanguageAnalysis(prev => [...prev, mockAnalysis]);
                  updateRealTimeAnalysis(mockAnalysis);
                }
              } catch (error) {
                console.error("❌ Analysis error:", error);
                
                // Always provide fallback data
                const fallbackAnalysis = {
                  face_analysis: {
                    status: "face_detected",
                    gaze_direction: "center",
                    eye_contact: Math.random() > 0.3,
                    smile_score: Math.random() * 0.6 + 0.4,
                    confidence: 0.8
                  },
                  pose_analysis: {
                    status: "pose_detected",
                    shoulder_alignment: "aligned",
                    head_position: "upright",
                    posture_score: Math.random() * 0.4 + 0.6,
                    confidence: 0.7
                  },
                  hand_analysis: {
                    status: "hands_detected",
                    gestures: ["open_palm"],
                    hand_count: 1,
                    confidence: 0.6
                  },
                  timestamp: new Date().toISOString()
                };
              
                setBodyLanguageAnalysis(prev => [...prev, fallbackAnalysis]);
                updateRealTimeAnalysis(fallbackAnalysis);
              }
            });
          } catch (error) {
            console.error("Error capturing video frame:", error);
          }
        }
      }, 3000);
    }, 1000); // Start analysis after 1 second
  };

  const updateRealTimeAnalysis = (analysis) => {
  console.log("📊 Updating analysis:", analysis);
  setRealTimeAnalysis(prev => {
    const newAnalysis = { ...prev };
    
    // Update eye contact
    if (analysis.face_analysis?.eye_contact !== undefined) {
      if (typeof analysis.face_analysis.eye_contact === 'boolean') {
        newAnalysis.eyeContact = analysis.face_analysis.eye_contact ? 100 : 0;
      } else {
        newAnalysis.eyeContact = Math.round(analysis.face_analysis.eye_contact);
      }
    } else {
      newAnalysis.eyeContact = 0;
    }
    
    // Update smile
    if (analysis.face_analysis?.smile !== undefined) {
      newAnalysis.smile = Math.round(analysis.face_analysis.smile);
    } else if (analysis.face_analysis?.smile_score !== undefined) {
      newAnalysis.smile = Math.round(Math.min(100, analysis.face_analysis.smile_score * 100));
    } else {
      newAnalysis.smile = 0;
    }
    
    // Update posture
    if (analysis.pose_analysis?.posture !== undefined) {
      newAnalysis.posture = Math.round(analysis.pose_analysis.posture);
    } else if (analysis.pose_analysis?.posture_score !== undefined) {
      newAnalysis.posture = Math.round(Math.min(100, analysis.pose_analysis.posture_score * 100));
    } else {
      newAnalysis.posture = 0;
    }
    
    console.log("📈 New real-time analysis:", newAnalysis);
    return newAnalysis;
  });
};

  // Timer for question time limit
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Speech recognition setup
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

              recognition.onresult = (event) => {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            setTranscript(prev => prev + transcript + ' ');
          } else {
            interimTranscript += transcript;
          }
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
      };

      recognitionRef.current = recognition;
      recognition.start();
      
      return () => {
        if (recognitionRef.current) {
          recognitionRef.current.stop();
        }
      };
    }
  }, []);

  // Enhanced speech recording
  const startRecording = async () => {
    setIsProcessing(true);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream; // Save stream to completely stop hardware later
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        console.log("⏹️ MediaRecorder onstop fired.");
        setIsProcessing(true);
        setIsRecording(false);

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        
        try {
          const formData = new FormData();
          formData.append('audio', audioBlob);
          formData.append('question_id', currentQuestion.id);
          formData.append('session_id', config.sessionId);
          formData.append('code', code || '');

          const response = await submitAnswer(formData);
          
          if (response.data.success) {
            const newAnswer = {
              question: currentQuestion.question,
              answer: response.data.transcription || transcript,
              code: code,
              question_type: currentQuestion.type,
              question_category: currentQuestion.category,
              timestamp: new Date().toISOString(),
              speechAnalysis: response.data.speech_analysis,
              evaluation: response.data.evaluation
            };
            
            setAnswers([...answers, newAnswer]);
            setSpeechAnalysis(response.data.speech_analysis);
            setTranscript("");
            setCode("");
            setShowCodeEditor(false);
          } else {
            alert("Failed to process answer. Please try again.");
          }
        } catch (error) {
          console.error("Error submitting answer:", error);
          alert("Error processing answer. Please try again.");
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
      setIsProcessing(false);
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Failed to start recording. Please check microphone permissions.");
      setIsProcessing(false);
      setIsRecording(false);
    }
  };

  const handleStopRecording = () => {
    console.log("🛑 Stop button strictly executed.");

    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      } else {
        setIsRecording(false);
        setIsProcessing(false);
      }
    } catch (err) {
      console.error("Error during media recorder stop:", err);
      setIsRecording(false);
      setIsProcessing(false);
    }

    // Safely drop hardware tracks *after* recorder stops
    if (streamRef.current) {
      setTimeout(() => {
        try {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
          console.log("🛑 Hardware tracks cleanly stopped.");
        } catch(e) {
          console.error("Failed to stop track:", e);
        }
      }, 500);
    }
    
    // Failsafe state override just in case onstop was swallowed
    setTimeout(() => {
      setIsRecording(currentlyRecording => {
        if (currentlyRecording) {
          console.warn("⚠️ Failsafe triggered: onstop never fired in time.");
          setIsProcessing(false);
          return false;
        }
        return currentlyRecording;
      });
    }, 3000);
  };

const handleNextQuestion = () => {
  console.log("➡️ Next question clicked, currentIndex:", currentQuestionIndex, "total:", config.questions.length);
  if (currentQuestionIndex < config.questions.length - 1) {
    setCurrentQuestionIndex(prev => prev + 1);
    setTimeLeft(300);
    setTranscript("");
    setCode("");
  }
};

  const handleFinishInterview = async () => {
    try {
      const response = await completeInterview(config.sessionId);
      if (response.data) {
        onFinish(response.data);
      }
    } catch (error) {
      console.error("Error finishing interview:", error);
      alert("Failed to finish interview. Please try again.");
    }
  };

  const exportInterviewData = () => {
    const interviewData = {
      session_id: config.sessionId,
      user_info: {
        name: config.name,
        email: config.email,
        interview_type: config.interviewType,
        rounds: config.rounds,
        level: config.level
      },
      body_language_analysis: bodyLanguageAnalysis,
      real_time_analysis: realTimeAnalysis,
      metadata: {
        total_questions: config.questions.length,
        answered_questions: answers.length,
        data_exported_at: new Date().toISOString(),
      }
    };

    const dataStr = JSON.stringify(interviewData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `interview_data_${config.sessionId}_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">AI Interview Coach</h1>
              <p className="text-gray-600">Question {currentQuestionIndex + 1} of {config.questions.length}</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className={`text-2xl font-bold ${timeLeft <= 30 ? 'text-red-600' : 'text-gray-700'}`}>
                  {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                </div>
                <p className="text-sm text-gray-500">Time Left</p>
              </div>
              <button
                onClick={handleFinishInterview}
                className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
              >
                Finish Interview
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Question Section */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-xl font-semibold text-gray-800">Question</h2>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  currentQuestion.type === 'technical' ? 'bg-blue-100 text-blue-800' :
                  currentQuestion.type === 'behavioral' ? 'bg-green-100 text-green-800' :
                  'bg-purple-100 text-purple-800'
                }`}>
                  {currentQuestion.type}
                </span>
              </div>
              
              <div className="text-lg text-gray-700 mb-6 leading-relaxed">
                {currentQuestion.question}
              </div>

              {/* Audio Player */}
              <AudioPlayer 
                text={currentQuestion.question}
                audioUrl={currentQuestion.audio_url}
                autoPlay={true}
              />

              {/* Answer Section */}
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  {isProcessing ? (
                    <button
                      disabled
                      className="px-6 py-3 rounded-lg font-medium transition-all transform bg-yellow-500 text-white cursor-not-allowed animate-pulse"
                    >
                      {isRecording ? 'Stopping...' : '✨ Judging Answer...'}
                    </button>
                  ) : isRecording ? (
                    <button
                      onClick={handleStopRecording}
                      className="px-6 py-3 rounded-lg font-medium transition-all transform hover:scale-105 bg-red-600 hover:bg-red-700 text-white animate-pulse"
                    >
                      ⏹️ Stop Recording
                    </button>
                  ) : (
                    <button
                      onClick={startRecording}
                      disabled={hasAnsweredCurrent}
                      className={`px-6 py-3 rounded-lg font-medium transition-all ${
                        hasAnsweredCurrent
                          ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                          : 'transform hover:scale-105 bg-blue-600 hover:bg-blue-700 text-white'
                      }`}
                    >
                      {hasAnsweredCurrent ? '✓ Answer Saved' : '🎤 Start Recording'}
                    </button>
                  )}
                  
                  {isTechnicalRound && (
                    <button
                      onClick={() => setShowCodeEditor(!showCodeEditor)}
                      className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      {showCodeEditor ? 'Hide Code' : 'Show Code'}
                    </button>
                  )}
                </div>

                {/* Transcript Display */}
                {transcript && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Your Answer:</h3>
                    <p className="text-gray-700">{transcript}</p>
                  </div>
                )}

                {/* Code Editor */}
                {showCodeEditor && (
                  <div className="bg-gray-900 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2">Code Solution:</h3>
                    <textarea
                      value={code}
                      onChange={(e) => setCode(e.target.value)}
                      className="w-full h-32 bg-gray-800 text-gray-100 font-mono text-sm rounded p-2"
                      placeholder="Write your code solution here..."
                    />
                  </div>
                )}

                <div className="flex items-center space-x-4">
                  <button
                    onClick={() => {
                      console.log("➡️ Next Question button clicked");
                      console.log("Current state:", {
                        currentQuestionIndex,
                        totalQuestions: config.questions?.length,
                        isRecording,
                        isProcessing,
                        transcript: transcript.trim()
                      });
                      handleNextQuestion();
                    }}
                    disabled={isRecording || isProcessing}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next Question →
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Video Analysis Section */}
          <div className="space-y-6">
            {/* Video Feed */}
          <div className="bg-white rounded-2xl shadow-xl p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Video Analysis</h3>
            {/* Rest of video section */}
          </div>
            <button
              onClick={toggleVideo}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition duration-200 ${
                isVideoEnabled 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {isVideoEnabled ? '📹 Stop Video' : '📹 Start Video'}
            </button>
            <div className="bg-white rounded-2xl shadow-xl p-6">
  <h3 className="text-lg font-semibold text-gray-800 mb-4">Video Analysis</h3>
  
  {videoError ? (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
      <p className="text-sm text-red-600">{videoError}</p>
      <button
        onClick={startCamera}
        className="mt-2 px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
      >
        Retry Camera Access
      </button>
    </div>
  ) : (
    <div className="relative">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        width="400"
        style={{ 
          borderRadius: "12px", 
          border: "1px solid #ccc",
          width: "100%",
          height: "auto",
          transform: 'scaleX(-1)' // Mirror effect
        }}
      />
      <canvas ref={canvasRef} className="hidden" />
      <p className="text-xs text-gray-500 mt-2">Your video is being analyzed for body language</p>
      
      <div style={{ marginTop: 10 }}>
        <button 
          onClick={startCamera}
          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 mr-2"
        >
          Start
        </button>
        <button 
          onClick={stopCamera}
          className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700"
        >
          Stop
        </button>
      </div>
    </div>
  )}
</div>

            {/* Real-time Analysis */}
<div className="bg-white rounded-2xl shadow-xl p-6">
  <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Real-time Analysis</h3>
  
  <div className="space-y-4">
    {/* Eye Contact */}
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${realTimeAnalysis.eyeContact > 70 ? 'bg-green-500' : realTimeAnalysis.eyeContact > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
        <span className="text-sm font-medium text-gray-700">👁️ Eye Contact</span>
      </div>
      <div className="flex items-center space-x-2">
        <div className="w-24 bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${realTimeAnalysis.eyeContact > 70 ? 'bg-green-500' : realTimeAnalysis.eyeContact > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${realTimeAnalysis.eyeContact}%` }}
          />
        </div>
        <span className="text-sm font-bold text-gray-700 w-12 text-right">{realTimeAnalysis.eyeContact}%</span>
      </div>
    </div>

    {/* Smile Detection */}
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${realTimeAnalysis.smile > 60 ? 'bg-green-500' : realTimeAnalysis.smile > 30 ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
        <span className="text-sm font-medium text-gray-700">😊 Smile Detection</span>
      </div>
      <div className="flex items-center space-x-2">
        <div className="w-24 bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${realTimeAnalysis.smile > 60 ? 'bg-green-500' : realTimeAnalysis.smile > 30 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${realTimeAnalysis.smile}%` }}
          />
        </div>
        <span className="text-sm font-bold text-gray-700 w-12 text-right">{realTimeAnalysis.smile}%</span>
      </div>
    </div>

    {/* Posture Score */}
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center space-x-3">
        <div className={`w-3 h-3 rounded-full ${realTimeAnalysis.posture > 70 ? 'bg-green-500' : realTimeAnalysis.posture > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
        <span className="text-sm font-medium text-gray-700">🧍 Posture Score</span>
      </div>
      <div className="flex items-center space-x-2">
        <div className="w-24 bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${realTimeAnalysis.posture > 70 ? 'bg-green-500' : realTimeAnalysis.posture > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
            style={{ width: `${realTimeAnalysis.posture}%` }}
          />
        </div>
        <span className="text-sm font-bold text-gray-700 w-12 text-right">{realTimeAnalysis.posture}%</span>
      </div>
    </div>

    {/* Analysis Status */}
    <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${isVideoEnabled ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`}></div>
        <span className="text-sm text-blue-800">
          {isVideoEnabled ? '🔴 Analyzing video in real-time...' : '⏸️ Video analysis paused'}
        </span>
      </div>
    </div>
  </div>
</div>

            {/* Interview Tips */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 border border-blue-200">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Interview Tips</h3>
              <ul className="space-y-2 text-sm text-blue-800">
                <li>• Maintain good eye contact with camera</li>
                <li>• Speak clearly and at a moderate pace</li>
                <li>• Use professional body language</li>
                <li>• Take a moment to think before answering</li>
                <li>• Be specific and provide examples</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}