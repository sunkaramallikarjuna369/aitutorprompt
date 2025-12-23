import { ContentBlock } from '../../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { 
  FileText, 
  Code, 
  Image, 
  Video, 
  Calculator,
  Lightbulb,
  BookOpen
} from 'lucide-react';

interface ContentViewerProps {
  blocks: ContentBlock[];
  title?: string;
}

export default function ContentViewer({ blocks, title }: ContentViewerProps) {
  const getBlockIcon = (type: string) => {
    switch (type) {
      case 'text': return <FileText className="h-4 w-4" />;
      case 'formula': return <Calculator className="h-4 w-4" />;
      case 'example': return <Lightbulb className="h-4 w-4" />;
      case 'definition': return <BookOpen className="h-4 w-4" />;
      case 'code': return <Code className="h-4 w-4" />;
      case 'image': return <Image className="h-4 w-4" />;
      case 'video': return <Video className="h-4 w-4" />;
      default: return <FileText className="h-4 w-4" />;
    }
  };

  const getBlockStyle = (type: string) => {
    switch (type) {
      case 'formula':
        return 'bg-blue-50 border-l-4 border-l-blue-500';
      case 'example':
        return 'bg-amber-50 border-l-4 border-l-amber-500';
      case 'definition':
        return 'bg-purple-50 border-l-4 border-l-purple-500';
      case 'important':
        return 'bg-red-50 border-l-4 border-l-red-500';
      default:
        return 'bg-white';
    }
  };

  const renderContent = (block: ContentBlock) => {
    switch (block.type) {
      case 'formula':
        return (
          <div className="font-mono text-lg text-center py-4 bg-white rounded">
            {block.content}
          </div>
        );
      case 'example': {
        const steps = block.metadata?.steps as string[] | undefined;
        return (
          <div className="space-y-2">
            <p className="text-gray-700 whitespace-pre-wrap">{block.content}</p>
            {steps && steps.length > 0 ? (
              <div className="mt-3 space-y-2">
                {steps.map((step, idx) => (
                  <div key={idx} className="flex items-start gap-2 text-sm">
                    <span className="bg-amber-200 text-amber-800 rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        );
      }
      case 'definition': {
        const keywords = block.metadata?.keywords as string[] | undefined;
        return (
          <div>
            <p className="text-gray-700 font-medium">{block.content}</p>
            {keywords && keywords.length > 0 ? (
              <div className="mt-2 flex flex-wrap gap-1">
                {keywords.map((keyword, idx) => (
                  <Badge key={idx} variant="secondary" className="text-xs">
                    {keyword}
                  </Badge>
                ))}
              </div>
            ) : null}
          </div>
        );
      }
      default:
        return (
          <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
            {block.content}
          </p>
        );
    }
  };

  return (
    <Card>
      {title && (
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-indigo-600" />
            {title}
          </CardTitle>
        </CardHeader>
      )}
      <CardContent className={title ? '' : 'pt-6'}>
        <div className="space-y-4">
          {blocks.sort((a, b) => a.order - b.order).map((block) => (
            <div 
              key={block.id}
              className={`p-4 rounded-lg ${getBlockStyle(block.type)}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-gray-500">
                  {getBlockIcon(block.type)}
                </span>
                <h4 className="font-semibold text-gray-900">{block.title}</h4>
                <Badge variant="outline" className="text-xs ml-auto">
                  {block.type}
                </Badge>
              </div>
              {renderContent(block)}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
