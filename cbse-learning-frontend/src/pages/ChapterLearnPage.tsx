import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  curriculumApi, 
  contentApi, 
  progressApi,
  authApi,
  ChapterWithTopics, 
  TopicContent,
  SGTFlow,
  StudentMode
} from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { ScrollArea } from '../components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import QuadraticVisualizer from '../components/learning/QuadraticVisualizer';
import RealWorldPanel from '../components/learning/RealWorldPanel';
import ContentViewer from '../components/learning/ContentViewer';
import StudentModeSelector from '../components/learning/StudentModeSelector';
import { 
  BookOpen, 
  ChevronLeft, 
  ChevronRight,
  GraduationCap,
  Target,
  Clock,
  CheckCircle2,
  PlayCircle,
  FileQuestion,
  Home,
  BarChart3,
  Sparkles
} from 'lucide-react';

export default function ChapterLearnPage() {
  const { chapterId } = useParams<{ chapterId: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [chapter, setChapter] = useState<ChapterWithTopics | null>(null);
  const [sgtFlow, setSgtFlow] = useState<SGTFlow | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<string | null>(null);
  const [topicContent, setTopicContent] = useState<TopicContent | null>(null);
  const [completedTopics, setCompletedTopics] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(true);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [studentMode, setStudentMode] = useState<StudentMode>(user?.student_mode || 'average');

  const handleModeChange = async (mode: StudentMode) => {
    setStudentMode(mode);
    try {
      await authApi.updateProfile({ student_mode: mode });
    } catch (error) {
      console.error('Failed to update student mode:', error);
    }
  };

  useEffect(() => {
    const fetchChapter = async () => {
      if (!chapterId) return;
      try {
        const [chapterData, sgtData] = await Promise.all([
          curriculumApi.getChapter(chapterId),
          contentApi.getSGTFlow(chapterId).catch(() => null),
        ]);
        setChapter(chapterData);
        setSgtFlow(sgtData);
        
        if (chapterData.topics_data && chapterData.topics_data.length > 0) {
          setSelectedTopicId(chapterData.topics_data[0].id);
        }
      } catch (error) {
        console.error('Failed to fetch chapter:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchChapter();
  }, [chapterId]);

  useEffect(() => {
    const fetchTopicContent = async () => {
      if (!selectedTopicId) return;
      try {
        const content = await contentApi.getTopicContent(selectedTopicId);
        setTopicContent(content);
        setStartTime(Date.now());
      } catch (error) {
        console.error('Failed to fetch topic content:', error);
      }
    };
    fetchTopicContent();
  }, [selectedTopicId]);

  const handleTopicComplete = async () => {
    if (!selectedTopicId || !chapterId || !topicContent) return;
    
    const timeSpent = Math.round((Date.now() - startTime) / 60000);
    
    try {
      await progressApi.recordTopicViewed(chapterId, {
        topic_id: selectedTopicId,
        time_spent_minutes: Math.max(1, timeSpent),
        content_blocks_viewed: topicContent.content_blocks.map(b => b.id),
      });
      
      setCompletedTopics(prev => new Set([...prev, selectedTopicId]));
      
      const currentIndex = chapter?.topics_data?.findIndex(t => t.id === selectedTopicId) ?? -1;
      if (currentIndex >= 0 && chapter?.topics_data && currentIndex < chapter.topics_data.length - 1) {
        setSelectedTopicId(chapter.topics_data[currentIndex + 1].id);
      }
    } catch (error) {
      console.error('Failed to record progress:', error);
    }
  };

  const navigateToTopic = (direction: 'prev' | 'next') => {
    if (!chapter?.topics_data || !selectedTopicId) return;
    const currentIndex = chapter.topics_data.findIndex(t => t.id === selectedTopicId);
    const newIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex >= 0 && newIndex < chapter.topics_data.length) {
      setSelectedTopicId(chapter.topics_data[newIndex].id);
    }
  };

  const progressPercentage = chapter?.topics_data 
    ? (completedTopics.size / chapter.topics_data.length) * 100 
    : 0;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading chapter content...</p>
        </div>
      </div>
    );
  }

  if (!chapter) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="pt-6 text-center">
            <p className="text-gray-600">Chapter not found</p>
            <Button className="mt-4" onClick={() => navigate('/dashboard')}>
              Return to Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentTopicIndex = chapter.topics_data?.findIndex(t => t.id === selectedTopicId) ?? 0;
  const currentTopic = chapter.topics_data?.find(t => t.id === selectedTopicId);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')}>
                <Home className="h-4 w-4 mr-2" />
                Dashboard
              </Button>
              <div className="h-6 w-px bg-gray-200" />
              <div>
                <h1 className="text-lg font-bold text-gray-900">
                  Chapter {chapter.number}: {chapter.name}
                </h1>
                <p className="text-sm text-gray-500">
                  {currentTopic?.name || 'Select a topic'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Progress value={progressPercentage} className="w-32 h-2" />
                <span className="text-sm text-gray-600">
                  {progressPercentage.toFixed(0)}%
                </span>
              </div>
              <Button onClick={() => navigate(`/chapter/${chapterId}/quiz`)}>
                <FileQuestion className="h-4 w-4 mr-2" />
                Take Quiz
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex h-[calc(100vh-64px)]">
        <aside className="w-72 bg-white border-r overflow-hidden flex flex-col">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-indigo-600" />
              Topics
            </h2>
          </div>
          <ScrollArea className="flex-1">
            <div className="p-2 space-y-1">
              {chapter.topics_data?.map((topic, index) => (
                <button
                  key={topic.id}
                  onClick={() => setSelectedTopicId(topic.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedTopicId === topic.id
                      ? 'bg-indigo-50 border border-indigo-200'
                      : 'hover:bg-gray-50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                      completedTopics.has(topic.id)
                        ? 'bg-green-100 text-green-700'
                        : selectedTopicId === topic.id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {completedTopics.has(topic.id) ? (
                        <CheckCircle2 className="h-4 w-4" />
                      ) : (
                        index + 1
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`font-medium text-sm truncate ${
                        selectedTopicId === topic.id ? 'text-indigo-900' : 'text-gray-900'
                      }`}>
                        {topic.name}
                      </p>
                      <div className="flex items-center gap-2 mt-1">
                        <Clock className="h-3 w-3 text-gray-400" />
                        <span className="text-xs text-gray-500">
                          {topic.estimated_time_minutes} min
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </ScrollArea>
          <div className="p-4 border-t bg-gray-50">
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => navigate('/reports')}
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              View Reports
            </Button>
          </div>
        </aside>

        <main className="flex-1 overflow-auto">
          <div className="max-w-4xl mx-auto p-6 space-y-6">
            {sgtFlow && currentTopicIndex === 0 && (
              <Card className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
                <CardContent className="py-6">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-white/20 rounded-lg">
                      <PlayCircle className="h-8 w-8" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold mb-2">
                        Welcome to {chapter.name}!
                      </h3>
                      <p className="text-white/90">
                        Imagine you're designing the arc of a bridge or calculating the path of a thrown ball. 
                        These real-world problems can be solved using quadratic equations! Let's explore how 
                        mathematics connects to the world around us.
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {currentTopic && (
              <>
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{currentTopic.name}</h2>
                    <p className="text-gray-600 mt-1">{currentTopic.description}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {currentTopic.tags?.map((tag) => (
                      <Badge key={tag} variant="secondary">{tag}</Badge>
                    ))}
                  </div>
                </div>

                {currentTopic.learning_objectives && currentTopic.learning_objectives.length > 0 && (
                  <Card>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base flex items-center gap-2">
                        <Target className="h-5 w-5 text-green-600" />
                        Learning Objectives
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {currentTopic.learning_objectives.map((obj) => (
                          <li key={obj.id} className="flex items-start gap-2">
                            <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5" />
                            <div>
                              <span className="text-gray-700">{obj.description}</span>
                              <Badge variant="outline" className="ml-2 text-xs">
                                {obj.bloom_level}
                              </Badge>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                )}

                <Tabs defaultValue="content" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="content">Content</TabsTrigger>
                    <TabsTrigger value="visualize">Interactive</TabsTrigger>
                    <TabsTrigger value="realworld">Real-World (SGT)</TabsTrigger>
                  </TabsList>

                  <TabsContent value="content" className="mt-4">
                    {topicContent && topicContent.content_blocks.length > 0 ? (
                      <ContentViewer 
                        blocks={topicContent.content_blocks} 
                        title={currentTopic.name}
                      />
                    ) : (
                      <Card>
                        <CardContent className="py-8 text-center text-gray-500">
                          No content available for this topic yet.
                        </CardContent>
                      </Card>
                    )}
                  </TabsContent>

                  <TabsContent value="visualize" className="mt-4">
                    <QuadraticVisualizer 
                      studentMode={studentMode} 
                      topicId={selectedTopicId || 'qe-graphical'} 
                    />
                  </TabsContent>

                  <TabsContent value="realworld" className="mt-4">
                    <RealWorldPanel topicId={selectedTopicId || ''} />
                  </TabsContent>
                </Tabs>

                <div className="flex items-center justify-between pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => navigateToTopic('prev')}
                    disabled={currentTopicIndex === 0}
                  >
                    <ChevronLeft className="h-4 w-4 mr-2" />
                    Previous Topic
                  </Button>

                  <Button
                    onClick={handleTopicComplete}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Mark as Complete
                  </Button>

                  <Button
                    variant="outline"
                    onClick={() => navigateToTopic('next')}
                    disabled={currentTopicIndex === (chapter.topics_data?.length ?? 0) - 1}
                  >
                    Next Topic
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </>
            )}
          </div>
        </main>

        <aside className="w-72 bg-white border-l overflow-hidden flex flex-col">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-600" />
              Learning Mode
            </h2>
          </div>
          <div className="p-4 border-b">
            <StudentModeSelector 
              currentMode={studentMode} 
              onModeChange={handleModeChange}
              compact={true}
            />
            <p className="text-xs text-gray-500 mt-2">
              {studentMode === 'dull' && 'Simplified visuals with real-world metaphors'}
              {studentMode === 'average' && 'Balanced procedural visualizations'}
              {studentMode === 'clever' && 'Complex abstract visualizations'}
            </p>
          </div>
          <div className="p-4 border-b">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-indigo-600" />
              Your Progress
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Chapter Progress</span>
                <span className="font-medium">{progressPercentage.toFixed(0)}%</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>

            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                <Clock className="h-4 w-4" />
                <span>Estimated Time</span>
              </div>
              <p className="font-semibold text-gray-900">
                {chapter.estimated_time_hours} hours
              </p>
            </div>

            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 text-sm text-gray-600 mb-1">
                <Target className="h-4 w-4" />
                <span>Topics Completed</span>
              </div>
              <p className="font-semibold text-gray-900">
                {completedTopics.size} / {chapter.topics_data?.length || 0}
              </p>
            </div>

            <div className="pt-4 border-t">
              <h3 className="font-medium text-gray-900 mb-3">Quick Actions</h3>
              <div className="space-y-2">
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate(`/chapter/${chapterId}/quiz?type=formative`)}
                >
                  <FileQuestion className="h-4 w-4 mr-2" />
                  Quick Check (5 questions)
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start"
                  onClick={() => navigate(`/chapter/${chapterId}/quiz?type=summative`)}
                >
                  <Target className="h-4 w-4 mr-2" />
                  Full Quiz (10 questions)
                </Button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
