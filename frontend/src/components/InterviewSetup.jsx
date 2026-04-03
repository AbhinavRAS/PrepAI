import { useState } from "react";
import { startInterview } from "../api/interviewApi";
import InterviewSession from "./InterviewSession";

export default function InterviewSetup({ onStart }) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    interviewType: "",
    rounds: [],
    level: "medium"
  });
  const [loading, setLoading] = useState(false);

  const interviewTypes = [
    { value: "college", label: "College Placement Interview" },
    { value: "experienced", label: "Experienced Professional Interview" },
    { value: "ips", label: "IPS Interview" },
    { value: "ias", label: "IAS Interview" },
    { value: "government", label: "Government Job Interview" },
    { value: "technical", label: "Technical Interview" },
  ];

  const rounds = [
    { value: "tr", label: "Technical Round" },
    { value: "mr", label: "Managerial Round" },
    { value: "hr", label: "HR Round" },
  ];

  const handleRoundChange = (round) => {
    setFormData(prev => ({
      ...prev,
      rounds: prev.rounds.includes(round)
        ? prev.rounds.filter(r => r !== round)
        : [...prev.rounds, round]
    }));
  };

  const startMockInterview = () => {
    console.log("=== Starting Mock Interview Debug ===");
    console.log("1. Function called");
    
    try {
      console.log("2. Current formData:", formData);
      
            const mockQuestions = [];
      
      // Add technical questions if technical round is selected
      if (formData.rounds.includes('tr')) {
        console.log("3. Adding technical question");
        mockQuestions.push({
          id: 'mock_1',
          question: 'What is the difference between let and const in JavaScript?',
          type: 'technical',
          category: 'javascript',
          difficulty: 'easy',
          audio_url: null  // Add this line
        });
        
        mockQuestions.push({
          id: 'mock_2',
          question: 'Explain the concept of closures in JavaScript with an example.',
          type: 'technical',
          category: 'javascript',
          difficulty: 'medium',
          audio_url: null  // Add this line
        });
      }
      
      // Add personal introduction question
      mockQuestions.push({
        id: 'mock_3',
        question: 'Tell me about yourself.',
        type: 'personal',
        category: 'introduction',
        difficulty: 'easy',
        audio_url: null  // Add this line
      });
      
      // Add behavioral question
      mockQuestions.push({
        id: 'mock_4',
        question: 'Describe a challenging situation you faced and how you overcame it.',
        type: 'behavioral',
        category: 'problem-solving',
        difficulty: 'medium',
        audio_url: null  // Add this line
      });
      
      // Add coding question if technical round is selected
      if (formData.rounds.includes('tr')) {
        console.log("4. Adding coding question");
        mockQuestions.push({
          id: 'mock_5',
          question: 'Write a function to reverse a string in JavaScript.',
          type: 'coding',
          category: 'algorithms',
          difficulty: 'medium',
          hint: 'Consider using built-in methods or loops',
          audio_url: null  // Add this line
        });
      }
      
      // Add managerial questions if managerial round is selected
      if (formData.rounds.includes('mr')) {
        console.log("5. Adding managerial question");
        mockQuestions.push({
          id: 'mock_6',
          question: 'How do you handle conflicts in a team?',
          type: 'behavioral',
          category: 'teamwork',
          difficulty: 'medium',
          audio_url: null  // Add this line
        });
      }
      
      // Add HR questions if HR round is selected
      if (formData.rounds.includes('hr')) {
        console.log("6. Adding HR question");
        mockQuestions.push({
          id: 'mock_7',
          question: 'What are your salary expectations?',
          type: 'hr',
          category: 'compensation',
          difficulty: 'easy',
          audio_url: null  // Add this line
        });
      }
      
      console.log("7. Final mock questions prepared:", mockQuestions);
      
      const config = {
        ...formData,
        questions: mockQuestions,
        sessionId: 'mock_session_' + Date.now(),
        level: 'medium'  // Add default level for mock interviews
      };
      
      console.log("8. Calling onStart with config:", config);
      console.log("9. onStart function:", typeof onStart);
      
      // Start mock interview
      onStart(config);
      
      console.log("10. onStart called successfully");
      
    } catch (error) {
      console.error("11. Error in startMockInterview:", error);
      alert("Error starting mock interview: " + error.message);
    }
    
    console.log("=== Mock Interview Debug End ===");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.interviewType || formData.rounds.length === 0) {
      alert("Please fill all fields and select at least one round");
      return;
    }

    setLoading(true);
    try {
      // Try to start GPT-based interview first
      const response = await startInterview({
        name: formData.name,
        email: formData.email,
        interview_type: formData.interviewType,
        rounds: formData.rounds.join(','),
        level: "Entry Level"
      });
      
      // If GPT interview succeeds
      if (response.data && response.data.questions) {
        onStart({
          ...formData,
          questions: response.data.questions,
          sessionId: response.data.session_id
        });
      } else {
        // Fallback to mock interview
        throw new Error("No questions received from API");
      }
    } catch (error) {
      console.log("GPT API failed, starting mock interview:", error.message);
      
      // Automatically start mock interview
      startMockInterview();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h1 className="text-4xl font-bold text-center mb-2 text-gray-800">
            AI Smart Interview Agent
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Practice your interview skills with AI-powered evaluation
          </p>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your full name"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="your@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Type
              </label>
              <select
                value={formData.interviewType}
                onChange={(e) => setFormData(prev => ({ ...prev, interviewType: e.target.value }))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">Select interview type</option>
                {interviewTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Interview Rounds
              </label>
              <div className="space-y-2">
                {rounds.map(round => (
                  <label key={round.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={formData.rounds.includes(round.value)}
                      onChange={() => handleRoundChange(round.value)}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-gray-700">{round.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-4">

              {/* Mock Interview Button */}
              <button
                type="button"
                onClick={startMockInterview}
                className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-700 transition duration-200"
              >
                🎭 Start Mock Interview (Bypass API)
              </button>

              {/* AI Interview Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 transition duration-200"
              >
                {loading ? "Starting Interview..." : "🚀 Start AI Interview"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}