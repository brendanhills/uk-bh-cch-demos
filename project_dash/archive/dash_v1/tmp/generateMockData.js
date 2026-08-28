const fs = require('fs');

function parseCSV(text) {
  const lines = [];
  let cur = '';
  let inQuotes = false;
  
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];
    
    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        cur += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === '\n' && !inQuotes) {
      lines.push(cur);
      cur = '';
    } else if (char === '\r' && !inQuotes) {
      // ignore CR
    } else {
      cur += char;
    }
  }
  if (cur.trim()) lines.push(cur);

  const rows = [];
  for (const line of lines) {
    const fields = [];
    let field = '';
    let inQ = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      const nc = line[i+1];
      if (c === '"') {
        if (inQ && nc === '"') {
          field += '"';
          i++;
        } else {
          inQ = !inQ;
        }
      } else if (c === ',' && !inQ) {
        fields.push(field);
        field = '';
      } else {
        field += c;
      }
    }
    fields.push(field);
    rows.push(fields);
  }
  return rows;
}

// Map likelihood text to number (1-5 or null)
function parseLikelihood(val) {
  if (!val || val === 'N/A' || val === 'No Data') return null;
  const match = val.match(/^(\d)/);
  if (match) return parseInt(match[1], 10);
  if (val.includes('1')) return 1;
  if (val.includes('2')) return 2;
  if (val.includes('3')) return 3;
  if (val.includes('4')) return 4;
  if (val.includes('5')) return 5;
  return null;
}

// Map consequence text to number (1-5 or null)
function parseConsequence(val) {
  if (!val || val === 'N/A' || val === 'No Data') return null;
  const match = val.match(/^(\d)/);
  if (match) return parseInt(match[1], 10);
  const lower = val.toLowerCase();
  if (lower.includes('minor')) return 1;
  if (lower.includes('moderate')) return 2;
  if (lower.includes('major')) return 3;
  if (lower.includes('critical')) return 4;
  if (lower.includes('catastrophic')) return 5;
  return null;
}

const issuesRaw = fs.readFileSync('/tmp/raw_issues.csv', 'utf8');
const issuesRows = parseCSV(issuesRaw);
const issuesHeader = issuesRows[0];
const issuesData = issuesRows.slice(1);

console.log(`Parsed ${issuesData.length} issue rows`);

const mockIssues = issuesData.map(row => {
  return {
    id: row[0] || '',
    status: row[1] || '',
    relatedRiskId: row[2] || 'N/A',
    issueOwner: row[3] || '',
    bundle: row[4] || 'N/A',
    driverTreeRef: row[5] || 'N/A',
    issueName: row[6] || '',
    issueDescription: row[7] || 'N/A',
    causeDescription: row[8] || 'N/A',
    impactCategory: row[9] || 'N/A',
    consequence: row[10] || 'N/A',
    trend: row[11] || 'N/A',
    priorityRating: row[12] || 'N/A',
    escalateTo: row[13] || 'N/A',
    severityRating: row[14] || 'N/A',
    actionPlan: row[15] || 'N/A',
    nextActionOwner: row[16] || 'N/A',
    dateRaised: row[17] || 'N/A',
    raisedBy: row[18] || 'N/A',
    dateClosed: row[19] || 'N/A',
    lastUpdated: row[20] || 'N/A',
    protectedIssueRisk: row[21] || 'N/A',
    dpeRefNumber: row[22] || 'N/A'
  };
});

const risksRaw = fs.readFileSync('/tmp/raw_risks.csv', 'utf8');
const risksRows = parseCSV(risksRaw);
const risksHeader = risksRows[0];
const risksData = risksRows.slice(1);

console.log(`Parsed ${risksData.length} risk rows`);

const mockRisks = risksData.map(row => {
  const inherentLikelihood = parseLikelihood(row[14]);
  const inherentConsequence = parseConsequence(row[15]);
  const residualLikelihood = parseLikelihood(row[20]);
  const residualConsequence = parseConsequence(row[21]);

  return {
    id: row[0] || '',
    status: row[1] || '',
    relatedIssueId: row[2] || 'N/A',
    riskOwner: row[3] || '',
    bundle: row[4] || 'N/A',
    driverTreeRef: row[5] || 'N/A',
    riskName: row[6] || '',
    riskDescription: row[7] || '',
    causeDescription: row[8] || '',
    causeCategory: row[9] || 'N/A',
    consequenceDescription: row[10] || '',
    trend: row[11] || 'N/A',
    priority: row[12] || 'N/A',
    governanceLevel: row[13] || 'N/A',
    
    inherentLikelihood: inherentLikelihood,
    inherentConsequence: inherentConsequence,
    inherentRiskLevel: row[16] || 'N/A',
    
    treatmentOwner: row[17] || '',
    treatmentPlan: row[18] || '',
    targetDate: row[19] || '',
    
    residualLikelihood: residualLikelihood,
    residualConsequence: residualConsequence,
    residualRiskLevel: row[22] || 'N/A',
    
    dateRaised: row[23] || '',
    dateClosed: row[24] || '',
    riskLastUpdated: row[25] || '',
    comments: row[26] || '',
    protectedIssueRisk: row[27] || '',
    dpeRefNumber: row[28] || '',
    timelines: row[29] || '',
    signOffRequirement: row[30] || '',
    executiveStatus: row[31] || '',
    nextMitigationDueDate: row[32] || '',
    mitigationStatus: row[33] || '',
    strategy: row[34] || '',
    whoRaised: row[35] || ''
  };
});

const fileContent = `/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { RiskTicket, IssueTicket, getMatrixScore, calculateRiskLevel } from '../types';

export const INITIAL_MOCK_ISSUE_TICKETS: IssueTicket[] = ${JSON.stringify(mockIssues, null, 2)};

export const INITIAL_MOCK_RISK_TICKETS: RiskTicket[] = ${JSON.stringify(mockRisks, null, 2)}.map(t => {
  const inherentRiskScore = getMatrixScore(t.inherentLikelihood, t.inherentConsequence);
  const residualRiskScore = getMatrixScore(t.residualLikelihood, t.residualConsequence);
  return {
    ...t,
    inherentRiskScore,
    residualRiskScore
  };
});
`;

fs.writeFileSync('/src/data/mockData.ts', fileContent);
console.log('Successfully wrote /src/data/mockData.ts');
