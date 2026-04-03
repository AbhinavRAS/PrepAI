import { useState } from "react";
import InterviewSetup from "../components/InterviewSetup";
import InterviewSession from "../components/InterviewSession";
import Report from "../components/Report";

export default function Home() {
  const [config, setConfig] = useState(null);
  const [report, setReport] = useState(null);

  const finishInterview = async (evaluation) => {
    try {
      // For mock interviews, the evaluation is already complete
      // For real interviews, we might need to call completeInterview
      setReport(evaluation);
    } catch (error) {
      console.error("Error finishing interview:", error);
      // Still set the report even if there's an error
      setReport(evaluation);
    }
  };

  if (report) return <Report report={report} />;
  if (config) return <InterviewSession config={config} onFinish={finishInterview} />;
  return <InterviewSetup onStart={setConfig} />;
}