import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { progressApi, recommendationApi, UserProgressSummary, ReviewPlan, LearningPath } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';
import { 
  Home, 
  TrendingUp, 
  Clock, 
  Target, 
  Brain,
  BookOpen,
  Award,
  Calendar,
  ChevronRight,
  Lightbulb,
  GraduationCap
} from 'lucide-react';

export default function ReportsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [summary, setSummary] = useState<UserProgressSummary | null>(null);
  const [reviewPlan, setReviewPlan] = useState<ReviewPlan | null>(null);
  const [learningPath, setLearningPath] = useState<LearningPath | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryData, reviewData, pathData] = await Promise.all([
          progressApi.getSummary().catch(() => null),
          recommendationApi.getReviewPlan().catch(() => null),
          recommendationApi.getLearningPath().catch(() => null),
        ]);
        setSummary(summaryData);
        setReviewPlan(reviewData);
        setLearningPath(pathData);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);


  const bloomData = [
    { name: 'Remember', value: 85, color: '#3b82f6' },
    { name: 'Understand', value: 78, color: '#10b981' },
    { name: 'Apply', value: 65, color: '#f59e0b' },
    { name: 'Analyze', value: 55, color: '#f97316' },
    { name: 'Evaluate', value: 45, color: '#ef4444' },
    { name: 'Create', value: 30, color: '#8b5cf6' },
  ];

  const weeklyProgress = [
    { day: 'Mon', minutes: 30, quizzes: 2 },
    { day: 'Tue', minutes: 45, quizzes: 1 },
    { day: 'Wed', minutes: 20, quizzes: 0 },
    { day: 'Thu', minutes: 60, quizzes: 3 },
    { day: 'Fri', minutes: 35, quizzes: 1 },
    { day: 'Sat', minutes: 50, quizzes: 2 },
    { day: 'Sun', minutes: 25, quizzes: 1 },
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your reports...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
                <Home className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
              <div className="h-6 w-px bg-gray-200" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Learning Reports</h1>
                <p className="text-sm text-gray-500">Track your progress and performance</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-indigo-600" />
              <span className="font-medium">{user?.name}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <BookOpen className="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {summary?.summary.chapters_completed || 0}
                  </p>
                  <p className="text-sm text-gray-500">Chapters Completed</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Clock className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {summary?.summary.total_time_spent_minutes || 0}m
                  </p>
                  <p className="text-sm text-gray-500">Time Spent Learning</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-amber-100 rounded-lg">
                  <Target className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {summary?.summary.total_quizzes_taken || 0}
                  </p>
                  <p className="text-sm text-gray-500">Quizzes Taken</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Award className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {summary?.summary.average_quiz_score?.toFixed(0) || 0}%
                  </p>
                  <p className="text-sm text-gray-500">Average Quiz Score</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="bloom">Bloom's Taxonomy</TabsTrigger>
            <TabsTrigger value="activity">Activity</TabsTrigger>
            <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-indigo-600" />
                    Learning Progress
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {learningPath?.learning_path && learningPath.learning_path.length > 0 ? (
                      (learningPath.learning_path as { chapter_name: string; progress_pct: number; status: string }[]).map((item, index) => (
                        <div key={index} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{item.chapter_name}</span>
                            <Badge variant={item.status === 'completed' ? 'default' : 'secondary'}>
                              {item.status}
                            </Badge>
                          </div>
                          <Progress value={item.progress_pct} className="h-2" />
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <BookOpen className="h-12 w-12 mx-auto mb-2 opacity-50" />
                        <p>Start learning to see your progress here!</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    Learning Profile
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Learning Style</p>
                      <p className="font-semibold capitalize">
                        {summary?.learning_profile.learning_style || user?.learning_style || 'Visual'}
                      </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Learning Pace</p>
                      <p className="font-semibold capitalize">
                        {summary?.learning_profile.pace || user?.pace || 'Normal'}
                      </p>
                    </div>
                    {summary?.learning_profile.top_strengths && summary.learning_profile.top_strengths.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-2">Top Strengths</p>
                        <div className="flex flex-wrap gap-2">
                          {summary.learning_profile.top_strengths.map((strength, idx) => (
                            <Badge key={idx} variant="secondary" className="bg-green-100 text-green-800">
                              {strength}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    {summary?.learning_profile.areas_to_improve && summary.learning_profile.areas_to_improve.length > 0 && (
                      <div>
                        <p className="text-sm text-gray-600 mb-2">Areas to Improve</p>
                        <div className="flex flex-wrap gap-2">
                          {summary.learning_profile.areas_to_improve.map((area, idx) => (
                            <Badge key={idx} variant="secondary" className="bg-amber-100 text-amber-800">
                              {area}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="bloom" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-purple-600" />
                  Bloom's Taxonomy Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={bloomData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" domain={[0, 100]} />
                        <YAxis dataKey="name" type="category" width={80} />
                        <Tooltip formatter={(value) => [`${value}%`, 'Score']} />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {bloomData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-semibold">Understanding Bloom's Levels</h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex items-start gap-3">
                        <Badge className="bg-blue-100 text-blue-800">Remember</Badge>
                        <p className="text-gray-600">Recall facts and basic concepts</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <Badge className="bg-green-100 text-green-800">Understand</Badge>
                        <p className="text-gray-600">Explain ideas or concepts</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <Badge className="bg-yellow-100 text-yellow-800">Apply</Badge>
                        <p className="text-gray-600">Use information in new situations</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <Badge className="bg-orange-100 text-orange-800">Analyze</Badge>
                        <p className="text-gray-600">Draw connections among ideas</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <Badge className="bg-red-100 text-red-800">Evaluate</Badge>
                        <p className="text-gray-600">Justify a decision or course of action</p>
                      </div>
                      <div className="flex items-start gap-3">
                        <Badge className="bg-purple-100 text-purple-800">Create</Badge>
                        <p className="text-gray-600">Produce new or original work</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activity" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-blue-600" />
                  Weekly Activity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={weeklyProgress}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line 
                        yAxisId="left"
                        type="monotone" 
                        dataKey="minutes" 
                        stroke="#4f46e5" 
                        strokeWidth={2}
                        name="Minutes Studied"
                      />
                      <Line 
                        yAxisId="right"
                        type="monotone" 
                        dataKey="quizzes" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        name="Quizzes Taken"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="recommendations" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Lightbulb className="h-5 w-5 text-amber-600" />
                    Review Plan
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {reviewPlan?.review_plan.items_needing_review && 
                   reviewPlan.review_plan.items_needing_review.length > 0 ? (
                    <div className="space-y-3">
                      {(reviewPlan.review_plan.items_needing_review as { topic_name: string; reason: string }[]).map((item, idx) => (
                        <div 
                          key={idx}
                          className="p-3 bg-amber-50 rounded-lg flex items-center justify-between"
                        >
                          <div>
                            <p className="font-medium">{item.topic_name}</p>
                            <p className="text-sm text-gray-600">{item.reason}</p>
                          </div>
                          <ChevronRight className="h-5 w-5 text-gray-400" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <Target className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No items need review right now!</p>
                    </div>
                  )}
                  
                  {reviewPlan?.spaced_repetition_info && (
                    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Spaced Repetition Schedule
                      </p>
                      <p className="text-xs text-gray-500">
                        Method: {reviewPlan.spaced_repetition_info.method}
                      </p>
                      <div className="flex flex-wrap gap-1 mt-2">
                        {reviewPlan.spaced_repetition_info.intervals.map((interval, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {interval}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-green-600" />
                    Next Steps
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div 
                      className="p-4 bg-indigo-50 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors"
                      onClick={() => navigate('/chapter/quadratic-equations/learn')}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-indigo-900">Continue Learning</p>
                          <p className="text-sm text-indigo-700">Quadratic Equations</p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-indigo-400" />
                      </div>
                    </div>
                    <div 
                      className="p-4 bg-green-50 rounded-lg cursor-pointer hover:bg-green-100 transition-colors"
                      onClick={() => navigate('/chapter/quadratic-equations/quiz?type=formative')}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-green-900">Quick Practice Quiz</p>
                          <p className="text-sm text-green-700">5 questions to test your knowledge</p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-green-400" />
                      </div>
                    </div>
                    <div 
                      className="p-4 bg-purple-50 rounded-lg cursor-pointer hover:bg-purple-100 transition-colors"
                      onClick={() => navigate('/chapter/quadratic-equations/quiz?type=summative')}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-purple-900">Full Assessment</p>
                          <p className="text-sm text-purple-700">Adaptive quiz with 10 questions</p>
                        </div>
                        <ChevronRight className="h-5 w-5 text-purple-400" />
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
