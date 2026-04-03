import React from 'react';

export default function Report({ report }) {
  if (!report) return <div>Loading report...</div>;

  const {
    overall_score,
    consistency_analysis,
    technical_assessment,
    communication_analysis,
    speech_analysis,
    body_language_analysis,
    comprehensive_feedback,
    session_summary,
    candidate_name,
    interview_type,
    total_questions,
    answered_questions
  } = report;

  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 70) return 'text-blue-600';
    if (score >= 55) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score) => {
    if (score >= 85) return 'Excellent';
    if (score >= 70) return 'Good';
    if (score >= 55) return 'Satisfactory';
    return 'Needs Improvement';
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-xl shadow-lg">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Interview Evaluation Report
        </h1>
        <p className="text-lg text-gray-600">
          {candidate_name} - {interview_type.toUpperCase()} Interview
        </p>
        <div className="mt-4">
          <span className={`text-4xl font-bold ${getScoreColor(overall_score)}`}>
            {overall_score}/100
          </span>
          <p className="text-lg text-gray-700 mt-1">
            {getScoreLabel(overall_score)} Performance
          </p>
        </div>
      </div>

      {/* Session Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">Session Summary</h3>
        <p className="text-blue-800">{session_summary}</p>
        <div className="mt-2 text-sm text-blue-700">
          Answered {answered_questions} of {total_questions} questions
        </div>
      </div>

      {/* Detailed Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {/* Consistency Score */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <h4 className="font-semibold text-gray-900 mb-2">Response Consistency</h4>
          <div className={`text-2xl font-bold ${getScoreColor(consistency_analysis?.consistency_score || 0)}`}>
            {consistency_analysis?.consistency_score || 0}/100
          </div>
          <p className="text-sm text-gray-600 mt-1">Logical coherence across answers</p>
        </div>

        {/* Technical Score */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <h4 className="font-semibold text-gray-900 mb-2">Technical Knowledge</h4>
          <div className={`text-2xl font-bold ${getScoreColor(technical_assessment?.technical_score || 0)}`}>
            {technical_assessment?.technical_score || 0}/100
          </div>
          <p className="text-sm text-gray-600 mt-1">Depth of technical understanding</p>
        </div>

        {/* Communication Score */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <h4 className="font-semibold text-gray-900 mb-2">Communication</h4>
          <div className={`text-2xl font-bold ${getScoreColor(communication_analysis?.communication_score || 0)}`}>
            {communication_analysis?.communication_score || 0}/100
          </div>
          <p className="text-sm text-gray-600 mt-1">Clarity and articulation</p>
        </div>

        {/* Speech Analysis */}
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <h4 className="font-semibold text-gray-900 mb-2">Speech Patterns</h4>
          <div className={`text-2xl font-bold ${getScoreColor((speech_analysis?.confidence_avg || 0) * 100)}`}>
            {Math.round((speech_analysis?.confidence_avg || 0) * 100)}/100
          </div>
          <p className="text-sm text-gray-600 mt-1">
            Fluency and confidence
          </p>
        </div>

        {/* Body Language */}
        {['government', 'ias', 'ips'].includes(interview_type?.toLowerCase()) && (
          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h4 className="font-semibold text-gray-900 mb-2">Body Language</h4>
            <div className={`text-2xl font-bold ${getScoreColor(body_language_analysis?.overall_engagement || 0)}`}>
              {Math.round(body_language_analysis?.overall_engagement || 0)}/100
            </div>
            <p className="text-sm text-gray-600 mt-1">Professional presence</p>
          </div>
        )}

        {/* Eye Contact */}
        {['government', 'ias', 'ips'].includes(interview_type?.toLowerCase()) && (
          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <h4 className="font-semibold text-gray-900 mb-2">Eye Contact</h4>
            <div className={`text-2xl font-bold ${getScoreColor(body_language_analysis?.eye_contact_avg || 0)}`}>
              {Math.round(body_language_analysis?.eye_contact_avg || 0)}%
            </div>
            <p className="text-sm text-gray-600 mt-1">Engagement level</p>
          </div>
        )}
      </div>

      {/* Comprehensive Feedback */}
      <div className="space-y-6">
        {/* Key Strengths */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-green-900 mb-3">🌟 Key Strengths</h3>
          <ul className="space-y-2">
            {comprehensive_feedback?.key_strengths?.map((strength, index) => (
              <li key={index} className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span className="text-green-800">{strength}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Improvement Areas */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-yellow-900 mb-3">🎯 Areas for Improvement</h3>
          <ul className="space-y-2">
            {comprehensive_feedback?.improvement_areas?.map((area, index) => (
              <li key={index} className="flex items-start">
                <span className="text-yellow-600 mr-2">→</span>
                <span className="text-yellow-800">{area}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Specific Recommendations */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">💡 Specific Recommendations</h3>
          <ul className="space-y-2">
            {comprehensive_feedback?.specific_recommendations?.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span className="text-blue-800">{rec}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Career Suggestions */}
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-purple-900 mb-3">🚀 Career Development Suggestions</h3>
          <ul className="space-y-2">
            {comprehensive_feedback?.career_suggestions?.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="text-purple-600 mr-2">▸</span>
                <span className="text-purple-800">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Next Steps */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">📋 Next Steps</h3>
          <ul className="space-y-2">
            {comprehensive_feedback?.next_steps?.map((step, index) => (
              <li key={index} className="flex items-start">
                <span className="text-gray-600 mr-2">▪</span>
                <span className="text-gray-800">{step}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Technical Analysis Details */}
      {technical_assessment?.knowledge_areas?.length > 0 && (
        <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">🔧 Technical Knowledge Areas</h3>
          <div className="flex flex-wrap gap-2">
            {technical_assessment.knowledge_areas.map((area, index) => (
              <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {area}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Speech Analysis Details */}
      {speech_analysis?.analysis_summary && (
        <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">🎤 Speech Analysis Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <span className="font-medium">Overall Fluency:</span>
              <span className="ml-2">{speech_analysis.analysis_summary.overall_fluency}</span>
            </div>
            <div>
              <span className="font-medium">Speaking Pace:</span>
              <span className="ml-2">{speech_analysis.analysis_summary.speaking_pace}</span>
            </div>
            <div>
              <span className="font-medium">Hesitation Level:</span>
              <span className="ml-2">{speech_analysis.analysis_summary.hesitation_level}</span>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex justify-center space-x-4">
        <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition duration-200">
          📊 Download Report
        </button>
        <button className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition duration-200">
          🔄 Practice Again
        </button>
        <button className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition duration-200">
          📧 Email Report
        </button>
      </div>
    </div>
  );
}