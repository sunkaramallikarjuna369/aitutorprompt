import { useState, useEffect } from 'react';
import { rwalApi, RWALResponse } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { 
  Globe, 
  Briefcase, 
  GraduationCap, 
  Lightbulb,
  Building2,
  Rocket,
  TreePine
} from 'lucide-react';

interface RealWorldPanelProps {
  topicId: string;
}

export default function RealWorldPanel({ topicId }: RealWorldPanelProps) {
  const [rwalData, setRwalData] = useState<RWALResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchRWAL = async () => {
      try {
        const data = await rwalApi.getTopicRWAL(topicId);
        setRwalData(data);
      } catch (error) {
        console.error('Failed to fetch RWAL data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchRWAL();
  }, [topicId]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'engineering': return <Building2 className="h-4 w-4" />;
      case 'physics': return <Rocket className="h-4 w-4" />;
      case 'technology': return <Globe className="h-4 w-4" />;
      case 'agriculture': return <TreePine className="h-4 w-4" />;
      case 'business': return <Briefcase className="h-4 w-4" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!rwalData || rwalData.scenarios.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-gray-500">
          No real-world applications available for this topic.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-l-4 border-l-amber-500">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5 text-amber-600" />
          Real-World Applications (SGT)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="scenarios" className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-4">
            <TabsTrigger value="scenarios" className="text-xs">Scenarios</TabsTrigger>
            <TabsTrigger value="daily" className="text-xs">Daily Life</TabsTrigger>
            <TabsTrigger value="careers" className="text-xs">Careers</TabsTrigger>
            <TabsTrigger value="projects" className="text-xs">Projects</TabsTrigger>
          </TabsList>

          <TabsContent value="scenarios" className="space-y-4">
            {rwalData.scenarios.map((scenario) => (
              <div 
                key={scenario.id}
                className="p-4 bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg"
              >
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-white rounded-lg shadow-sm">
                    {getCategoryIcon(scenario.category)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{scenario.title}</h4>
                      <Badge variant="outline" className="text-xs">
                        {scenario.category}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-700">{scenario.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </TabsContent>

          <TabsContent value="daily" className="space-y-3">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-5 w-5 text-yellow-600" />
              <h4 className="font-medium">Daily Life Examples</h4>
            </div>
            <ul className="space-y-2">
              {rwalData.summary.daily_life_examples.map((example, index) => (
                <li 
                  key={index}
                  className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
                >
                  <span className="text-amber-500 font-bold">{index + 1}.</span>
                  <span className="text-sm text-gray-700">{example}</span>
                </li>
              ))}
            </ul>
          </TabsContent>

          <TabsContent value="careers" className="space-y-3">
            <div className="flex items-center gap-2 mb-3">
              <GraduationCap className="h-5 w-5 text-indigo-600" />
              <h4 className="font-medium">Career Connections</h4>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {rwalData.summary.career_links.map((career, index) => (
                <div 
                  key={index}
                  className="p-3 bg-indigo-50 rounded-lg text-center"
                >
                  <Briefcase className="h-5 w-5 text-indigo-600 mx-auto mb-1" />
                  <span className="text-sm font-medium text-indigo-900">{career}</span>
                </div>
              ))}
            </div>
            <div className="mt-4">
              <h5 className="font-medium text-sm mb-2">Industry Use Cases</h5>
              <ul className="space-y-2">
                {rwalData.summary.industry_use_cases.slice(0, 3).map((useCase, index) => (
                  <li 
                    key={index}
                    className="text-sm text-gray-600 flex items-start gap-2"
                  >
                    <span className="text-indigo-500">-</span>
                    {useCase}
                  </li>
                ))}
              </ul>
            </div>
          </TabsContent>

          <TabsContent value="projects" className="space-y-3">
            <div className="flex items-center gap-2 mb-3">
              <Rocket className="h-5 w-5 text-purple-600" />
              <h4 className="font-medium">Mini Project Ideas</h4>
            </div>
            <div className="space-y-3">
              {rwalData.summary.mini_project_ideas.map((project, index) => (
                <div 
                  key={index}
                  className="p-4 border border-purple-200 bg-purple-50 rounded-lg"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </div>
                    <p className="text-sm text-gray-700 flex-1">{project}</p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
