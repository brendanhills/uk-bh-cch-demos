/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { RiskTicket, IssueTicket, calculateRiskLevel } from '../types';
import { parseFlexibleDate } from './dateUtils';

export interface GoogleSheetsSyncConfig {
  sheetUrlOrId: string;
  gid?: string;
  autoRefreshIntervalMs?: number; // e.g. 60000 (1 min)
}

/**
 * Extracts Spreadsheet ID and GID from a full Google Sheets URL or ID string
 */
export function parseGoogleSheetUrl(urlOrId: string): { sheetId: string; gid: string } {
  if (!urlOrId) return { sheetId: '', gid: '0' };
  
  // If it's already a raw ID without slashes
  if (!urlOrId.includes('/') && !urlOrId.includes('.')) {
    return { sheetId: urlOrId.trim(), gid: '0' };
  }

  // Regex to match Google Sheet URL patterns:
  // https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0
  const matchId = urlOrId.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
  const sheetId = matchId ? matchId[1] : urlOrId;

  const matchGid = urlOrId.match(/[#&?]gid=([0-9]+)/);
  const gid = matchGid ? matchGid[1] : '0';

  return { sheetId, gid };
}

/**
 * Parses CSV text into array of object rows
 */
export function parseCSV(csvText: string): Record<string, string>[] {
  const lines = csvText.split(/\r?\n/).filter(line => line.trim() !== '');
  if (lines.length === 0) return [];

  // Parse header row
  const headers = parseCSVLine(lines[0]);
  const rows: Record<string, string>[] = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    if (values.length === 0 || (values.length === 1 && !values[0])) continue;
    
    const row: Record<string, string> = {};
    headers.forEach((header, idx) => {
      const cleanHeader = header.trim().toLowerCase().replace(/[^a-z0-9]/g, '');
      row[cleanHeader] = (values[idx] || '').trim();
      row[header.trim()] = (values[idx] || '').trim();
    });
    rows.push(row);
  }

  return rows;
}

function parseCSVLine(line: string): string[] {
  const result: string[] = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
}

/**
 * Maps raw spreadsheet rows to RiskTicket objects
 */
export function mapRowsToRiskTickets(rows: Record<string, string>[]): RiskTicket[] {
  return rows.map((row, index) => {
    const getVal = (...keys: string[]): string => {
      for (const k of keys) {
        const clean = k.toLowerCase().replace(/[^a-z0-9]/g, '');
        if (row[clean] !== undefined && row[clean] !== '') return row[clean];
        if (row[k] !== undefined && row[k] !== '') return row[k];
      }
      return '';
    };

    const id = getVal('Risk ID', 'ID', 'RiskID') || `RSK-${String(index + 1).padStart(3, '0')}`;
    const riskName = getVal('Risk Name', 'Title', 'Name', 'Risk') || 'Untitled Risk';
    const riskDescription = getVal('Risk Description', 'Description', 'Detail') || '';
    const causeDescription = getVal('Cause Description', 'Cause', 'Root Cause') || '';
    const causeCategory = getVal('Cause Category', 'Category', 'Risk Category') || 'Governance';
    const consequenceDescription = getVal('Consequence Description', 'Consequence', 'Impact Description') || '';
    const riskOwner = getVal('Risk Owner', 'Owner', 'Lead') || 'Unassigned';
    const treatmentOwner = getVal('Treatment Owner', 'Mitigation Owner', 'Action Owner') || riskOwner;
    const treatmentPlan = getVal('Treatment Plan', 'Mitigation Plan', 'Action Plan') || '';
    const status = getVal('Status', 'Risk Status', 'State') || 'Active';
    const trend = getVal('Trend', 'Risk Trend', 'Direction') || 'Same';
    const priority = getVal('Priority', 'Risk Priority') || 'Medium';
    const governanceLevel = getVal('Governance Level', 'Escalation', 'Governance') || 'Internal Google';
    const bundle = getVal('Bundle', 'Workstream') || 'F-DSE';
    const driverTreeRef = getVal('Driver Tree Ref', 'Driver Tree', 'Driver Ref') || '1.10b';
    
    // Inherent ratings
    const inLikelihood = parseInt(getVal('Inherent Likelihood', 'Inherent L'), 10) || 3;
    const inConsequence = parseInt(getVal('Inherent Consequence', 'Inherent C'), 10) || 3;
    const inherentRiskScore = inLikelihood * inConsequence;
    const inherentRiskLevel = calculateRiskLevel(inherentRiskScore);

    // Residual ratings
    const resLikelihood = parseInt(getVal('Residual Likelihood', 'Residual L'), 10) || 2;
    const resConsequence = parseInt(getVal('Residual Consequence', 'Residual C'), 10) || 2;
    const residualRiskScore = resLikelihood * resConsequence;
    const residualRiskLevel = calculateRiskLevel(residualRiskScore);

    const dateRaised = parseFlexibleDate(getVal('Date Raised', 'Raised Date', 'Created Date')) || '2026-07-01';
    const targetDate = parseFlexibleDate(getVal('Target Date', 'Due Date', 'Target Resolution Date')) || '2026-08-31';
    const dateClosed = parseFlexibleDate(getVal('Date Closed', 'Closed Date', 'Resolved Date')) || undefined;

    return {
      id,
      riskName,
      riskDescription,
      causeDescription,
      causeCategory,
      consequenceDescription,
      riskOwner,
      treatmentOwner,
      treatmentPlan,
      status,
      trend,
      priority,
      governanceLevel,
      bundle,
      driverTreeRef,
      inherentLikelihood: inLikelihood,
      inherentConsequence: inConsequence,
      inherentRiskScore,
      inherentRiskLevel,
      residualLikelihood: resLikelihood,
      residualConsequence: resConsequence,
      residualRiskScore,
      residualRiskLevel,
      dateRaised,
      targetDate,
      dateClosed,
      comments: getVal('Comments', 'Notes', 'Remarks'),
      timelines: getVal('Timelines', 'Timeline'),
      signOffRequirement: getVal('Sign-off Requirement', 'SignOff'),
      mitigationStatus: getVal('Mitigation Status', 'Action Status') || 'In Progress'
    };
  });
}

/**
 * Fetches Google Sheet directly via published CSV export or public URL
 */
export async function fetchGoogleSheetData(sheetUrlOrId: string): Promise<RiskTicket[]> {
  const { sheetId, gid } = parseGoogleSheetUrl(sheetUrlOrId);
  if (!sheetId) throw new Error("Invalid Google Sheet URL or ID");

  // Google Sheets Direct Export URL format
  const exportUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/export?format=csv&gid=${gid}`;
  
  const response = await fetch(exportUrl);
  if (!response.ok) {
    throw new Error(`Failed to fetch Google Sheet (${response.status}: ${response.statusText})`);
  }

  const csvText = await response.text();
  const rows = parseCSV(csvText);
  return mapRowsToRiskTickets(rows);
}
