import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  X, 
  Upload, 
  CheckCircle, 
  AlertTriangle, 
  Plus, 
  Database,
  ShieldAlert,
  AlertCircle,
  FileSpreadsheet
} from 'lucide-react';
import { RiskTicket, IssueTicket, calculateRiskLevel, getMatrixScore, CauseCategory, RiskStatus, RiskTrend, RiskPriority, GovernanceLevel } from '../types';

interface ImportDataModalProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'risk' | 'issue';
  existingCount: number;
  onImportRisks?: (newRisks: RiskTicket[]) => void;
  onImportIssues?: (newIssues: IssueTicket[]) => void;
}

// Solid helper to parse CSV/TSV lines taking quotes into account
function parseCSVLine(line: string, separator: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === separator && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result.map(val => val.replace(/^["']|["']$/g, '').trim());
}

export default function ImportDataModal({
  isOpen,
  onClose,
  type,
  existingCount,
  onImportRisks,
  onImportIssues
}: ImportDataModalProps) {
  const [importTarget, setImportTarget] = useState<'risk' | 'issue'>(type);
  const [rawTextContent, setRawTextContent] = useState<string>('');
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [headersMatched, setHeadersMatched] = useState<string[]>([]);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync importTarget when modal opens or type prop changes
  useEffect(() => {
    if (isOpen) {
      setImportTarget(type);
      setRawTextContent('');
      setFileName('');
      setErrorMsg(null);
      setPreviewData([]);
      setHeadersMatched([]);
    }
  }, [isOpen, type]);

  // Re-process preview when import target changes if file content exists
  useEffect(() => {
    if (rawTextContent) {
      processTextData(rawTextContent, importTarget);
    }
  }, [importTarget]);

  if (!isOpen) return null;

  const todayStr = new Date().toISOString().split('T')[0];

  // Map arbitrary CSV/TSV column titles to the closest internal schema key
  const matchHeaderToKey = (header: string, targetType: 'risk' | 'issue'): string | null => {
    const clean = header.toLowerCase().replace(/[^a-z0-9]/g, '');
    
    if (targetType === 'risk') {
      if (/^(id|riskid|rsk)$/.test(clean)) return 'id';
      if (/^(status|riskstatus|state)$/.test(clean)) return 'status';
      if (/^(relatedissueid|issueid|issue)$/.test(clean)) return 'relatedIssueId';
      if (/^(riskowner|owner|assignedto)$/.test(clean)) return 'riskOwner';
      if (/^(bundle|workstream|portfolio)$/.test(clean)) return 'bundle';
      if (/^(drivertreeref|drivertree|dtr)$/.test(clean)) return 'driverTreeRef';
      if (/^(riskname|risktitle|name|title)$/.test(clean)) return 'riskName';
      if (/^(riskdescription|description|statement|riskstatement)$/.test(clean)) return 'riskDescription';
      if (/^(causedescription|cause|rootcause)$/.test(clean)) return 'causeDescription';
      if (/^(causecategory|category)$/.test(clean)) return 'causeCategory';
      if (/^(consequencedescription|consequence|impact)$/.test(clean)) return 'consequenceDescription';
      if (/^(trend|risktrend|direction)$/.test(clean)) return 'trend';
      if (/^(priority|riskpriority)$/.test(clean)) return 'priority';
      if (/^(governancelevel|govlevel|governance|highlighttogovernancelevel|highlightto|highlighttogovernance)$/.test(clean)) return 'governanceLevel';
      if (/^(inherentlikelihoodrating|inherentlikelihood|likelihood|inhlikelihood|l)$/.test(clean)) return 'inherentLikelihood';
      if (/^(inherentconsequencerating|inherentconsequence|consequence|inhconsequence|c)$/.test(clean)) return 'inherentConsequence';
      if (/^(inherentrisk|inherentriskscore)$/.test(clean)) return 'inherentRiskScore';
      if (/^(treatmentowner)$/.test(clean)) return 'treatmentOwner';
      if (/^(treatmentmitigationplan|treatmentplan|treatment|mitigationplan|mitigation)$/.test(clean)) return 'treatmentPlan';
      if (/^(targetdate|mitigationduedate|duedate)$/.test(clean)) return 'targetDate';
      if (/^(residuallikelihoodrating|residuallikelihood|reslikelihood|rl)$/.test(clean)) return 'residualLikelihood';
      if (/^(residualconsequencerating|residualconsequence|resconsequence|rc)$/.test(clean)) return 'residualConsequence';
      if (/^(residualrisk|residualriskscore)$/.test(clean)) return 'residualRiskScore';
      if (/^(dateraised|raiseddate|createddate)$/.test(clean)) return 'dateRaised';
      if (/^(dateclosed|closeddate)$/.test(clean)) return 'dateClosed';
      if (/^(risklastupdated|lastupdated)$/.test(clean)) return 'riskLastUpdated';
      if (/^(comments|notes|remarks)$/.test(clean)) return 'comments';
      if (/^(protectedissuerisk|protected|issuerisk)$/.test(clean)) return 'protectedIssueRisk';
      if (/^(dperefnumber|dperef|refnumber)$/.test(clean)) return 'dpeRefNumber';
      if (/^(timelines|timeline)$/.test(clean)) return 'timelines';
      if (/^(signoffrequirement|signoff)$/.test(clean)) return 'signOffRequirement';
      if (/^(executivestatus|execstatus)$/.test(clean)) return 'executiveStatus';
      if (/^(nextmitigationduedate|nextduedate)$/.test(clean)) return 'nextMitigationDueDate';
      if (/^(mitigationstatus|mitstatus)$/.test(clean)) return 'mitigationStatus';
      if (/^(strategy|treatmentstrategy)$/.test(clean)) return 'strategy';
      if (/^(whoraised|raisedby)$/.test(clean)) return 'whoRaised';
      if (/^(opendays)$/.test(clean)) return 'openDays';
    } else {
      // Issue matching
      if (/^(id|issueid|iss)$/.test(clean)) return 'id';
      if (/^(status|issuestatus|state)$/.test(clean)) return 'status';
      if (/^(relatedriskid|riskid|risk)$/.test(clean)) return 'relatedRiskId';
      if (/^(issueowner|owner|assignedto)$/.test(clean)) return 'issueOwner';
      if (/^(bundle|workstream|portfolio)$/.test(clean)) return 'bundle';
      if (/^(drivertreeref|drivertree|dtr)$/.test(clean)) return 'driverTreeRef';
      if (/^(issuename|issuetitle|name|title)$/.test(clean)) return 'issueName';
      if (/^(issuedescription|description|statement)$/.test(clean)) return 'issueDescription';
      if (/^(causedescription|cause|rootcause)$/.test(clean)) return 'causeDescription';
      if (/^(impactcategory|category|impact)$/.test(clean)) return 'impactCategory';
      if (/^(consequence|impactconsequence)$/.test(clean)) return 'consequence';
      if (/^(trend|issuetrend|direction)$/.test(clean)) return 'trend';
      if (/^(priorityrating|priority|issuepriority)$/.test(clean)) return 'priorityRating';
      if (/^(escalateto|escalation)$/.test(clean)) return 'escalateTo';
      if (/^(severityrating|severity|issueseverity)$/.test(clean)) return 'severityRating';
      if (/^(actionplan|mitigation|plan|actionplanwhatwhenwho)$/.test(clean)) return 'actionPlan';
      if (/^(nextactionowner|actionowner)$/.test(clean)) return 'nextActionOwner';
      if (/^(dateraised|raiseddate|createddate)$/.test(clean)) return 'dateRaised';
      if (/^(raisedby|whoraised)$/.test(clean)) return 'raisedBy';
      if (/^(dateclosed|closeddate)$/.test(clean)) return 'dateClosed';
      if (/^(lastupdated|updateddate|lastmodified)$/.test(clean)) return 'lastUpdated';
      if (/^(protectedissuerisk|protected|issuerisk)$/.test(clean)) return 'protectedIssueRisk';
      if (/^(dperefnumber|dperef|refnumber)$/.test(clean)) return 'dpeRefNumber';
    }
    return null;
  };

  const parseRating = (val: any, defaultVal: number | null = null): number | null => {
    if (val === undefined || val === null) return defaultVal;
    const vStr = String(val).trim().toLowerCase();
    if (!vStr || vStr === 'n/a' || vStr === 'na' || vStr === 'none' || vStr === '-' || vStr === 'null' || vStr === 'undefined') {
      return null;
    }

    const match = vStr.match(/\d+/);
    if (match) {
      const num = parseInt(match[0], 10);
      if (num >= 1 && num <= 6) return num;
      if (num === 0) return null;
    }

    // Check textual labels for Likelihood
    if (vStr.includes('rare')) return 1;
    if (vStr.includes('improb')) return 2;
    if (vStr.includes('occas')) return 3;
    if (vStr.includes('prob')) return 4;
    if (vStr.includes('almost') || vStr.includes('certain') || vStr.includes('freq')) return 5;

    // Check textual labels for Consequence
    if (vStr.includes('neglig') || vStr.includes('minor') || vStr.includes('insig')) return 1;
    if (vStr.includes('mod')) return 2;
    if (vStr.includes('maj')) return 3;
    if (vStr.includes('crit') || vStr.includes('sev')) return 4;
    if (vStr.includes('catastr') || vStr.includes('extreme')) return 5;

    if (vStr.includes('no data') || vStr.includes('nodata')) return 6;

    return defaultVal;
  };

  const parseRiskStatus = (val?: string): RiskStatus => {
    if (!val) return 'Active';
    const v = val.trim().toLowerCase();
    if (v.startsWith('act')) return 'Active';
    if (v.startsWith('cl')) return 'Closed';
    if (v.startsWith('tr')) return 'Transferred';
    if (v.startsWith('ret')) return 'Retired';
    if (v.includes('issue') || v.includes('eventuated') || v.startsWith('iss') || v.startsWith('ev')) return 'Issue Eventuated';
    return 'Active';
  };

  const parseCauseCategory = (val?: string): CauseCategory => {
    if (!val) return 'Unknown';
    const trimmed = val.trim();
    if (!trimmed) return 'Unknown';

    const ALL_CATEGORIES = [
      'Contract & Legal',
      'Cost',
      'Eng capability',
      'Governance Assurance',
      'Industry',
      'Interoperability',
      'Legal/Contract',
      'Prime Governance',
      'Product',
      'Reputation',
      'Schedule',
      'Scope',
      'Security',
      'Security & Cyber',
      'SovOps',
      'Technical Maturity',
      'Technical Performance',
      'NA',
      'N/A',
      'Unknown',
      'No Data',
      '-',
      ' ',
    ];

    const exactMatch = ALL_CATEGORIES.find(
      cat => cat.trim().toLowerCase() === trimmed.toLowerCase()
    );
    if (exactMatch) return exactMatch;

    const v = trimmed.toLowerCase();

    if (v === 'na' || v === 'n.a.') return 'NA';
    if (v === 'n/a' || v === 'not applicable') return 'N/A';
    if (v === 'unknown' || v === 'unk') return 'Unknown';
    if (v === 'no data' || v === 'nodata' || v === 'none') return 'No Data';
    if (v === '-' || v === '--') return '-';

    if (v.includes('contract') && v.includes('legal')) return 'Contract & Legal';
    if (v.includes('legal/contract') || v.includes('legal / contract')) return 'Legal/Contract';
    if (v.includes('eng') && (v.includes('cap') || v.includes('ability'))) return 'Eng capability';
    if (v.includes('prime')) return 'Prime Governance';
    if (v.includes('gov') || v.includes('assurance')) return 'Governance Assurance';
    if (v.includes('cyber') || (v.includes('sec') && v.includes('cyber'))) return 'Security & Cyber';
    if (v.includes('sec')) return 'Security';
    if (v.includes('sov')) return 'SovOps';
    if (v.includes('matur')) return 'Technical Maturity';
    if (v.includes('perf')) return 'Technical Performance';
    if (v.includes('tech')) return 'Technical Performance';
    if (v.includes('interop')) return 'Interoperability';
    if (v.includes('prod')) return 'Product';
    if (v.includes('rep')) return 'Reputation';
    if (v.includes('ind')) return 'Industry';
    if (v.includes('sched')) return 'Schedule';
    if (v.includes('scop')) return 'Scope';
    if (v.includes('cost') || v.includes('comm') || v.includes('fin')) return 'Cost';

    return 'Unknown';
  };

  const parseRiskTrend = (val?: string): RiskTrend => {
    if (!val) return 'Stable';
    const v = val.trim().toLowerCase();
    if (v.includes('inc')) return 'Increasing';
    if (v.includes('dec')) return 'Decreasing';
    return 'Stable';
  };

  const parseRiskPriority = (val?: string): RiskPriority => {
    if (!val) return 'Prompt';
    const v = val.trim().toLowerCase();
    if (v.includes('imm')) return 'Immediate';
    if (v.includes('urg')) return 'Urgent';
    if (v.includes('pro')) return 'Prompt';
    if (v.includes('not')) return 'Not Urgent';
    return 'Prompt';
  };

  const parseGovernanceLevel = (val?: string): GovernanceLevel => {
    if (!val || !val.trim()) return 'No Data';
    const v = val.trim().toLowerCase();
    if (v === 'n/a' || v === 'na' || v === 'not applicable' || v === 'n/a.') return 'N/A';
    if (v === 'no data' || v === 'nodata' || v === 'none' || v === '-' || v === 'no_data') return 'No Data';
    if (v.includes('ipf')) return 'IPF';
    if (v.includes('psg')) return 'PSG';
    if (v.includes('pcg')) return 'PCG';
    if (v.includes('team')) return 'Team Google';
    if (v.includes('internal') || v.includes('google')) return 'Internal Google';
    return val.trim() || 'Internal Google';
  };

  // Process RAW CSV / TSV text data
  const processTextData = (rawText: string, targetType: 'risk' | 'issue') => {
    setErrorMsg(null);
    setPreviewData([]);
    
    if (!rawText.trim()) {
      setErrorMsg("The uploaded file is empty.");
      return;
    }

    // Detect separator (Tab or Comma) based on first line
    const firstLineText = rawText.split(/\r?\n/)[0] || '';
    const separator = firstLineText.includes('\t') ? '\t' : ',';

    // Parse text into grid rows, handling quotes and multi-line fields properly
    const parseCSVOrTSV = (text: string, sep: string): string[][] => {
      const rows: string[][] = [];
      let currentRow: string[] = [];
      let currentCell = '';
      let inQuotes = false;
      
      for (let i = 0; i < text.length; i++) {
        const char = text[i];
        const nextChar = text[i + 1];
        
        if (char === '"') {
          if (inQuotes && nextChar === '"') {
            currentCell += '"';
            i++; // skip next quote
          } else {
            inQuotes = !inQuotes;
          }
        } else if (char === sep && !inQuotes) {
          currentRow.push(currentCell);
          currentCell = '';
        } else if ((char === '\n' || char === '\r') && !inQuotes) {
          if (char === '\r' && nextChar === '\n') {
            i++; // skip \n
          }
          currentRow.push(currentCell);
          if (currentRow.some(cell => cell.trim() !== '')) {
            rows.push(currentRow.map(val => val.replace(/^["']|["']$/g, '').trim()));
          }
          currentRow = [];
          currentCell = '';
        } else {
          currentCell += char;
        }
      }
      
      if (currentCell !== '' || currentRow.length > 0) {
        currentRow.push(currentCell);
      }
      if (currentRow.some(cell => cell.trim() !== '')) {
        rows.push(currentRow.map(val => val.replace(/^["']|["']$/g, '').trim()));
      }
      
      return rows;
    };

    const allRows = parseCSVOrTSV(rawText, separator);
    if (allRows.length < 2) {
      setErrorMsg("Insufficient data lines detected. First line must be column headers, followed by data rows.");
      return;
    }

    // Parse headers
    const rawHeaders = allRows[0];
    const mappedKeys = rawHeaders.map(h => matchHeaderToKey(h, targetType));
    
    setHeadersMatched(rawHeaders.map((h, i) => mappedKeys[i] ? `${h} ➜ ${mappedKeys[i]}` : `${h} (Skipped)`));

    const parsedRecords: any[] = [];
    
    for (let i = 1; i < allRows.length; i++) {
      const lineValues = allRows[i];
      const record: any = {};
      
      // Auto-assign values based on header mapping
      mappedKeys.forEach((key, keyIndex) => {
        if (key && lineValues[keyIndex] !== undefined) {
          const val = lineValues[keyIndex].trim();
          record[key] = val;
        }
      });

      // Default value fills for missing values
      if (targetType === 'risk') {
        const inheritL = parseRating(record.inherentLikelihood, null);
        const inheritC = parseRating(record.inherentConsequence, null);
        const residL = parseRating(record.residualLikelihood, null);
        const residC = parseRating(record.residualConsequence, null);

        const inheritScore = (inheritL !== null && inheritC !== null) 
          ? getMatrixScore(inheritL, inheritC) 
          : (parseRating(record.inherentRiskScore, null) ?? null);

        const residScore = (residL !== null && residC !== null) 
          ? getMatrixScore(residL, residC) 
          : (parseRating(record.residualRiskScore, null) ?? null);

        const cleanRecord: Partial<RiskTicket> = {
          id: record.id || `RSK-${String(existingCount + i).padStart(3, '0')}`,
          status: parseRiskStatus(record.status),
          riskOwner: record.riskOwner || 'Unassigned',
          bundle: record.bundle || 'Default Workstream',
          driverTreeRef: record.driverTreeRef || undefined,
          riskName: record.riskName || `Imported Risk #${i}`,
          riskDescription: record.riskDescription || 'IF [Event], THEN [Consequence]',
          causeDescription: record.causeDescription || 'No root cause provided.',
          causeCategory: parseCauseCategory(record.causeCategory),
          consequenceDescription: record.consequenceDescription || 'No consequence details provided.',
          trend: parseRiskTrend(record.trend),
          priority: parseRiskPriority(record.priority),
          governanceLevel: parseGovernanceLevel(record.governanceLevel),
          
          inherentLikelihood: inheritL,
          inherentConsequence: inheritC,
          inherentRiskScore: inheritScore,
          inherentRiskLevel: calculateRiskLevel(inheritScore),
          
          treatmentOwner: record.treatmentOwner || record.riskOwner || 'Unassigned',
          treatmentPlan: record.treatmentPlan || 'No treatment details defined yet.',
          targetDate: record.targetDate || todayStr,
          
          residualLikelihood: residL,
          residualConsequence: residC,
          residualRiskScore: residScore,
          residualRiskLevel: calculateRiskLevel(residScore),
          
          dateRaised: record.dateRaised || todayStr,
          dateClosed: record.dateClosed || undefined,
          
          relatedIssueId: record.relatedIssueId || undefined,
          riskLastUpdated: record.riskLastUpdated || todayStr,
          comments: record.comments || undefined,
          protectedIssueRisk: record.protectedIssueRisk || 'No',
          dpeRefNumber: record.dpeRefNumber || undefined,
          timelines: record.timelines || undefined,
          signOffRequirement: record.signOffRequirement || undefined,
          executiveStatus: record.executiveStatus || 'Pending',
          nextMitigationDueDate: record.nextMitigationDueDate || record.targetDate || todayStr,
          mitigationStatus: record.mitigationStatus || 'Pending',
          strategy: record.strategy || 'N/A',
          whoRaised: record.whoRaised || 'CSV Batch Import'
        };
        parsedRecords.push(cleanRecord);
      } else {
        // Issue defaults mapping
        const cleanRecord: Partial<IssueTicket> = {
          id: record.id || `ISS-${String(existingCount + i).padStart(3, '0')}`,
          status: record.status || 'Open',
          relatedRiskId: record.relatedRiskId || '',
          issueOwner: record.issueOwner || 'Unassigned',
          bundle: record.bundle || 'Default Workstream',
          driverTreeRef: record.driverTreeRef || undefined,
          issueName: record.issueName || `Imported Issue #${i}`,
          issueDescription: record.issueDescription || 'No description provided.',
          causeDescription: record.causeDescription || 'No cause description defined.',
          impactCategory: record.impactCategory || 'Operational',
          consequence: record.consequence || 'No consequence details.',
          trend: record.trend || 'Stable',
          priorityRating: record.priorityRating || 'Prompt',
          escalateTo: record.escalateTo || '',
          severityRating: record.severityRating || 'Medium',
          actionPlan: record.actionPlan || 'No action plan created.',
          nextActionOwner: record.nextActionOwner || record.issueOwner || 'Unassigned',
          dateRaised: record.dateRaised || todayStr,
          raisedBy: record.raisedBy || 'CSV Batch Import',
          dateClosed: record.dateClosed || undefined,
          lastUpdated: record.lastUpdated || todayStr,
          protectedIssueRisk: record.protectedIssueRisk === 'Yes' ? 'Yes' : 'No',
          dpeRefNumber: record.dpeRefNumber || ''
        };
        parsedRecords.push(cleanRecord);
      }
    }

    if (parsedRecords.length === 0) {
      setErrorMsg("No valid records could be processed. Please check headers format.");
    } else {
      setPreviewData(parsedRecords);
    }
  };

  // CSV file reading
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setRawTextContent(text);
      processTextData(text, importTarget);
    };
    reader.readAsText(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (!file) return;
    setFileName(file.name);
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setRawTextContent(text);
      processTextData(text, importTarget);
    };
    reader.readAsText(file);
  };

  const executeImport = () => {
    if (previewData.length === 0) return;
    
    if (importTarget === 'risk' && onImportRisks) {
      onImportRisks(previewData);
    } else if (importTarget === 'issue' && onImportIssues) {
      onImportIssues(previewData);
    }

    // Reset states and close
    setRawTextContent('');
    setPreviewData([]);
    setFileName('');
    onClose();
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          className="bg-white rounded-2xl shadow-xl border border-slate-200/80 w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/60">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl">
                <Database className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-800">
                  Import Corporate Data — {importTarget === 'risk' ? 'Risk Register' : 'Issue Register'}
                </h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Batch import records separately into your Risk Register or Issue Register via CSV or TSV spreadsheet files.
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-slate-200/80 text-slate-400 hover:text-slate-600 rounded-lg transition-colors cursor-pointer"
            >
              <X className="w-4.5 h-4.5" />
            </button>
          </div>

          {/* Dialog Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Import Target Tabs (Import Risk vs Import Issue) */}
            <div>
              <label className="block text-xs font-bold text-slate-600 mb-1.5">
                Select Destination Register:
              </label>
              <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 max-w-md text-xs font-semibold shadow-inner">
                <button
                  type="button"
                  onClick={() => setImportTarget('risk')}
                  className={`flex-1 py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    importTarget === 'risk' 
                      ? 'bg-white shadow-xs text-indigo-700 font-extrabold border border-slate-200/60' 
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <ShieldAlert className={`w-4 h-4 ${importTarget === 'risk' ? 'text-indigo-600' : 'text-slate-400'}`} />
                  Import Risks
                </button>
                <button
                  type="button"
                  onClick={() => setImportTarget('issue')}
                  className={`flex-1 py-2.5 px-4 rounded-lg flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    importTarget === 'issue' 
                      ? 'bg-white shadow-xs text-indigo-700 font-extrabold border border-slate-200/60' 
                      : 'text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <AlertCircle className={`w-4 h-4 ${importTarget === 'issue' ? 'text-amber-600' : 'text-slate-400'}`} />
                  Import Issues
                </button>
              </div>
            </div>

            {/* File Upload Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-colors cursor-pointer select-none ${
                dragOver ? 'border-indigo-500 bg-indigo-50/20' : 'border-slate-200 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-300'
              }`}
            >
              <input
                type="file"
                accept=".csv,.tsv,.txt"
                ref={fileInputRef}
                onChange={handleFileUpload}
                className="hidden"
              />
              <div className="p-3 bg-white border border-slate-100 rounded-xl shadow-xs text-slate-400">
                <Upload className="w-6 h-6 text-indigo-500" />
              </div>
              <div className="text-center">
                <p className="text-xs font-bold text-slate-700">
                  {fileName ? `Loaded: ${fileName}` : `Drag & drop CSV spreadsheet file for ${importTarget === 'risk' ? 'Risks' : 'Issues'}`}
                </p>
                <p className="text-[11px] text-slate-400 mt-1">
                  Supports .csv, .tsv, or .txt format
                </p>
              </div>
            </div>

            {/* Error Feedback */}
            {errorMsg && (
              <div className="p-3.5 bg-red-50 border border-red-100 rounded-xl text-xs text-red-700 flex items-start gap-2.5">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                <div>
                  <span className="font-bold">Parsing Error</span>
                  <p className="mt-0.5 text-[11px] text-red-600">{errorMsg}</p>
                </div>
              </div>
            )}

            {/* Match headers / Preview Section */}
            {previewData.length > 0 && (
              <div className="space-y-4 pt-2">
                <div className="border-t border-slate-100 pt-4">
                  <h4 className="text-xs font-bold text-slate-700 mb-2">Column Headers Association Diagnostics:</h4>
                  <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto p-3 bg-slate-50 border border-slate-100 rounded-xl">
                    {headersMatched.map((match, idx) => (
                      <span 
                        key={idx} 
                        className={`text-[9px] px-2 py-0.5 rounded-md font-bold tracking-tight border ${
                          match.includes('Skipped') 
                            ? 'bg-slate-100 text-slate-500 border-slate-200' 
                            : 'bg-emerald-50 text-emerald-700 border-emerald-100'
                        }`}
                      >
                        {match}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-xs font-bold text-slate-700">
                      High-Fidelity Preview ({previewData.length} active {importTarget === 'risk' ? 'risk' : 'issue'} records analyzed)
                    </h4>
                    <span className="text-[10px] text-emerald-600 font-bold flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" /> Parsed & Validated
                    </span>
                  </div>

                  <div className="bg-slate-50 border border-slate-150 rounded-xl overflow-hidden max-h-56 overflow-y-auto">
                    <table className="w-full table-auto border-collapse text-left text-[11px]">
                      <thead className="bg-slate-100/80 sticky top-0 border-b border-slate-200/60 font-bold text-slate-600">
                        <tr>
                          <th className="px-3 py-2">ID</th>
                          <th className="px-3 py-2">Title / Name</th>
                          <th className="px-3 py-2">Owner</th>
                          <th className="px-3 py-2">Workstream</th>
                          {importTarget === 'risk' ? (
                            <>
                              <th className="px-3 py-2 text-center">Inherent Risk</th>
                              <th className="px-3 py-2 text-center">Residual Risk</th>
                            </>
                          ) : (
                            <>
                              <th className="px-3 py-2">Severity</th>
                              <th className="px-3 py-2">Status</th>
                            </>
                          )}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 text-slate-700">
                        {previewData.map((row, idx) => (
                          <tr key={idx} className="hover:bg-slate-100/50 transition-colors">
                            <td className="px-3 py-2 font-mono text-indigo-600 font-semibold">{row.id}</td>
                            <td className="px-3 py-2 font-medium max-w-xs truncate">{importTarget === 'risk' ? row.riskName : row.issueName}</td>
                            <td className="px-3 py-2 text-slate-500">{importTarget === 'risk' ? row.riskOwner : row.issueOwner}</td>
                            <td className="px-3 py-2 text-slate-500">{row.bundle}</td>
                            {importTarget === 'risk' ? (
                              <>
                                <td className="px-3 py-2 text-center">
                                  <span className="text-[9px] px-1.5 py-0.5 bg-rose-50 text-rose-700 font-bold rounded">
                                    L{row.inherentLikelihood}&times;C{row.inherentConsequence} ({row.inherentRiskLevel})
                                  </span>
                                </td>
                                <td className="px-3 py-2 text-center">
                                  <span className="text-[9px] px-1.5 py-0.5 bg-indigo-50 text-indigo-700 font-bold rounded">
                                    L{row.residualLikelihood}&times;C{row.residualConsequence} ({row.residualRiskLevel})
                                  </span>
                                </td>
                              </>
                            ) : (
                              <>
                                <td className="px-3 py-2">
                                  <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                                    row.severityRating === 'Critical' ? 'bg-red-100 text-red-700' :
                                    row.severityRating === 'High' ? 'bg-orange-100 text-orange-700' : 'bg-slate-100 text-slate-700'
                                  }`}>
                                    {row.severityRating}
                                  </span>
                                </td>
                                <td className="px-3 py-2">
                                  <span className="text-[9px] px-1.5 py-0.5 bg-emerald-50 text-emerald-700 font-bold rounded">
                                    {row.status}
                                  </span>
                                </td>
                              </>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer Action Buttons */}
          <div className="p-4 border-t border-slate-100 bg-slate-50/60 flex items-center justify-between">
            <span className="text-[11px] text-slate-400">
              * Any columns not found will automatically be pre-filled with logical defaults.
            </span>
            <div className="flex gap-2">
              <button
                onClick={onClose}
                className="px-4 py-2 text-xs font-bold text-slate-500 hover:text-slate-700 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer"
              >
                Cancel
              </button>
              <button
                disabled={previewData.length === 0}
                onClick={executeImport}
                className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-200 disabled:text-slate-400 rounded-lg transition-all cursor-pointer shadow-sm flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" />
                Commit Batch to {importTarget === 'risk' ? 'Risk Register' : 'Issue Register'} ({previewData.length} records)
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
