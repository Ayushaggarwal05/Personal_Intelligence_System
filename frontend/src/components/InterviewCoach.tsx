import React, { useState } from 'react';
import { Award, Zap, ChevronRight, CheckCircle } from 'lucide-react';

interface InterviewCoachProps {
  projectId: string | null;
}

export const InterviewCoach: React.FC<InterviewCoachProps> = ({ projectId }) => {
  const [session, setSession] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [userAnswer, setUserAnswer] = useState('');
  const [scorecard, setScorecard] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    setScorecard(null);
    setUserAnswer('');

    try {
      const res = await fetch('http://localhost:8000/api/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId }),
      });
      if (res.ok) {
        const data = await res.json();
        setSession(data);
      } else {
        setError('Failed to initiate mock interview session.');
      }
    } catch (err) {
      setError('Connection to technical coach offline.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitAnswer = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectId || !session || !userAnswer.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch('http://localhost:8000/api/interview/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_path: session.project_path,
          interview_id: session.interview_id,
          qa_id: session.qa_id,
          user_answer: userAnswer.trim(),
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setScorecard(data.evaluation);
        if (data.next_question) {
          setSession({
            ...session,
            qa_id: data.next_question.qa_id,
            question: data.next_question.question,
            focus_area: data.next_question.focus_area,
          });
        }
        setUserAnswer('');
      } else {
        setError('Submission evaluation failed.');
      }
    } catch (err) {
      setError('Connection to submission engine offline.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full p-6 overflow-y-auto bg-black/10 animate-fade-in">
      <div className="flex items-center gap-2 mb-6">
        <Award size={24} className="text-accentPurple" />
        <div>
          <h2 className="text-lg font-bold text-gray-100 font-outfit">Technical Mock Interview Coach</h2>
          <p className="text-xs text-gray-400">Adaptive questions based on your codebase symbols</p>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-950/20 border border-red-500/30 text-red-400 rounded-md text-xs mb-4">
          {error}
        </div>
      )}

      {!session ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center py-20">
          <Zap size={48} className="text-accentPurple/45 mb-4 animate-pulse" />
          <h3 className="text-base font-semibold text-gray-200 mb-2 font-outfit">Start Mock Interview Session</h3>
          <p className="text-xs text-gray-400 max-w-[400px] mb-6 leading-relaxed">
            Answer system questions generated dynamically from your code class schemas, routes, and functional dependencies.
          </p>
          <button onClick={handleStart} disabled={!projectId || isLoading} className="glow-btn">
            {isLoading ? 'Booting Coach...' : 'Launch Interview'}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          {/* Question panel */}
          <div className="p-4 border-l-4 border-accentPurple bg-bgCard backdrop-blur-md rounded-r-lg border border-white/5">
            <span className="text-[10px] text-accentCyan font-bold block mb-1.5 font-mono uppercase">
              FOCUS AREA: {session.focus_area}
            </span>
            <span className="text-sm font-medium text-white leading-relaxed">
              {session.question}
            </span>
          </div>

          {/* Submission form */}
          <form onSubmit={handleSubmitAnswer} className="flex flex-col gap-3">
            <textarea
              placeholder="Draft your explanation answer here in detail..."
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              disabled={isLoading}
              className="w-full h-32 bg-black/20 border border-white/10 rounded-lg p-3 text-xs text-white outline-none resize-none box-border leading-relaxed focus:border-accentPurple/50 transition-all"
            />
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setSession(null)}
                className="px-4 py-2 text-xs rounded border border-white/10 bg-transparent text-gray-400 hover:text-white hover:bg-white/5 transition-all cursor-pointer"
              >
                Quit
              </button>
              <button type="submit" disabled={isLoading || !userAnswer.trim()} className="glow-btn">
                {isLoading ? 'Grading Answer...' : 'Submit Answer'}
              </button>
            </div>
          </form>

          {/* Scorecard Results Overlay */}
          {scorecard && (
            <div className="p-5 mt-4 border-l-4 border-accentCyan bg-bgCard backdrop-blur-md rounded-r-lg border border-white/5 animate-fade-in">
              <div className="flex justify-between items-center mb-4">
                <span className="flex items-center gap-1.5 font-bold text-sm text-gray-100 font-outfit">
                  <CheckCircle size={18} className="text-accentCyan" />
                  Evaluation Scorecard
                </span>
                <span className="text-2xl font-extrabold text-accentCyan font-outfit">
                  {scorecard.score}/100
                </span>
              </div>

              <div className="flex flex-col gap-3 text-xs">
                <div>
                  <span className="text-gray-400 font-semibold block mb-1 text-[11px] font-outfit">Suggestions:</span>
                  <p className="text-gray-200 m-0 leading-relaxed">{scorecard.suggestions}</p>
                </div>

                {scorecard.model_answer && (
                  <div>
                    <span className="text-gray-400 font-semibold block mb-1 text-[11px] font-outfit">Model Answer Key:</span>
                    <p className="text-gray-400 m-0 italic leading-relaxed">{scorecard.model_answer}</p>
                  </div>
                )}

                <div className="border-t border-white/10 pt-3 mt-2 flex justify-between items-center">
                  <span className="text-gray-500 text-[10px] font-mono">Next question loaded in panel</span>
                  <button
                    type="button"
                    onClick={() => setScorecard(null)}
                    className="glow-btn py-1.5 px-3 text-[11px] flex items-center gap-1 cursor-pointer"
                  >
                    Continue <ChevronRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
