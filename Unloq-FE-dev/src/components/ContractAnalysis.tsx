import React, { useState, useEffect } from 'react';
import { contractAnalysisService } from '../services/contractAnalysisService';

interface ContractAnalysisViewProps {
  contractId: string;
  onClose: () => void;
}

const ContractAnalysisView: React.FC<ContractAnalysisViewProps> = ({ contractId, onClose }) => {
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [analyzing, setAnalyzing] = useState<boolean>(false);

  const fetchAnalysis = React.useCallback(async () => {
    try {
      setLoading(true);
      const result = await contractAnalysisService.getContractAnalysis(contractId);
      if (result) {
        setAnalysis(result.analysis);
      } else {
        setAnalysis(null);
      }
    } catch (error) {
      console.error('Error fetching analysis:', error);
      setAnalysis('Error loading analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [contractId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      const result = await contractAnalysisService.analyzeContract(contractId);
      setAnalysis(result.analysis);
    } catch (error) {
      console.error('Error analyzing contract:', error);
      setAnalysis('Error analyzing contract. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        <div className="flex justify-between items-center p-4 border-b">
          <h2 className="text-xl font-bold">Contract Analysis</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            &times;
          </button>
        </div>
        
        <div className="overflow-y-auto flex-grow p-4">
          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
          ) : analysis ? (
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap">{analysis}</div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-6">This contract has not been analyzed yet.</p>
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className={`px-6 py-3 bg-blue-600 text-white rounded-lg font-medium ${
                  analyzing ? 'opacity-70 cursor-not-allowed' : 'hover:bg-blue-700'
                }`}
              >
                {analyzing ? (
                  <span className="flex items-center justify-center">
                    <span className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></span>
                    Analyzing...
                  </span>
                ) : (
                  'Analyze with AI'
                )}
              </button>
            </div>
          )}
        </div>
        
        <div className="p-4 border-t bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContractAnalysisView;