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
    <div
      className="flex-1 flex flex-col h-full p-6 overflow-y-auto animate-fade-in"
      style={{ background: 'transparent' }}
    >
      <div className="flex items-center gap-3 mb-6 select-none">
        <div
          className="w-9 h-9 rounded-xl flex items-center justify-center"
          style={{
            background: 'linear-gradient(135deg, var(--accent) 0%, var(--sage) 100%)',
            boxShadow: '0 4px 12px rgba(77,124,115,.12)',
          }}
        >
          <Award size={16} style={{ color: 'var(--bg-card)' }} />
        </div>
        <div>
          <h2
            className="font-heading font-bold tracking-tight text-txtPrimary"
            style={{ fontSize: 14 }}
          >
            Technical Mock Interview Coach
          </h2>
          <p
            className="font-mono text-txtMuted mt-0.5"
            style={{ fontSize: 9, letterSpacing: '0.02em' }}
          >
            Adaptive questions based on your codebase symbols
          </p>
        </div>
      </div>

      {error && (
        <div
          className="p-3 border text-xs mb-4 rounded-xl"
          style={{
            background: 'rgba(239, 68, 68, 0.06)',
            borderColor: 'rgba(239, 68, 68, 0.15)',
            color: '#ef4444',
            fontFamily: 'JetBrains Mono, monospace',
          }}
        >
          {error}
        </div>
      )}

      {!session ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center py-20 select-none">
          <Zap size={44} style={{ color: 'var(--accent)', opacity: 0.6, marginBottom: 16 }} className="animate-pulse" />
          <h3
            className="font-heading font-bold text-txtPrimary mb-2"
            style={{ fontSize: 15 }}
          >
            Start Mock Interview Session
          </h3>
          <p
            className="text-txtMuted max-w-[400px] mb-6 leading-relaxed"
            style={{ fontSize: 12 }}
          >
            Answer system questions generated dynamically from your code class schemas, routes, and functional dependencies.
          </p>
          <button
            onClick={handleStart}
            disabled={!projectId || isLoading}
            className="asta-btn-premium font-heading font-semibold"
            style={{
              padding: '12px 24px',
              borderRadius: 12,
              background: (!projectId || isLoading) ? 'transparent' : 'var(--accent)',
              color: (!projectId || isLoading) ? 'var(--txt-disabled)' : '#F4F6F5',
              cursor: (!projectId || isLoading) ? 'not-allowed' : 'pointer',
              border: 'none',
              transition: 'all 200ms ease',
            }}
          >
            {isLoading ? 'Booting Coach...' : 'Launch Interview'}
          </button>
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          {/* Question panel */}
          <div
            className="p-4 rounded-r-lg border border-white/5"
            style={{
              background: 'var(--bg-card)',
              borderLeft: '4px solid var(--accent)',
            }}
          >
            <span
              className="text-[10px] font-bold block mb-1.5 font-mono uppercase"
              style={{ color: 'var(--sage)' }}
            >
              Focus Area: {isLoading ? 'Evaluating & Generating...' : session.focus_area}
            </span>
            {isLoading ? (
              <div className="flex flex-col gap-2 mt-2">
                <div className="h-4 bg-white/10 rounded w-11/12 animate-pulse" />
                <div className="h-4 bg-white/10 rounded w-8/12 animate-pulse" />
              </div>
            ) : (
              <span className="text-sm font-medium text-white leading-relaxed">
                {session.question}
              </span>
            )}
          </div>

          {/* Submission form */}
          <form onSubmit={handleSubmitAnswer} className="flex flex-col gap-3">
            <textarea
              placeholder="Draft your explanation answer here in detail..."
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              disabled={isLoading}
              className="w-full h-32 rounded-lg p-3 text-xs text-white outline-none resize-none box-border leading-relaxed transition-all"
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'rgba(77, 124, 115, 0.3)';
                e.target.style.background = 'rgba(255, 255, 255, 0.03)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.05)';
                e.target.style.background = 'rgba(255, 255, 255, 0.02)';
              }}
            />
            <div className="flex justify-end gap-3 select-none">
              <button
                type="button"
                onClick={() => setSession(null)}
                className="px-4 py-2 text-xs rounded border bg-transparent text-txtMuted hover:text-white transition-all cursor-pointer"
                style={{
                  borderColor: 'rgba(255, 255, 255, 0.05)',
                  borderRadius: 10,
                }}
              >
                Quit
              </button>
              <button
                type="submit"
                disabled={isLoading || !userAnswer.trim()}
                className="font-heading font-semibold"
                style={{
                  padding: '8px 16px',
                  borderRadius: 10,
                  fontSize: 12,
                  background: (isLoading || !userAnswer.trim()) ? 'transparent' : 'var(--accent)',
                  color: (isLoading || !userAnswer.trim()) ? 'var(--txt-disabled)' : '#F4F6F5',
                  cursor: (isLoading || !userAnswer.trim()) ? 'not-allowed' : 'pointer',
                  border: 'none',
                  transition: 'all 200ms ease',
                }}
              >
                {isLoading ? 'Grading Answer...' : 'Submit Answer'}
              </button>
            </div>
          </form>

          {/* Scorecard Results Overlay */}
          {scorecard && (
            <div
              className="p-5 mt-4 rounded-r-lg border border-white/5 animate-fade-in"
              style={{
                background: 'rgba(26, 33, 30, 0.45)',
                borderLeft: '4px solid var(--sage)',
              }}
            >
              <div className="flex justify-between items-center mb-4">
                <span className="flex items-center gap-1.5 font-bold text-sm text-gray-100 font-heading">
                  <CheckCircle size={18} style={{ color: 'var(--sage)' }} />
                  Evaluation Scorecard
                </span>
                <span
                  className="text-2xl font-extrabold font-heading"
                  style={{ color: 'var(--sage)' }}
                >
                  {scorecard.score}/100
                </span>
              </div>

              <div className="flex flex-col gap-3 text-xs">
                <div>
                  <span className="text-gray-400 font-semibold block mb-1 text-[11px] font-heading">Suggestions:</span>
                  <p className="text-gray-200 m-0 leading-relaxed">{scorecard.suggestions}</p>
                </div>

                {scorecard.model_answer && (
                  <div>
                    <span className="text-gray-400 font-semibold block mb-1 text-[11px] font-heading">Model Answer Key:</span>
                    <p className="text-gray-400 m-0 italic leading-relaxed">{scorecard.model_answer}</p>
                  </div>
                )}

                <div className="border-t border-white/10 pt-3 mt-2 flex justify-between items-center select-none">
                  <span className="text-gray-500 text-[10px] font-mono">Next question loaded in panel</span>
                  <button
                    type="button"
                    onClick={() => setScorecard(null)}
                    className="font-heading font-semibold flex items-center gap-1 cursor-pointer"
                    style={{
                      padding: '6px 12px',
                      borderRadius: 8,
                      fontSize: 11.5,
                      background: 'var(--accent)',
                      color: '#F4F6F5',
                      border: 'none',
                      transition: 'all 200ms ease',
                    }}
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
