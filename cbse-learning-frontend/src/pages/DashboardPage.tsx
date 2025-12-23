import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { curriculumApi, progressApi, recommendationApi, ClassHierarchy, ProgressSummary, RecommendationsResponse } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { 
  BookOpen, 
  GraduationCap, 
  Calculator, 
  Target, 
  Clock, 
  TrendingUp,
  ChevronRight,
  LogOut,
  User,
  Lightbulb
} from 'lucide-react';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [hierarchy, setHierarchy] = useState<ClassHierarchy[]>([]);
  const [progress, setProgress] = useState<ProgressSummary | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hierarchyData, progressData, recsData] = await Promise.all([
          curriculumApi.getHierarchy(),
          progressApi.getMyProgress().catch(() => null),
          recommendationApi.getNextSteps().catch(() => null),
        ]);
        setHierarchy(hierarchyData.hierarchy);
        setProgress(progressData);
        setRecommendations(recsData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <GraduationCap className="h-8 w-8 text-indigo-600" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">CBSE Learning Platform</h1>
                <p className="text-sm text-gray-500">Class 10 Mathematics</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <User className="h-4 w-4" />
                <span>{user?.name}</span>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-medium flex items-center gap-2">
                <Target className="h-5 w-5" />
                Progress Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold mb-2">
                {progress?.summary.overall_completion_pct.toFixed(0) || 0}%
              </div>
              <Progress 
                value={progress?.summary.overall_completion_pct || 0} 
                className="h-2 bg-white/20"
              />
              <p className="text-sm mt-2 text-white/80">
                {progress?.summary.completed || 0} chapters completed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-medium flex items-center gap-2">
                <Clock className="h-5 w-5 text-blue-600" />
                Learning Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {Math.round((progress?.summary.total_chapters_started || 0) * 30)} min
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Total time spent learning
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-medium flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                Quiz Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-gray-900">
                {progress?.summary.in_progress || 0}
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Chapters in progress
              </p>
            </CardContent>
          </Card>
        </div>

        {recommendations && recommendations.recommendations.length > 0 && (
          <Card className="mb-8 border-l-4 border-l-amber-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-medium flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-amber-500" />
                Recommended Next Steps
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recommendations.recommendations.slice(0, 3).map((rec, index) => (
                  <div 
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
                    onClick={() => {
                      if (rec.chapter_id) {
                        navigate(`/chapter/${rec.chapter_id}/learn`);
                      }
                    }}
                  >
                    <div>
                      <p className="font-medium text-gray-900">{rec.reason}</p>
                      {rec.chapter_name && (
                        <p className="text-sm text-gray-500">{rec.chapter_name}</p>
                      )}
                    </div>
                    <ChevronRight className="h-5 w-5 text-gray-400" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-gray-900">Your Courses</h2>
          
          {hierarchy.map((classData) => (
            <div key={classData.id} className="space-y-4">
              <div className="flex items-center gap-2">
                <GraduationCap className="h-6 w-6 text-indigo-600" />
                <h3 className="text-xl font-semibold text-gray-900">{classData.name}</h3>
                <Badge variant="secondary">{classData.board}</Badge>
              </div>
              
              {classData.subjects_data?.map((subject) => (
                <div key={subject.id} className="space-y-3">
                  <div className="flex items-center gap-2 ml-4">
                    <Calculator className="h-5 w-5 text-purple-600" />
                    <h4 className="text-lg font-medium text-gray-800">{subject.name}</h4>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ml-8">
                    {subject.chapters_data?.map((chapter) => {
                      const chapterProgress = progress?.progress.find(
                        p => p.chapter_id === chapter.id
                      );
                      
                      return (
                        <Card 
                          key={chapter.id}
                          className="hover:shadow-lg transition-shadow cursor-pointer group"
                          onClick={() => navigate(`/chapter/${chapter.id}/learn`)}
                        >
                          <CardHeader className="pb-2">
                            <div className="flex items-start justify-between">
                              <div>
                                <CardTitle className="text-base group-hover:text-indigo-600 transition-colors">
                                  Chapter {chapter.number}: {chapter.name}
                                </CardTitle>
                                <CardDescription className="mt-1 line-clamp-2">
                                  {chapter.description}
                                </CardDescription>
                              </div>
                              <BookOpen className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" />
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-gray-500">Progress</span>
                                <span className="font-medium">
                                  {chapterProgress?.progress_pct.toFixed(0) || 0}%
                                </span>
                              </div>
                              <Progress 
                                value={chapterProgress?.progress_pct || 0} 
                                className="h-2"
                              />
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-1 text-sm text-gray-500">
                                  <Clock className="h-4 w-4" />
                                  <span>{chapter.estimated_time_hours}h</span>
                                </div>
                                <Badge 
                                  variant={
                                    chapterProgress?.status === 'completed' ? 'default' :
                                    chapterProgress?.status === 'in_progress' ? 'secondary' :
                                    'outline'
                                  }
                                >
                                  {chapterProgress?.status || 'Not Started'}
                                </Badge>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
