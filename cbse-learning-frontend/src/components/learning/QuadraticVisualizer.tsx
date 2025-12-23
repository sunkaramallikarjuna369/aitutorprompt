import { useState, useEffect } from 'react';
import { visualizationApi, visualizationOrchestratorApi, QuadraticAnalysis, StudentMode, AIVisualConfig } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Slider } from '../ui/slider';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer } from 'recharts';
import { Calculator, TrendingUp, Target, Info, Lightbulb, Sparkles } from 'lucide-react';

interface QuadraticVisualizerProps {
  initialA?: number;
  initialB?: number;
  initialC?: number;
  studentMode?: StudentMode;
  topicId?: string;
}

export default function QuadraticVisualizer({ 
  initialA = 1, 
  initialB = -5, 
  initialC = 6,
  studentMode = 'average',
  topicId = 'qe-graphical'
}: QuadraticVisualizerProps) {
  const [a, setA] = useState(initialA);
  const [b, setB] = useState(initialB);
  const [c, setC] = useState(initialC);
  const [analysis, setAnalysis] = useState<QuadraticAnalysis | null>(null);
  const [visualConfig, setVisualConfig] = useState<AIVisualConfig | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [configLoading, setConfigLoading] = useState(false);

  useEffect(() => {
    const fetchVisualConfig = async () => {
      setConfigLoading(true);
      try {
        const response = await visualizationOrchestratorApi.getVisualConfig(topicId, { student_mode: studentMode });
        setVisualConfig(response.config);
      } catch (error) {
        console.error('Failed to fetch visual config:', error);
      } finally {
        setConfigLoading(false);
      }
    };
    fetchVisualConfig();
  }, [studentMode, topicId]);

  useEffect(() => {
    const fetchAnalysis = async () => {
      if (a === 0) return;
      setIsLoading(true);
      try {
        const data = await visualizationApi.analyzeQuadratic({ a, b, c });
        setAnalysis(data);
      } catch (error) {
        console.error('Failed to analyze quadratic:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    const debounce = setTimeout(fetchAnalysis, 300);
    return () => clearTimeout(debounce);
  }, [a, b, c]);

  const chartData = analysis?.plot_points.map(([x, y]) => ({ x, y })) || [];

  const getRootsTypeColor = (type: string) => {
    switch (type) {
      case 'two_distinct_real': return 'bg-green-100 text-green-800';
      case 'two_equal_real': return 'bg-blue-100 text-blue-800';
      case 'no_real_roots': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const colors = visualConfig?.colors || {
    primary: '#4f46e5',
    secondary: '#9333ea',
    background: '#f5f5f5',
    text: '#1f2937',
    accent: '#f59e0b',
    error: '#ef4444',
    success: '#22c55e'
  };

  const xAxisColor = visualConfig?.x_axis?.color || '#FF6B6B';
  const yAxisColor = visualConfig?.y_axis?.color || '#4ECDC4';

  return (
    <div className="space-y-6">
      {visualConfig && visualConfig.scaffolding?.show_hints && visualConfig.pedagogical_notes?.length > 0 && (
        <Card className="border-amber-200 bg-amber-50">
          <CardContent className="pt-4">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-5 w-5 text-amber-600 mt-0.5" />
              <div>
                <h4 className="font-medium text-amber-900 mb-1">Learning Tips</h4>
                <ul className="text-sm text-amber-800 space-y-1">
                  {visualConfig.pedagogical_notes.slice(0, 3).map((note, idx) => (
                    <li key={idx}>{note}</li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card style={{ backgroundColor: visualConfig?.colors?.background || '#ffffff' }}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" style={{ color: colors.primary }} />
            {visualConfig?.title || 'Interactive Parabola Explorer'}
            {visualConfig && (
              <Badge variant="outline" className="ml-2">
                <Sparkles className="h-3 w-3 mr-1" />
                {visualConfig.student_mode} mode
              </Badge>
            )}
          </CardTitle>
          {visualConfig?.description && (
            <p className="text-sm text-gray-600">{visualConfig.description}</p>
          )}
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="slider-a" className="text-sm font-medium">
                      Coefficient a (x²)
                    </Label>
                    <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                      a = {a}
                    </span>
                  </div>
                  <Slider
                    id="slider-a"
                    min={-5}
                    max={5}
                    step={0.5}
                    value={[a]}
                    onValueChange={([val]) => setA(val)}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    Controls the width and direction of the parabola
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="slider-b" className="text-sm font-medium">
                      Coefficient b (x)
                    </Label>
                    <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                      b = {b}
                    </span>
                  </div>
                  <Slider
                    id="slider-b"
                    min={-10}
                    max={10}
                    step={1}
                    value={[b]}
                    onValueChange={([val]) => setB(val)}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    Shifts the parabola horizontally
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="slider-c" className="text-sm font-medium">
                      Constant c
                    </Label>
                    <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
                      c = {c}
                    </span>
                  </div>
                  <Slider
                    id="slider-c"
                    min={-10}
                    max={10}
                    step={1}
                    value={[c]}
                    onValueChange={([val]) => setC(val)}
                    className="w-full"
                  />
                  <p className="text-xs text-gray-500">
                    Shifts the parabola vertically (y-intercept)
                  </p>
                </div>
              </div>

              {analysis && (
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <h4 className="font-semibold text-indigo-900 mb-2">
                    Equation: {analysis.equation_string}
                  </h4>
                  {analysis.factored_form && (
                    <p className="text-sm text-indigo-700">
                      Factored: {analysis.factored_form}
                    </p>
                  )}
                  <p className="text-sm text-indigo-700">
                    Vertex form: {analysis.vertex_form}
                  </p>
                </div>
              )}
            </div>

            <div className="h-80">
              {isLoading || configLoading ? (
                <div className="h-full flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: colors.primary }}></div>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid 
                      strokeDasharray="3 3" 
                      stroke={visualConfig?.x_axis?.grid_color || '#e0e0e0'} 
                    />
                    <XAxis 
                      dataKey="x" 
                      type="number" 
                      domain={['dataMin', 'dataMax']}
                      tickFormatter={(val) => val.toFixed(0)}
                      stroke={xAxisColor}
                      tick={{ fill: colors.text, fontSize: visualConfig?.x_axis?.label_size || 12 }}
                    />
                    <YAxis 
                      type="number"
                      domain={['auto', 'auto']}
                      tickFormatter={(val) => val.toFixed(0)}
                      stroke={yAxisColor}
                      tick={{ fill: colors.text, fontSize: visualConfig?.y_axis?.label_size || 12 }}
                    />
                    <Tooltip 
                      formatter={(value: number) => [value.toFixed(2), 'y']}
                      labelFormatter={(label) => `x = ${Number(label).toFixed(2)}`}
                      contentStyle={{ backgroundColor: colors.background, borderColor: colors.primary }}
                    />
                    <ReferenceLine x={0} stroke={xAxisColor} strokeWidth={2} />
                    <ReferenceLine y={0} stroke={yAxisColor} strokeWidth={2} />
                    {analysis?.axis_of_symmetry !== undefined && (
                      <ReferenceLine 
                        x={analysis.axis_of_symmetry} 
                        stroke={colors.secondary} 
                        strokeDasharray="5 5"
                        label={{ value: 'Axis', position: 'top', fill: colors.secondary }}
                      />
                    )}
                    <Line 
                      type="monotone" 
                      dataKey="y" 
                      stroke={colors.primary} 
                      strokeWidth={2}
                      dot={false}
                      animationDuration={visualConfig?.animation?.duration_ms || 1000}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {analysis && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <Target className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium text-gray-600">Roots</span>
              </div>
              <Badge className={getRootsTypeColor(analysis.roots_type)}>
                {analysis.roots_type.replace(/_/g, ' ')}
              </Badge>
              {analysis.roots && (
                <p className="mt-2 font-mono text-lg">
                  x = {analysis.roots.join(', ')}
                </p>
              )}
              {!analysis.roots && (
                <p className="mt-2 text-sm text-gray-500">No real roots</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-gray-600">Vertex</span>
              </div>
              <p className="font-mono text-lg">
                ({analysis.vertex[0]}, {analysis.vertex[1]})
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {analysis.direction === 'upward' ? 'Minimum' : 'Maximum'} point
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <Info className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-gray-600">Discriminant</span>
              </div>
              <p className="font-mono text-lg">
                D = {analysis.discriminant}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {analysis.discriminant_interpretation}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-2">
                <Calculator className="h-4 w-4 text-orange-600" />
                <span className="text-sm font-medium text-gray-600">Properties</span>
              </div>
              <div className="space-y-1 text-sm">
                <p>Direction: <span className="font-medium">{analysis.direction}</span></p>
                <p>Y-intercept: <span className="font-medium">{analysis.y_intercept}</span></p>
                <p>Axis: <span className="font-medium">x = {analysis.axis_of_symmetry}</span></p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
