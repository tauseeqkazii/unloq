import { useState } from 'react';
import ContractAnalysisView from '../components/ContractAnalysis';


interface Contract {
  id: string;
  client_name: string;
  // add other fields if needed
}

export function ContractsPage() {
  const [selectedContract, setSelectedContract] = useState<string | null>(null);

  // Dummy data for now
  const contracts: Contract[] = [
    { id: '1', client_name: 'Client A' },
    { id: '2', client_name: 'Client B' },
  ];

  return (
    <div>
      {/* Contract list */}
      {contracts.map((contract: Contract) => (
        <div key={contract.id}>
          <h3>{contract.client_name}</h3>
          <button onClick={() => setSelectedContract(contract.id)}>
            View Analysis
          </button>
        </div>
      ))}

      {/* Analysis modal/panel */}
      {selectedContract && (
        <ContractAnalysisView
          contractId={selectedContract}
          onClose={() => setSelectedContract(null)}
        />
      )}
    </div>
  );
}
