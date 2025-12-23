import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { quizApi, curriculumApi, QuizStart, Question, AnswerResponse, QuizReport } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { Slider } from '../components/ui/slider';
import { 
  Clock, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  ChevronRight,
  Home,
  Trophy,
  Target,
  Brain,
  Lightbulb,
  BarChart3
} from 'lucide-react';

export default function QuizPage() {
  const { chapterId } = useParams<{ chapterId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [quizSession, setQuizSession] = useState<QuizStart | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string>('');
  const [confidence, setConfidence] = useState(3);
  const [answerResult, setAnswerResult] = useState<AnswerResponse | null>(null);
  const [quizReport, setQuizReport] = useState<QuizReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [chapterName, setChapterName] = useState('');
  
  const startTimeRef = useRef<number>(Date.now());

  const quizType = searchParams.get('type') || 'summative';
  const questionCount = quizType === 'formative' ? 5 : 10;

  useEffect(() => {
    const startQuiz = async () => {
      if (!chapterId) return;
      try {
        const [quiz, chapter] = await Promise.all([
          quizApi.startQuiz(chapterId, { quiz_type: quizType, question_count: questionCount }),
          curriculumApi.getChapter(chapterId),
        ]);
        setQuizSession(quiz);
        setCurrentQuestion(quiz.current_question);
        setCurrentIndex(quiz.current_index);
        setTimeRemaining(quiz.time_limit_seconds);
        setChapterName(chapter.name);
        startTimeRef.current = Date.now();
      } catch (error) {
        console.error('Failed to start quiz:', error);
      } finally {
        setIsLoading(false);
      }
    };
    startQuiz();
  }, [chapterId, quizType, questionCount]);

  useEffect(() => {
    if (!currentQuestion || answerResult || quizReport) return;
    
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleSubmitAnswer();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [currentQuestion, answerResult, quizReport]);

  const handleSubmitAnswer = async () => {
    if (!quizSession || !currentQuestion || isSubmitting) return;
    
    setIsSubmitting(true);
    const responseTime = Date.now() - startTimeRef.current;
    
    try {
      const result = await quizApi.submitAnswer(quizSession.session_id, {
        question_id: currentQuestion.id,
        answer: selectedAnswer || 'no_answer',
        confidence_level: confidence,
        response_time_ms: responseTime,
      });
      
      setAnswerResult(result);
      
      if (result.quiz_completed) {
        const report = await quizApi.getReport(quizSession.session_id);
        setQuizReport(report);
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNextQuestion = () => {
    if (!answerResult?.next_question) return;
    
    setCurrentQuestion(answerResult.next_question);
    setCurrentIndex(answerResult.current_index || currentIndex + 1);
    setTimeRemaining(answerResult.time_limit_seconds || 60);
    setSelectedAnswer('');
    setConfidence(3);
    setAnswerResult(null);
    startTimeRef.current = Date.now();
  };

  const getBloomLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      remember: 'bg-blue-100 text-blue-800',
      understand: 'bg-green-100 text-green-800',
      apply: 'bg-yellow-100 text-yellow-800',
      analyze: 'bg-orange-100 text-orange-800',
      evaluate: 'bg-red-100 text-red-800',
      create: 'bg-purple-100 text-purple-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Preparing your quiz...</p>
        </div>
      </div>
    );
  }

  if (quizReport) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-3xl mx-auto px-4">
          <Card className="mb-6">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                <Trophy className="h-8 w-8 text-indigo-600" />
              </div>
              <CardTitle className="text-2xl">Quiz Complete!</CardTitle>
              <p className="text-gray-600">{chapterName}</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-indigo-600">
                    {quizReport.score_percentage.toFixed(0)}%
                  </p>
                  <p className="text-sm text-gray-600">Score</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-green-600">
                    {quizReport.correct_answers}/{quizReport.total_questions}
                  </p>
                  <p className="text-sm text-gray-600">Correct</p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <p className="text-3xl font-bold text-blue-600">
                    {Math.round(quizReport.time_taken_seconds / 60)}m
                  </p>
                  <p className="text-sm text-gray-600">Time</p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    Bloom's Taxonomy Performance
                  </h3>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(quizReport.bloom_breakdown).map(([level, data]) => (
                      <div key={level} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <Badge className={getBloomLevelColor(level)}>{level}</Badge>
                        <span className="text-sm font-medium">
                          {data.correct}/{data.total} ({data.percentage.toFixed(0)}%)
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {quizReport.strengths.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                      Strengths
                    </h3>
                    <ul className="space-y-1">
                      {quizReport.strengths.map((strength, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-green-500">+</span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {quizReport.weaknesses.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <Target className="h-5 w-5 text-orange-600" />
                      Areas to Improve
                    </h3>
                    <ul className="space-y-1">
                      {quizReport.weaknesses.map((weakness, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-orange-500">-</span>
                          {weakness}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {quizReport.recommendations.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-amber-600" />
                      Recommendations
                    </h3>
                    <ul className="space-y-1">
                      {quizReport.recommendations.map((rec, idx) => (
                        <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                          <span className="text-amber-500">*</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t">
                <Button variant="outline" onClick={() => navigate('/dashboard')} className="flex-1">
                  <Home className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
                <Button variant="outline" onClick={() => navigate(`/chapter/${chapterId}/learn`)} className="flex-1">
                  Continue Learning
                </Button>
                <Button onClick={() => navigate('/reports')} className="flex-1">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  View Reports
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-gray-600">No questions available</p>
            <Button className="mt-4" onClick={() => navigate('/dashboard')}>
              Return to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-lg font-bold text-gray-900">{chapterName} Quiz</h1>
              <p className="text-sm text-gray-500">
                {quizType === 'formative' ? 'Quick Check' : 'Adaptive Assessment'}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${
                timeRemaining < 10 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'
              }`}>
                <Clock className="h-4 w-4" />
                <span className="font-mono font-medium">{formatTime(timeRemaining)}</span>
              </div>
              <Badge variant="outline">
                Question {currentIndex + 1} of {quizSession?.total_questions}
              </Badge>
            </div>
          </div>
          <Progress 
            value={((currentIndex + 1) / (quizSession?.total_questions || 1)) * 100} 
            className="h-1 mt-3"
          />
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between mb-2">
              <Badge className={getBloomLevelColor(currentQuestion.bloom_level)}>
                {currentQuestion.bloom_level}
              </Badge>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span>Difficulty: {currentQuestion.difficulty}/5</span>
                <span>|</span>
                <span>{currentQuestion.points} points</span>
              </div>
            </div>
            <CardTitle className="text-xl leading-relaxed">
              {currentQuestion.question_text}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {answerResult ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg ${
                  answerResult.is_correct 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    {answerResult.is_correct ? (
                      <>
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                        <span className="font-semibold text-green-800">Correct!</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-5 w-5 text-red-600" />
                        <span className="font-semibold text-red-800">Incorrect</span>
                      </>
                    )}
                    <span className="ml-auto text-sm">
                      +{answerResult.points_earned} points
                    </span>
                  </div>
                  {!answerResult.is_correct && (
                    <p className="text-sm text-gray-700 mb-2">
                      <span className="font-medium">Correct answer:</span> {answerResult.correct_answer}
                    </p>
                  )}
                  <p className="text-sm text-gray-700">{answerResult.explanation}</p>
                </div>

                <div className="flex items-center justify-between pt-4">
                  <div className="text-sm text-gray-600">
                    Current Score: <span className="font-bold">{answerResult.current_score}</span>
                  </div>
                  {answerResult.next_question ? (
                    <Button onClick={handleNextQuestion}>
                      Next Question
                      <ChevronRight className="h-4 w-4 ml-2" />
                    </Button>
                  ) : (
                    <Button onClick={() => quizApi.finishQuiz(quizSession!.session_id).then(setQuizReport)}>
                      View Results
                    </Button>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {currentQuestion.options && currentQuestion.options.length > 0 ? (
                  <RadioGroup value={selectedAnswer} onValueChange={setSelectedAnswer}>
                    <div className="space-y-3">
                      {currentQuestion.options.map((option) => (
                        <div
                          key={option.id}
                          className={`flex items-center space-x-3 p-4 rounded-lg border transition-colors cursor-pointer ${
                            selectedAnswer === option.id
                              ? 'border-indigo-500 bg-indigo-50'
                              : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                          }`}
                          onClick={() => setSelectedAnswer(option.id)}
                        >
                          <RadioGroupItem value={option.id} id={option.id} />
                          <Label htmlFor={option.id} className="flex-1 cursor-pointer">
                            {option.text}
                          </Label>
                        </div>
                      ))}
                    </div>
                  </RadioGroup>
                ) : (
                  <div className="p-4 bg-gray-50 rounded-lg text-center text-gray-500">
                    <AlertCircle className="h-8 w-8 mx-auto mb-2" />
                    <p>This question requires a written response.</p>
                  </div>
                )}

                <div className="pt-4 border-t">
                  <div className="flex items-center justify-between mb-2">
                    <Label className="text-sm font-medium">
                      How confident are you? (1-5)
                    </Label>
                    <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                      {confidence}
                    </span>
                  </div>
                  <Slider
                    min={1}
                    max={5}
                    step={1}
                    value={[confidence]}
                    onValueChange={([val]) => setConfidence(val)}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>Not sure</span>
                    <span>Very confident</span>
                  </div>
                </div>

                {currentQuestion.hint && (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
                    <div className="flex items-center gap-2 text-amber-800">
                      <Lightbulb className="h-4 w-4" />
                      <span className="text-sm font-medium">Hint:</span>
                    </div>
                    <p className="text-sm text-amber-700 mt-1">{currentQuestion.hint}</p>
                  </div>
                )}

                <div className="flex justify-end pt-4">
                  <Button 
                    onClick={handleSubmitAnswer} 
                    disabled={!selectedAnswer || isSubmitting}
                    size="lg"
                  >
                    {isSubmitting ? 'Submitting...' : 'Submit Answer'}
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
