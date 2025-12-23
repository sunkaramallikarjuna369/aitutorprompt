import { useState } from 'react';
import { 
  ragAgentApi, 
  pdfIngestionApi,
  AskQuestionResponse, 
  PDFMetadata,
  StudentMode 
} from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { 
  MessageSquare, 
  Send, 
  FileText, 
  Lightbulb,
  BookOpen,
  Loader2,
  ChevronDown,
  ChevronUp,
  BarChart3,
  RefreshCw
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

interface RAGAgentProps {
  studentMode: StudentMode;
  onModeChange?: (mode: StudentMode) => void;
}

export default function RAGAgent({ studentMode, onModeChange }: RAGAgentProps) {
  const [pdfs, setPdfs] = useState<PDFMetadata[]>([]);
  const [selectedPdfId, setSelectedPdfId] = useState<string>('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<AskQuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingPdfs, setLoadingPdfs] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [showCitations, setShowCitations] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPdfs = async () => {
    setLoadingPdfs(true);
    try {
      const pdfList = await pdfIngestionApi.listPdfs();
      setPdfs(pdfList.filter(p => p.status === 'processed'));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load PDFs');
    } finally {
      setLoadingPdfs(false);
    }
  };

  const indexPdf = async () => {
    if (!selectedPdfId) return;
    setIndexing(true);
    try {
      await ragAgentApi.indexPdf(selectedPdfId);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to index PDF');
    } finally {
      setIndexing(false);
    }
  };

  const askQuestion = async () => {
    if (!selectedPdfId || !question.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await ragAgentApi.askQuestion({
        pdf_id: selectedPdfId,
        question: question.trim(),
        student_mode: studentMode,
        include_visualization: true,
        max_chunks: 5
      });
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
    } finally {
      setLoading(false);
    }
  };

  const getQuestionTypeColor = (type: string) => {
    switch (type) {
      case 'factual': return 'bg-blue-100 text-blue-800';
      case 'conceptual': return 'bg-purple-100 text-purple-800';
      case 'procedural': return 'bg-green-100 text-green-800';
      case 'application': return 'bg-amber-100 text-amber-800';
      case 'exercise': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getModeDescription = (mode: StudentMode) => {
    switch (mode) {
      case 'dull': return 'Simple explanations with real-world examples';
      case 'average': return 'Balanced explanations with standard terminology';
      case 'clever': return 'Advanced explanations with deeper insights';
    }
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-indigo-600" />
            Ask Questions About PDF Content
          </CardTitle>
          <CardDescription>
            Use RAG (Retrieval-Augmented Generation) to ask questions about uploaded NCERT PDFs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Select PDF</label>
              <Select value={selectedPdfId} onValueChange={setSelectedPdfId}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a processed PDF" />
                </SelectTrigger>
                <SelectContent>
                  {pdfs.map(pdf => (
                    <SelectItem key={pdf.pdf_id} value={pdf.pdf_id}>
                      {pdf.filename} ({pdf.class_level} - {pdf.subject})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <Button 
              variant="outline" 
              onClick={loadPdfs}
              disabled={loadingPdfs}
            >
              {loadingPdfs ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
            {selectedPdfId && (
              <Button 
                variant="outline" 
                onClick={indexPdf}
                disabled={indexing}
              >
                {indexing ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <FileText className="h-4 w-4 mr-2" />
                )}
                Index
              </Button>
            )}
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Learning Mode</label>
            <Select 
              value={studentMode} 
              onValueChange={(value) => onModeChange?.(value as StudentMode)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="dull">Dull (Simplified)</SelectItem>
                <SelectItem value="average">Average (Balanced)</SelectItem>
                <SelectItem value="clever">Clever (Advanced)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-gray-500 mt-1">{getModeDescription(studentMode)}</p>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Your Question</label>
            <Textarea
              placeholder="Ask a question about the PDF content... (e.g., 'How do I solve a quadratic equation?')"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              rows={3}
              className="resize-none"
            />
          </div>

          <Button 
            onClick={askQuestion}
            disabled={loading || !selectedPdfId || !question.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                Thinking...
              </>
            ) : (
              <>
                <Send className="h-4 w-4 mr-2" />
                Ask Question
              </>
            )}
          </Button>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}
        </CardContent>
      </Card>

      {response && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-amber-500" />
              Answer
              <Badge className={`ml-2 ${getQuestionTypeColor(response.question_type)}`}>
                {response.question_type}
              </Badge>
              {response.cached && (
                <Badge variant="outline" className="ml-2">Cached</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="prose prose-sm max-w-none">
              <div className="whitespace-pre-wrap text-gray-700 leading-relaxed">
                {response.answer}
              </div>
            </div>

            {response.visualization && (
              <div className="p-4 bg-indigo-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <BarChart3 className="h-4 w-4 text-indigo-600" />
                  <span className="font-medium text-indigo-900">
                    {response.visualization.title}
                  </span>
                </div>
                <p className="text-sm text-indigo-700 mb-3">
                  {response.visualization.description}
                </p>
                {response.visualization.pedagogical_notes.length > 0 && (
                  <div className="space-y-1">
                    {response.visualization.pedagogical_notes.map((note, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-sm text-indigo-600">
                        <span className="text-indigo-400">-</span>
                        <span>{note}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {response.citations.length > 0 && (
              <div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowCitations(!showCitations)}
                  className="flex items-center gap-1 text-gray-600"
                >
                  <BookOpen className="h-4 w-4" />
                  {showCitations ? 'Hide' : 'Show'} Citations ({response.citations.length})
                  {showCitations ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
                
                {showCitations && (
                  <div className="mt-2 space-y-2">
                    {response.citations.map((citation, idx) => (
                      <div 
                        key={idx}
                        className="p-3 bg-gray-50 rounded-lg text-sm"
                      >
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="text-xs">
                            Chunk {citation.chunk_id}
                          </Badge>
                          {citation.page_number && (
                            <Badge variant="outline" className="text-xs">
                              Page {citation.page_number}
                            </Badge>
                          )}
                          <span className="text-xs text-gray-400 ml-auto">
                            Score: {citation.score.toFixed(2)}
                          </span>
                        </div>
                        <p className="text-gray-600 line-clamp-3">
                          {citation.content}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {pdfs.length === 0 && !loadingPdfs && (
        <Card>
          <CardContent className="py-8 text-center">
            <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 mb-2">No processed PDFs available</p>
            <p className="text-sm text-gray-400">
              Upload and process a PDF first using the PDF Ingestion feature
            </p>
            <Button 
              variant="outline" 
              onClick={loadPdfs}
              className="mt-4"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh PDF List
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
