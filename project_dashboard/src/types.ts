/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type RiskStatus = string;
export type CauseCategory = string;
export type RiskTrend = string;
export type RiskPriority = string;
export type GovernanceLevel = string;
export type RiskLevel = string;

export interface RiskTicket {
  id: string; // e.g., "RSK-001"
  status: RiskStatus;
  riskOwner: string;
  bundle: string;
  driverTreeRef?: string;
  riskName: string;
  riskDescription: string; // IF [Event], THEN [Consequence]
  causeDescription: string;
  causeCategory: CauseCategory;
  consequenceDescription: string;
  trend: RiskTrend;
  priority: RiskPriority;
  governanceLevel: GovernanceLevel;
  
  // Inherent risk metrics
  inherentLikelihood: number | null; // 1 to 5 or null
  inherentConsequence: number | null; // 1 to 5 or null
  inherentRiskScore: number | null; // Likelihood * Consequence (1 to 25) or null
  inherentRiskLevel: RiskLevel;
  
  // Mitigation & Treatment
  treatmentOwner: string;
  treatmentPlan: string;
  targetDate: string; // YYYY-MM-DD
  
  // Residual risk metrics
  residualLikelihood: number | null; // 1 to 5 or null
  residualConsequence: number | null; // 1 to 5 or null
  residualRiskScore: number | null; // Likelihood * Consequence (1 to 25) or null
  residualRiskLevel: RiskLevel;
  
  dateRaised: string; // YYYY-MM-DD
  dateClosed?: string; // YYYY-MM-DD
  userId?: string; // Associated Firebase User ID

  // Additional 36-column spreadsheet attributes
  relatedIssueId?: string;
  riskLastUpdated?: string;
  comments?: string;
  protectedIssueRisk?: string;
  dpeRefNumber?: string;
  timelines?: string;
  signOffRequirement?: string;
  executiveStatus?: string;
  nextMitigationDueDate?: string;
  mitigationStatus?: string;
  strategy?: string;
  whoRaised?: string;
}

// Utility to calculate open days between raised date and closed date (or today if open)
export function calculateOpenDays(dateRaisedStr: string, dateClosedStr?: string): number {
  if (!dateRaisedStr) return 0;
  const raised = new Date(dateRaisedStr);
  if (isNaN(raised.getTime())) return 0;
  
  const closed = dateClosedStr && dateClosedStr !== '-' && dateClosedStr.trim() !== '' 
    ? new Date(dateClosedStr) 
    : new Date();
  if (isNaN(closed.getTime())) return 0;
  
  // Clear times to make date-only comparison
  raised.setHours(0, 0, 0, 0);
  closed.setHours(0, 0, 0, 0);
  
  const diffTime = closed.getTime() - raised.getTime();
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  return isNaN(diffDays) || diffDays < 0 ? 0 : diffDays;
}

// Utility to calculate risk level based on the standard 5x5 Risk Matrix score
export function calculateRiskLevel(score: number | null): RiskLevel {
  if (score === null || score === undefined || score === 0) return '-';
  if (score >= 23) return 'Very High';
  if (score >= 18) return 'High';
  if (score >= 13) return 'Medium';
  if (score >= 7) return 'Low';
  if (score >= 1) return 'Very Low';
  return '-';
}

// Map rating numbers to text descriptions
export const LIKELIHOOD_LABELS: Record<number, string> = {
  0: 'N/A',
  1: '1 Rare',
  2: '2 Improbable',
  3: '3 Occasional',
  4: '4 Probable',
  5: '5 Almost Certain',
  6: 'No Data',
};

export const CONSEQUENCE_LABELS: Record<number, string> = {
  0: 'N/A',
  1: 'Minor',
  2: 'Moderate',
  3: 'Major',
  4: 'Critical',
  5: 'Catastrophic',
  6: 'No Data',
};

export const MATRIX_SCORES: Record<number, Record<number, number>> = {
  5: { 1: 12, 2: 17, 3: 22, 4: 24, 5: 25 },
  4: { 1: 11, 2: 16, 3: 20, 4: 21, 5: 23 },
  3: { 1: 6,  2: 10, 3: 15, 4: 18, 5: 19 },
  2: { 1: 4,  2: 5,  3: 9,  4: 13, 5: 14 },
  1: { 1: 1,  2: 2,  3: 3,  4: 7,  5: 8  }
};

export function getMatrixScore(likelihood: number | null, consequence: number | null): number | null {
  if (likelihood === null || likelihood === undefined || consequence === null || consequence === undefined) return null;
  return MATRIX_SCORES[consequence]?.[likelihood] || (likelihood * consequence);
}

// Colors for Priority
export const PRIORITY_COLORS: Record<string, string> = {
  'Immediate': 'bg-red-50 text-red-700 border-red-200',
  'Urgent': 'bg-amber-50 text-amber-700 border-amber-200',
  'Prompt': 'bg-blue-50 text-blue-700 border-blue-200',
  'Not Urgent': 'bg-slate-50 text-slate-600 border-slate-200',
};

// Colors for Risk Level
export const RISK_LEVEL_COLORS: Record<string, { text: string, bg: string, border: string, darkBg: string }> = {
  'Critical': {
    text: 'text-red-700 font-extrabold',
    bg: 'bg-red-50',
    border: 'border-red-200',
    darkBg: 'bg-[#ea4335]',
  },
  'Very High': {
    text: 'text-red-700 font-extrabold',
    bg: 'bg-red-50',
    border: 'border-red-200',
    darkBg: 'bg-[#ea4335]',
  },
  'High': {
    text: 'text-orange-700 font-bold',
    bg: 'bg-orange-50',
    border: 'border-orange-200',
    darkBg: 'bg-[#ff9900]',
  },
  'Medium': {
    text: 'text-amber-800 font-bold',
    bg: 'bg-yellow-50',
    border: 'border-amber-200',
    darkBg: 'bg-[#fdfdb9]',
  },
  'Low': {
    text: 'text-emerald-800 font-bold',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    darkBg: 'bg-[#34a853]',
  },
  'Very Low': {
    text: 'text-green-700 font-bold',
    bg: 'bg-green-50',
    border: 'border-green-200',
    darkBg: 'bg-[#93c47d]',
  },
  '-': {
    text: 'text-slate-500 font-medium',
    bg: 'bg-slate-100',
    border: 'border-slate-200',
    darkBg: 'bg-slate-400',
  }
};

// Colors for Status
export const STATUS_COLORS: Record<string, string> = {
  'Active': 'bg-sky-50 text-sky-700 border-sky-200',
  'Closed': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'Transferred': 'bg-purple-50 text-purple-700 border-purple-200',
  'Retired': 'bg-gray-50 text-gray-600 border-gray-200',
  'Issue Eventuated': 'bg-amber-50 text-amber-700 border-amber-200',
};

export interface IssueTicket {
  id: string;
  status: string;
  relatedRiskId: string;
  issueOwner: string;
  bundle: string;
  driverTreeRef?: string;
  issueName: string;
  issueDescription: string;
  causeDescription: string;
  impactCategory: string;
  consequence: string;
  trend: string;
  priorityRating: string;
  escalateTo: string;
  severityRating: string;
  actionPlan: string;
  nextActionOwner?: string;
  dateRaised: string;
  raisedBy: string;
  dateClosed?: string;
  lastUpdated: string;
  protectedIssueRisk: string;
  dpeRefNumber: string;
  userId?: string;
}

export const DRIVER_TREE_REF_ORDERED_OPTIONS: string[] = [
  '1.1',
  '1.10a',
  '1.10b',
  '1.10c',
  '1.10d',
  '1.13',
  '1.14',
  '1.15',
  '1.16c',
  '1.17',
  '1.2',
  '1.2a',
  '1.2b',
  '1.3',
  '1.4',
  '1.5',
  '1.6',
  '1.7',
  '1.7a',
  '1.7b',
  '1.7c',
  '2',
  '2.1',
  '2.2',
  '2.3',
  '2.4',
  '3.1',
  '3.2',
  '4',
  '4.1',
  '4.2',
  '4.3',
  '4.4',
  '5.1',
  '5.2',
  '5.2a',
  '5.3',
  'N/A',
  'No Data'
];

export function isDriverTreeRefMatch(refField: string | undefined | null, targetRef: string): boolean {
  if (!targetRef) return false;
  const targetTrim = targetRef.trim();
  const targetNorm = targetTrim.toLowerCase().replace(/^(cd1[.-]?|item[.-]?|ref[.-]?)+/g, '').replace(/[\[\]]/g, '').trim();
  if (!targetNorm) return false;

  if (targetNorm === 'no data') {
    return !refField || !refField.trim() || refField.trim() === '-' || refField.trim() === 'N/A' || refField.trim().toLowerCase() === 'no data';
  }

  if (!refField) return false;
  const rawRef = refField.trim().toLowerCase();
  if (rawRef === targetTrim.toLowerCase()) return true;

  // Split by common delimiters: space, comma, semicolon, slash, dash, colon
  const tokens = rawRef.split(/[,;:\/\s-]+/).map(tok => 
    tok.replace(/^(cd1[.-]?|item[.-]?|ref[.-]?)+/g, '').replace(/[\[\]]/g, '').trim()
  ).filter(Boolean);

  for (const tok of tokens) {
    if (tok === targetNorm) return true;
    if ((targetNorm === '2.0' || targetNorm === '2') && (tok === '2' || tok === '2.0')) return true;
    if ((targetNorm === '4.0' || targetNorm === '4') && (tok === '4' || tok === '4.0')) return true;
  }

  // Check direct prefix match (e.g. "1.10b Platform Ready...")
  const cleanRaw = rawRef.replace(/^(cd1[.-]?|item[.-]?|ref[.-]?)+/g, '').replace(/[\[\]]/g, '').trim();
  if (cleanRaw.startsWith(targetNorm)) {
    const nextChar = cleanRaw[targetNorm.length];
    if (!nextChar || !/[a-z0-9]/i.test(nextChar)) {
      return true;
    }
  }

  return false;
}

