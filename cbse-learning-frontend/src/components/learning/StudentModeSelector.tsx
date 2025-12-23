import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { visualizationOrchestratorApi, StudentMode, StudentModeInfo } from '@/lib/api';
import { Sparkles, BookOpen, Rocket, Check } from 'lucide-react';

interface StudentModeSelectorProps {
  currentMode: StudentMode;
  onModeChange: (mode: StudentMode) => void;
  compact?: boolean;
}

const modeIcons: Record<StudentMode, React.ReactNode> = {
  dull: <BookOpen className="h-5 w-5" />,
  average: <Sparkles className="h-5 w-5" />,
  clever: <Rocket className="h-5 w-5" />,
};

const modeColors: Record<StudentMode, string> = {
  dull: 'bg-amber-100 border-amber-300 hover:bg-amber-200',
  average: 'bg-blue-100 border-blue-300 hover:bg-blue-200',
  clever: 'bg-purple-100 border-purple-300 hover:bg-purple-200',
};

const modeSelectedColors: Record<StudentMode, string> = {
  dull: 'bg-amber-500 border-amber-600 text-white',
  average: 'bg-blue-500 border-blue-600 text-white',
  clever: 'bg-purple-500 border-purple-600 text-white',
};

export function StudentModeSelector({ currentMode, onModeChange, compact = false }: StudentModeSelectorProps) {
  const [modes, setModes] = useState<StudentModeInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModes = async () => {
      try {
        const response = await visualizationOrchestratorApi.getModes();
        setModes(response.modes);
      } catch (error) {
        console.error('Failed to fetch modes:', error);
        setModes([
          {
            id: 'dull',
            name: 'Supportive Learning',
            description: 'Simplified visualizations with real-world metaphors',
            features: ['High-contrast colors', 'Real-world metaphors', 'Step-by-step guidance'],
            recommended_for: 'Students who need extra support',
          },
          {
            id: 'average',
            name: 'Balanced Learning',
            description: 'Procedural visualizations focusing on mathematical relationships',
            features: ['Standard color coding', 'Discriminant visualization', 'Medium scaffolding'],
            recommended_for: 'Students with foundational understanding',
          },
          {
            id: 'clever',
            name: 'Advanced Exploration',
            description: 'Complex visualizations with abstract concepts',
            features: ['Complex roots', 'Sandbox mode', 'Minimal scaffolding'],
            recommended_for: 'Advanced students seeking challenges',
          },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchModes();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="flex gap-2">
        {modes.map((mode) => (
          <Button
            key={mode.id}
            variant={currentMode === mode.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => onModeChange(mode.id)}
            className={`flex items-center gap-1 ${
              currentMode === mode.id ? modeSelectedColors[mode.id] : ''
            }`}
          >
            {modeIcons[mode.id]}
            <span className="hidden sm:inline">{mode.name}</span>
          </Button>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900">Choose Your Learning Mode</h3>
        <p className="text-sm text-gray-500">Select the mode that best fits your learning style</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {modes.map((mode) => (
          <Card
            key={mode.id}
            className={`cursor-pointer transition-all duration-200 border-2 ${
              currentMode === mode.id
                ? modeSelectedColors[mode.id]
                : modeColors[mode.id]
            }`}
            onClick={() => onModeChange(mode.id)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {modeIcons[mode.id]}
                  <CardTitle className="text-base">{mode.name}</CardTitle>
                </div>
                {currentMode === mode.id && (
                  <Check className="h-5 w-5" />
                )}
              </div>
              <CardDescription className={currentMode === mode.id ? 'text-white/80' : ''}>
                {mode.description}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1">
                  {mode.features.slice(0, 3).map((feature, idx) => (
                    <Badge
                      key={idx}
                      variant={currentMode === mode.id ? 'secondary' : 'outline'}
                      className="text-xs"
                    >
                      {feature}
                    </Badge>
                  ))}
                </div>
                <p className={`text-xs ${currentMode === mode.id ? 'text-white/70' : 'text-gray-500'}`}>
                  {mode.recommended_for}
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default StudentModeSelector;
