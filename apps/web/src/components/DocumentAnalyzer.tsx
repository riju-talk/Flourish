import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { analyzeDocument } from '@/integrations/api';

export default function DocumentAnalyzer() {
  const [file, setFile] = useState<File | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'text/plain', 'text/markdown'];
      if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.txt')) {
        setError('Please upload a PDF or text file');
        return;
      }

      // Validate file size (10MB max)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      setFile(selectedFile);
      setError(null);
      setResult(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setAnalyzing(true);
    setError(null);

    try {
      const analysis = await analyzeDocument(file);
      setResult(analysis);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze document');
      console.error('Document analysis error:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>📄 Document Analyzer</CardTitle>
          <CardDescription>
            Upload plant care guides, manuals, or documents for AI-powered analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!result ? (
            <>
              {/* Upload Area */}
              <div className="border-2 border-dashed rounded-lg p-8 text-center hover:border-primary transition-colors">
                <input
                  type="file"
                  id="file-upload"
                  className="hidden"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileSelect}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                  <p className="text-lg font-semibold mb-2">
                    {file ? file.name : 'Choose a file or drag it here'}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    PDF or text files, up to 10MB
                  </p>
                </label>
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {file && (
                <div className="flex items-center justify-between p-4 bg-accent rounded-lg">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  <div className="space-x-2">
                    <Button variant="outline" size="sm" onClick={reset}>
                      Remove
                    </Button>
                    <Button onClick={handleAnalyze} disabled={analyzing}>
                      {analyzing ? 'Analyzing...' : 'Analyze'}
                    </Button>
                  </div>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Analysis Results */}
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Document analyzed successfully! Here's what we found:
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                {/* Summary */}
                <div>
                  <h3 className="text-lg font-semibold mb-2">📝 Summary</h3>
                  <p className="text-sm">{result.analysis}</p>
                </div>

                {/* Key Points */}
                {result.key_points && result.key_points.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">🔑 Key Points</h3>
                    <ul className="space-y-1">
                      {result.key_points.map((point: string, idx: number) => (
                        <li key={idx} className="text-sm flex items-start">
                          <span className="mr-2">•</span>
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Care Schedule */}
                <div className="grid md:grid-cols-2 gap-4">
                  {result.watering_schedule && result.watering_schedule !== "Not specified" && (
                    <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                      <h4 className="font-semibold mb-2">💧 Watering</h4>
                      <p className="text-sm">{result.watering_schedule}</p>
                    </div>
                  )}
                  {result.fertilizing_schedule && result.fertilizing_schedule !== "Not specified" && (
                    <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                      <h4 className="font-semibold mb-2">🌿 Fertilizing</h4>
                      <p className="text-sm">{result.fertilizing_schedule}</p>
                    </div>
                  )}
                  {result.light_requirements && result.light_requirements !== "Not specified" && (
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                      <h4 className="font-semibold mb-2">☀️ Light</h4>
                      <p className="text-sm">{result.light_requirements}</p>
                    </div>
                  )}
                </div>

                {/* Warnings */}
                {result.warnings && result.warnings.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2 text-orange-600">⚠️ Warnings</h3>
                    <div className="space-y-2">
                      {result.warnings.map((warning: string, idx: number) => (
                        <Alert key={idx} variant="destructive">
                          <AlertDescription>{warning}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  </div>
                )}

                {/* Action Items */}
                {result.action_items && result.action_items.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">✅ Recommended Actions</h3>
                    <div className="space-y-2">
                      {result.action_items.map((action: string, idx: number) => (
                        <div key={idx} className="flex items-center space-x-2 p-2 bg-accent rounded">
                          <Badge variant="outline">{idx + 1}</Badge>
                          <span className="text-sm">{action}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Button onClick={reset} variant="outline" className="w-full">
                Analyze Another Document
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {/* Info Section */}
      <Card className="mt-6">
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              • Upload any plant care document (PDF, TXT)
            </p>
            <p>
              • Our AI powered by Ollama extracts key information
            </p>
            <p>
              • Get watering schedules, fertilizing tips, light requirements, and warnings
            </p>
            <p>
              • Receive actionable recommendations based on the document
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
