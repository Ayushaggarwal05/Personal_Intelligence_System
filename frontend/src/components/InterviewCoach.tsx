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
        // Set session parameters for the next pre-generated question
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
    <div style={{ flex: '1', display: 'flex', flexDirection: 'column', height: '100%', padding: '24px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
        <Award size={24} style={{ color: 'var(--accent-purple)' }} />
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Technical Mock Interview Coach</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Adaptive questions based on your codebase symbols</p>
        </div>
      </div>

      {error && (
        <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', borderRadius: '6px', fontSize: '13px', marginBottom: '16px' }}>
          {error}
        </div>
      )}

      {!session ? (
        <div style={{ flex: '1', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
          <Zap size={48} style={{ color: 'var(--accent-purple)', opacity: '0.4', marginBottom: '16px' }} />
          <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Start Mock Interview Session</h3>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', maxWidth: '400px', marginBottom: '24px' }}>
            Answer system questions generated dynamically from your code class schemas, routes, and functional dependencies.
          </p>
          <button onClick={handleStart} disabled={!projectId || isLoading} className="glow-btn">
            {isLoading ? 'Booting Coach...' : 'Launch Interview'}
          </button>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Question panel */}
          <div className="glass-panel" style={{ padding: '16px', borderLeft: '4px solid var(--accent-purple)' }}>
            <span style={{ fontSize: '11px', color: 'var(--accent-cyan)', fontWeight: 'bold', display: 'block', marginBottom: '6px' }}>
              FOCUS AREA: {session.focus_area.toUpperCase()}
            </span>
            <span style={{ fontSize: '15px', fontWeight: '500', color: '#fff', lineHeight: '1.6' }}>
              {session.question}
            </span>
          </div>

          {/* Submission form */}
          <form onSubmit={handleSubmitAnswer} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <textarea
              placeholder="Draft your explanation answer here in detail..."
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              disabled={isLoading}
              style={{
                width: '100%',
                height: '120px',
                background: 'rgba(0,0,0,0.2)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '12px',
                color: '#fff',
                fontSize: '13px',
                outline: 'none',
                resize: 'none',
                boxSizing: 'border-box',
                lineHeight: '1.6',
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
              <button type="button" onClick={() => setSession(null)} className="glow-btn" style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                Quit
              </button>
              <button type="submit" disabled={isLoading || !userAnswer.trim()} className="glow-btn">
                {isLoading ? 'Grading Answer...' : 'Submit Answer'}
              </button>
            </div>
          </form>

          {/* Scorecard Results Overlay */}
          {scorecard && (
            <div className="glass-panel animate-fade-in" style={{ padding: '20px', marginTop: '12px', borderLeft: '4px solid var(--accent-cyan)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 'bold', fontSize: '15px' }}>
                  <CheckCircle size={18} style={{ color: 'var(--accent-cyan)' }} />
                  Evaluation Scorecard
                </span>
                <span style={{ fontSize: '24px', fontWeight: '800', color: 'var(--accent-cyan)' }}>
                  {scorecard.score}/100
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)', fontWeight: '600', display: 'block', marginBottom: '4px' }}>Suggestions:</span>
                  <p style={{ color: 'var(--text-primary)', margin: 0 }}>{scorecard.suggestions}</p>
                </div>

                {scorecard.model_answer && (
                  <div>
                    <span style={{ color: 'var(--text-secondary)', fontWeight: '600', display: 'block', marginBottom: '4px' }}>Model Answer Key:</span>
                    <p style={{ color: 'var(--text-secondary)', margin: 0, fontStyle: 'italic' }}>{scorecard.model_answer}</p>
                  </div>
                )}

                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '12px', marginTop: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Next question loaded in panel</span>
                  <button type="button" onClick={() => setScorecard(null)} className="glow-btn" style={{ padding: '6px 12px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '4px' }}>
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
