import { apiClient as api } from '../lib/api';


interface ContractAnalysis {
  id: string;
  contract_id: string;
  analysis: string;
  created_at: string;
  updated_at: string;
}

interface Contract {
  id: string;
  client_name: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const contractAnalysisService = {
  // Get all contracts
  getContracts: async (): Promise<Contract[]> => {
    try {
      const response = await api.get<Contract[]>('/api/v1/harper/contracts');
      return response.data;
    } catch (error) {
      console.error('Error fetching contracts:', error);
      throw error;
    }
  },

  // Get existing analysis for a contract
  getContractAnalysis: async (contractId: string): Promise<ContractAnalysis | null> => {
    try {
      const response = await api.get<ContractAnalysis>(`/api/v1/analysis/contracts/${contractId}/analysis`);
      return response.data;
    } catch (error: unknown) {
      const err = error as { response?: { status?: number } };
      if (err.response?.status === 404) {
        return null; // No analysis exists yet
      }
      console.error('Error fetching contract analysis:', error);
      throw error;
    }
  },

  // Trigger analysis for a contract
  analyzeContract: async (contractId: string): Promise<ContractAnalysis> => {
    try {
      const response = await api.post<ContractAnalysis>(`/api/v1/analysis/contracts/${contractId}/analyze`);
      return response.data;
    } catch (error: unknown) {
      console.error('Error analyzing contract:', error);
      throw error;
    }
  },

  // Bulk analyze contracts
  bulkAnalyzeContracts: async (contractIds: string[]): Promise<unknown> => {
    try {
      const response = await api.post('/api/v1/analysis/contracts/analyze-bulk', {
        contract_ids: contractIds
      });
      return response.data;
    } catch (error: unknown) {
      console.error('Error bulk analyzing contracts:', error);
      throw error;
    }
  }
};