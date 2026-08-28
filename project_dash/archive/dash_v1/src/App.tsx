/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useMemo } from 'react';
import { RiskTicket, IssueTicket, calculateRiskLevel } from './types';
import { parseFlexibleDate } from './utils/dateUtils';
import { INITIAL_MOCK_RISK_TICKETS, INITIAL_MOCK_ISSUE_TICKETS } from './data/mockData';
import RiskMatrix from './components/RiskMatrix';
import WholeDataTab from './components/WholeDataTab';
import TrendsTab from './components/TrendsTab';
import DataEntryTab from './components/DataEntryTab';
import CD1DriverTree from './components/CD1DriverTree';
import IssueRegisterView from './components/IssueRegisterView';
import ImportDataModal from './components/ImportDataModal';
import { motion, AnimatePresence } from 'motion/react';
import { 
  ShieldAlert, 
  PlusCircle, 
  Table, 
  TrendingUp, 
  LayoutDashboard, 
  User, 
  Clock, 
  HelpCircle,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  Database,
  Wifi,
  WifiOff,
  Flame,
  Layers,
  AlertCircle,
  CheckCircle,
  TrendingDown,
  Briefcase,
  Activity,
  Calendar,
  Shield,
  ExternalLink,
  GitBranch
} from 'lucide-react';
const LOCAL_STORAGE_RISKS_KEY = 'risk_governance_tickets_db_v4';
const LOCAL_STORAGE_ISSUES_KEY = 'risk_governance_issues_db_v4';
const LOCAL_STORAGE_LAST_RISK_IMPORT_KEY = 'last_risk_import_timestamp_v1';
const LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY = 'last_issue_import_timestamp_v1';

export default function App() {
  const [user] = useState<any>({
    uid: "navjot_singh_default",
    displayName: "Navjot Singh",
    email: "navjotsngh@google.com",
    emailVerified: true
  });
  const [tickets, setTickets] = useState<RiskTicket[]>([]);
  const [issues, setIssues] = useState<IssueTicket[]>([]);
  const [lastRiskImportDate, setLastRiskImportDate] = useState<string>('');
  const [lastIssueImportDate, setLastIssueImportDate] = useState<string>('');
  const [appImportType, setAppImportType] = useState<'risk' | 'issue' | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'data-entry' | 'whole-data' | 'trends' | 'cd1-driver-tree' | 'issue-dashboard'>('overview');
  const [editingTicket, setEditingTicket] = useState<RiskTicket | null>(null);
  const [ticketToDelete, setTicketToDelete] = useState<string | null>(null);

  // Grid filter state populated via Risk Matrix cell clicks
  const [matrixFilter, setMatrixFilter] = useState<{ likelihood: number; consequence: number; type: 'inherent' | 'residual' } | null>(null);

  // Active filter overrides passed to WholeDataTab and IssueRegisterView
  const [overrideSearchTerm, setOverrideSearchTerm] = useState<string>('');
  const [overrideIssueSearchTerm, setOverrideIssueSearchTerm] = useState<string>('');
  const [overrideStatusFilter, setOverrideStatusFilter] = useState<string>('all');
  const [overrideGovFilter, setOverrideGovFilter] = useState<string>('all');
  const [overrideDriverTreeRefFilter, setOverrideDriverTreeRefFilter] = useState<string>('all');
  const [overrideDateFilter, setOverrideDateFilter] = useState<string>('all');

  const handleFilterNewRisks = () => {
    setOverrideDateFilter('7days');
    setOverrideSearchTerm('');
    setOverrideStatusFilter('all');
    setOverrideGovFilter('all');
    setOverrideDriverTreeRefFilter('all');
    setMatrixFilter(null);
    setActiveTab('whole-data');
  };

  const handleFilterClosedRisks = () => {
    setOverrideDateFilter('all');
    setOverrideStatusFilter('Closed');
    setOverrideSearchTerm('');
    setOverrideGovFilter('all');
    setOverrideDriverTreeRefFilter('all');
    setMatrixFilter(null);
    setActiveTab('whole-data');
  };

  const handleFilterLastUpdated = () => {
    setOverrideDateFilter('7days');
    setOverrideSearchTerm('');
    setOverrideStatusFilter('all');
    setOverrideGovFilter('all');
    setOverrideDriverTreeRefFilter('all');
    setMatrixFilter(null);
    setActiveTab('whole-data');
  };

  const handleFilterGovernance = (govLevel?: string) => {
    setOverrideGovFilter(govLevel || 'Internal Google');
    setOverrideDateFilter('all');
    setOverrideSearchTerm('');
    setOverrideStatusFilter('all');
    setOverrideDriverTreeRefFilter('all');
    setMatrixFilter(null);
    setActiveTab('whole-data');
  };

  // 1. Load initial data from localStorage or fallback to initial seed mock data on Mount
  useEffect(() => {
    const savedRisks = localStorage.getItem(LOCAL_STORAGE_RISKS_KEY);
    if (savedRisks) {
      try {
        const parsed = JSON.parse(savedRisks);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Keep only items that have valid structural IDs
          const sanitized = parsed.filter(t => t && t.id && !t.id.startsWith('-') && t.id.length < 50);
          if (sanitized.length > 0) {
            setTickets(sanitized);
          } else {
            setTickets(INITIAL_MOCK_RISK_TICKETS);
            localStorage.setItem(LOCAL_STORAGE_RISKS_KEY, JSON.stringify(INITIAL_MOCK_RISK_TICKETS));
          }
        } else {
          setTickets(INITIAL_MOCK_RISK_TICKETS);
          localStorage.setItem(LOCAL_STORAGE_RISKS_KEY, JSON.stringify(INITIAL_MOCK_RISK_TICKETS));
        }
      } catch (e) {
        console.error("Failed to parse saved risks:", e);
        setTickets(INITIAL_MOCK_RISK_TICKETS);
        localStorage.setItem(LOCAL_STORAGE_RISKS_KEY, JSON.stringify(INITIAL_MOCK_RISK_TICKETS));
      }
    } else {
      setTickets(INITIAL_MOCK_RISK_TICKETS);
      localStorage.setItem(LOCAL_STORAGE_RISKS_KEY, JSON.stringify(INITIAL_MOCK_RISK_TICKETS));
    }

    const savedIssues = localStorage.getItem(LOCAL_STORAGE_ISSUES_KEY);
    if (savedIssues) {
      try {
        const parsed = JSON.parse(savedIssues);
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Keep only items that have valid structural IDs
          const sanitized = parsed.filter(i => i && i.id && !i.id.startsWith('-') && i.id.length < 50);
          if (sanitized.length > 0) {
            setIssues(sanitized);
          } else {
            setIssues(INITIAL_MOCK_ISSUE_TICKETS);
            localStorage.setItem(LOCAL_STORAGE_ISSUES_KEY, JSON.stringify(INITIAL_MOCK_ISSUE_TICKETS));
          }
        } else {
          setIssues(INITIAL_MOCK_ISSUE_TICKETS);
          localStorage.setItem(LOCAL_STORAGE_ISSUES_KEY, JSON.stringify(INITIAL_MOCK_ISSUE_TICKETS));
        }
      } catch (e) {
        console.error("Failed to parse saved issues:", e);
        setIssues(INITIAL_MOCK_ISSUE_TICKETS);
        localStorage.setItem(LOCAL_STORAGE_ISSUES_KEY, JSON.stringify(INITIAL_MOCK_ISSUE_TICKETS));
      }
    } else {
      setIssues(INITIAL_MOCK_ISSUE_TICKETS);
      localStorage.setItem(LOCAL_STORAGE_ISSUES_KEY, JSON.stringify(INITIAL_MOCK_ISSUE_TICKETS));
    }

    const savedRiskImport = localStorage.getItem(LOCAL_STORAGE_LAST_RISK_IMPORT_KEY);
    if (savedRiskImport) {
      setLastRiskImportDate(savedRiskImport);
    } else {
      const defaultDate = '29 Jul 2026';
      setLastRiskImportDate(defaultDate);
      localStorage.setItem(LOCAL_STORAGE_LAST_RISK_IMPORT_KEY, defaultDate);
    }

    const savedIssueImport = localStorage.getItem(LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY);
    if (savedIssueImport) {
      setLastIssueImportDate(savedIssueImport);
    } else {
      const defaultDate = '29 Jul 2026';
      setLastIssueImportDate(defaultDate);
      localStorage.setItem(LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY, defaultDate);
    }
  }, []);

  // Sync state changes back to localStorage
  const saveTicketsState = (updatedTickets: RiskTicket[]) => {
    setTickets(updatedTickets);
    localStorage.setItem(LOCAL_STORAGE_RISKS_KEY, JSON.stringify(updatedTickets));
  };

  const saveIssuesState = (updatedIssues: IssueTicket[]) => {
    setIssues(updatedIssues);
    localStorage.setItem(LOCAL_STORAGE_ISSUES_KEY, JSON.stringify(updatedIssues));
  };

  // Generate next consecutive Risk ID (e.g., RSK-021)
  const getNextId = (): string => {
    if (tickets.length === 0) return 'RSK-001';
    
    const ids = tickets.map(t => {
      const numPart = t.id.split('-')[1];
      return parseInt(numPart) || 0;
    });
    
    const maxId = Math.max(...ids);
    const nextNum = maxId + 1;
    return `RSK-${String(nextNum).padStart(3, '0')}`;
  };

  // Action: Save or Update Ticket
  const handleSaveTicket = async (ticket: RiskTicket) => {
    let updated: RiskTicket[];
    const exists = tickets.some(t => t.id === ticket.id);
    if (exists) {
      updated = tickets.map(t => t.id === ticket.id ? ticket : t);
    } else {
      updated = [ticket, ...tickets];
    }
    saveTicketsState(updated);
    setEditingTicket(null);
    setActiveTab('whole-data'); // Redirect to ledger to see changes
  };

  // Action: Delete Ticket
  const handleDeleteTicket = (id: string) => {
    setTicketToDelete(id);
  };

  // Action: Confirm and Perform Delete
  const confirmDeleteTicket = async () => {
    if (!ticketToDelete) return;
    const updated = tickets.filter(t => t.id !== ticketToDelete);
    saveTicketsState(updated);
    
    // Clear matrix filter if it corresponds to the deleted ticket
    if (matrixFilter) {
      setMatrixFilter(null);
    }
    setTicketToDelete(null);
  };

  // Action: Trigger Edit Flow
  const handleEditTicket = (ticket: RiskTicket) => {
    setEditingTicket(ticket);
    setActiveTab('data-entry');
  };

  // Action: Save or Update Issue
  const handleSaveIssue = async (issue: IssueTicket) => {
    let updated: IssueTicket[];
    const exists = issues.some(i => i.id === issue.id);
    if (exists) {
      updated = issues.map(i => i.id === issue.id ? issue : i);
    } else {
      updated = [issue, ...issues];
    }
    saveIssuesState(updated);
  };

  // Action: Delete Issue
  const handleDeleteIssue = async (id: string) => {
    const updated = issues.filter(i => i.id !== id);
    saveIssuesState(updated);
  };

  // Action: Batch Import Risks (overwrites dataset as per requirements)
  const handleImportRisks = async (newRisks: RiskTicket[]) => {
    saveTicketsState(newRisks);

    const nowStr = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    setLastRiskImportDate(nowStr);
    localStorage.setItem(LOCAL_STORAGE_LAST_RISK_IMPORT_KEY, nowStr);
  };

  // Action: Batch Import Issues (overwrites dataset as per requirements)
  const handleImportIssues = async (newIssues: IssueTicket[]) => {
    saveIssuesState(newIssues);

    const nowStr = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    setLastIssueImportDate(nowStr);
    localStorage.setItem(LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY, nowStr);
  };

  // Action: Reset Registers to Default Mock Data
  const handleClearAllRegisters = async () => {
    localStorage.removeItem(LOCAL_STORAGE_RISKS_KEY);
    localStorage.removeItem(LOCAL_STORAGE_ISSUES_KEY);
    localStorage.removeItem(LOCAL_STORAGE_LAST_RISK_IMPORT_KEY);
    localStorage.removeItem(LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY);

    saveTicketsState(INITIAL_MOCK_RISK_TICKETS);
    saveIssuesState(INITIAL_MOCK_ISSUE_TICKETS);

    const defaultDate = '29 Jul 2026';
    setLastRiskImportDate(defaultDate);
    setLastIssueImportDate(defaultDate);
    localStorage.setItem(LOCAL_STORAGE_LAST_RISK_IMPORT_KEY, defaultDate);
    localStorage.setItem(LOCAL_STORAGE_LAST_ISSUE_IMPORT_KEY, defaultDate);
    setMatrixFilter(null);
  };

  // Trigger Matrix Cell Click Filter
  const handleMatrixCellClick = (likelihood: number, consequence: number, type: 'inherent' | 'residual') => {
    if (likelihood === 0 && consequence === 0) {
      setMatrixFilter(null);
    } else {
      setMatrixFilter({ likelihood, consequence, type });
      setOverrideStatusFilter('all');
      setOverrideSearchTerm('');
      setOverrideGovFilter('all');
      setOverrideDriverTreeRefFilter('all');
      setOverrideDateFilter('all');
      setActiveTab('whole-data'); // Redirect to the ledger instantly with filter pre-filled
    }
  };

  // Quick list of active critical items for the overview panel
  const criticalBacklog = useMemo(() => tickets.filter(t => t.status !== 'Closed' && (t.inherentRiskLevel === 'Very High' || t.inherentRiskLevel === 'Critical')), [tickets]);
  const totalActiveRisks = useMemo(() => tickets.filter(t => t.status !== 'Closed').length, [tickets]);
  
  // Dashboard Metrics & Calculations
  const activeRisks = useMemo(() => tickets.filter(t => t.status !== 'Closed'), [tickets]);
  const criticalRisksCount = useMemo(() => activeRisks.filter(t => t.inherentRiskLevel === 'Very High' || t.inherentRiskLevel === 'Critical').length, [activeRisks]);
  const highRisksCount = useMemo(() => activeRisks.filter(t => t.inherentRiskLevel === 'High').length, [activeRisks]);
  const medRisksCount = useMemo(() => activeRisks.filter(t => t.inherentRiskLevel === 'Medium').length, [activeRisks]);
  const lowRisksCount = useMemo(() => activeRisks.filter(t => t.inherentRiskLevel === 'Low').length, [activeRisks]);
  const veryLowRisksCount = useMemo(() => activeRisks.filter(t => t.inherentRiskLevel === 'Very Low').length, [activeRisks]);

  const totalOpenIssues = useMemo(() => issues.filter(i => i.status !== 'Closed' && i.status !== 'Resolved').length, [issues]);
  const highSeverityIssuesCount = useMemo(() => issues.filter(i => 
    i.status !== 'Closed' && 
    i.status !== 'Resolved' && 
    (i.severityRating === 'Critical' || i.severityRating === 'High')
  ).length, [issues]);

  // Average Scores and Mitigation Efficiency
  const { avgInherent, avgResidual, mitigationRatePct } = useMemo(() => {
    const totalInherentScore = activeRisks.reduce((sum, t) => sum + (t.inherentRiskScore || 0), 0);
    const totalResidualScore = activeRisks.reduce((sum, t) => sum + (t.residualRiskScore || 0), 0);
    const avgInherentVal = activeRisks.length > 0 ? (totalInherentScore / activeRisks.length) : 0;
    const avgResidualVal = activeRisks.length > 0 ? (totalResidualScore / activeRisks.length) : 0;
    const pct = avgInherentVal > 0 
      ? Math.round(((avgInherentVal - avgResidualVal) / avgInherentVal) * 100) 
      : 0;
    return { avgInherent: avgInherentVal, avgResidual: avgResidualVal, mitigationRatePct: pct };
  }, [activeRisks]);

  // SLA Overdue Actions (comparing against today's date)
  const { risksWithTarget, overdueRisksCount, slaCompliancePct } = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const withTarget = activeRisks.filter(t => parseFlexibleDate(t.targetDate) !== null);
    const overdueCount = activeRisks.filter(t => {
      const dTarget = parseFlexibleDate(t.targetDate);
      return dTarget !== null && dTarget < today;
    }).length;
    const sla = withTarget.length > 0 
      ? Math.round(((withTarget.length - overdueCount) / withTarget.length) * 100)
      : 100;
    return { risksWithTarget: withTarget, overdueRisksCount: overdueCount, slaCompliancePct: sla };
  }, [activeRisks]);

  // Key Highlights Specific Calculations:
  const {
    risksRaisedLast7DaysCount,
    totalRaisedCount,
    risksClosedLast7DaysCount,
    totalClosedCount,
    risksUpdatedLast7DaysCount,
    totalUpdatedCount,
    internalGovCount,
    teamGovCount,
    ipfGovCount,
    psgPcgGovCount,
    escalatedGovCount
  } = useMemo(() => {
    const isWithinLast7Days = (dateStr?: string): boolean => {
      const d = parseFlexibleDate(dateStr);
      if (!d) return false;

      const now = new Date();
      const sevenDaysAgo = new Date();
      sevenDaysAgo.setDate(now.getDate() - 7);
      sevenDaysAgo.setHours(0, 0, 0, 0);

      const endOfToday = new Date();
      endOfToday.setHours(23, 59, 59, 999);

      return d >= sevenDaysAgo && d <= endOfToday;
    };

    const raised7 = tickets.filter(t => isWithinLast7Days(t.dateRaised)).length;
    const totRaised = tickets.filter(t => t.dateRaised && t.dateRaised !== '-' && t.dateRaised.trim() !== '').length;
    const closed7 = tickets.filter(t => isWithinLast7Days(t.dateClosed)).length;
    const totClosed = tickets.filter(t => t.status === 'Closed' || (t.dateClosed && t.dateClosed !== '-' && t.dateClosed.trim() !== '')).length;
    const updated7 = tickets.filter(t => isWithinLast7Days(t.riskLastUpdated)).length;
    const totUpdated = tickets.filter(t => t.riskLastUpdated && t.riskLastUpdated !== '-' && t.riskLastUpdated.trim() !== '').length;

    const internal = tickets.filter(t => t.governanceLevel === 'Internal Google').length;
    const team = tickets.filter(t => t.governanceLevel === 'Team Google').length;
    const ipf = tickets.filter(t => t.governanceLevel === 'IPF').length;
    const psgPcg = tickets.filter(t => t.governanceLevel === 'PSG' || t.governanceLevel === 'PCG').length;
    const esc = tickets.length - internal;

    return {
      risksRaisedLast7DaysCount: raised7,
      totalRaisedCount: totRaised,
      risksClosedLast7DaysCount: closed7,
      totalClosedCount: totClosed,
      risksUpdatedLast7DaysCount: updated7,
      totalUpdatedCount: totUpdated,
      internalGovCount: internal,
      teamGovCount: team,
      ipfGovCount: ipf,
      psgPcgGovCount: psgPcg,
      escalatedGovCount: esc
    };
  }, [tickets]);



  return (
    <div className="min-h-screen bg-slate-50/50 flex flex-col font-sans text-slate-800">
      
      {/* Top Professional Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          
          <div className="flex items-center gap-3">
            <div className="bg-red-50 text-red-600 p-2 rounded-xl shadow-xs border border-red-200">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-extrabold text-slate-900 tracking-tight">
                Risk and Issue Interactive Dashboard
              </h1>
            </div>
          </div>

          {/* Far Right: Dashboard Last Updated & Import Registers */}
          <div className="flex flex-wrap items-center gap-2 sm:gap-3 self-end sm:self-auto">
            <div className="bg-slate-50 border border-slate-200/90 rounded-xl px-3.5 py-1.5 flex items-center gap-2.5 shadow-2xs">
              <Clock className="w-4 h-4 text-indigo-600 shrink-0" />
              <div className="flex flex-col">
                <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider leading-none">
                  Dashboard Last Updated
                </span>
                <div className="flex items-center gap-2.5 mt-1 text-[11px] font-mono">
                  <span className="text-slate-700 font-medium">
                    <span className="text-indigo-600 font-bold">Risk Reg:</span> {lastRiskImportDate || '29 Jul 2026'}
                  </span>
                  <span className="text-slate-300">|</span>
                  <span className="text-slate-700 font-medium">
                    <span className="text-amber-600 font-bold">Issue Reg:</span> {lastIssueImportDate || '29 Jul 2026'}
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </header>

      {/* Primary Dashboard Navigation Layout */}
      <div className="max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6 flex-1 flex flex-col gap-6">
        
        {/* Navigation Tabs Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-2">
          
          <nav className="flex overflow-x-auto no-scrollbar max-w-full gap-2 bg-slate-200/70 p-1.5 rounded-xl border border-slate-300/60 shadow-xs self-start">
            {/* Tab 1: Risk Dashboard */}
            <button
              onClick={() => {
                setActiveTab('overview');
                setEditingTicket(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                activeTab === 'overview'
                  ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                  : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <LayoutDashboard className={`w-4 h-4 ${activeTab === 'overview' ? 'text-white' : 'text-slate-500'}`} />
              Risk Dashboard
            </button>

            {/* Tab 2: Issue Dashboard */}
            <button
              onClick={() => {
                setActiveTab('issue-dashboard');
                setEditingTicket(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                activeTab === 'issue-dashboard'
                  ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                  : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <AlertCircle className={`w-4 h-4 ${activeTab === 'issue-dashboard' ? 'text-amber-300' : 'text-amber-600'}`} />
              Issue Dashboard
            </button>

            {/* Tab 3: Performance Trends */}
            <button
              onClick={() => {
                setActiveTab('trends');
                setEditingTicket(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                activeTab === 'trends'
                  ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                  : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <TrendingUp className={`w-4 h-4 ${activeTab === 'trends' ? 'text-white' : 'text-slate-500'}`} />
              Performance Trends
            </button>

            {/* Tab 4: CD1 Driver Tree */}
            <button
              onClick={() => {
                setActiveTab('cd1-driver-tree');
                setEditingTicket(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                activeTab === 'cd1-driver-tree'
                  ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                  : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <GitBranch className={`w-4 h-4 ${activeTab === 'cd1-driver-tree' ? 'text-white' : 'text-indigo-600'}`} />
              CD1 Driver Tree
            </button>

            {/* Tab 5: Whole Register Ledger */}
            <button
              onClick={() => {
                setActiveTab('whole-data');
                setEditingTicket(null);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                activeTab === 'whole-data'
                  ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                  : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
              }`}
            >
              <Table className={`w-4 h-4 ${activeTab === 'whole-data' ? 'text-white' : 'text-slate-500'}`} />
              Whole Register Ledger
            </button>

            {/* Tab 6: Data Entry / Edit (Conditional) */}
            {(activeTab === 'data-entry' || editingTicket) && (
              <button
                onClick={() => setActiveTab('data-entry')}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-bold transition-all duration-200 cursor-pointer select-none ${
                  activeTab === 'data-entry'
                    ? 'bg-indigo-600 text-white border border-indigo-700 shadow-md shadow-indigo-600/25 -translate-y-0.5'
                    : 'bg-white text-slate-700 border border-slate-200/90 shadow-2xs hover:bg-indigo-50/70 hover:text-indigo-700 hover:border-indigo-300 hover:shadow-md hover:-translate-y-0.5 active:translate-y-0'
                }`}
              >
                <PlusCircle className={`w-4 h-4 ${activeTab === 'data-entry' ? 'text-white' : 'text-emerald-600'}`} />
                {editingTicket ? `Edit Risk: ${editingTicket.id}` : 'Log New Risk'}
              </button>
            )}
          </nav>

          {/* Quick Primary Actions */}
          <div className="flex items-center gap-2">
          </div>
        </div>

        {/* Tab Router Section with subtle fade-in transition */}
        <main className="flex-1">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.15 }}
              className="h-full"
            >
              {activeTab === 'overview' && (
                <div id="overview-tab-view" className="space-y-6">
                  
                  {/* Full-width Heatmap Matrix */}
                  <div className="w-full space-y-6">
                    <RiskMatrix 
                      tickets={tickets} 
                      issues={issues}
                      onCellClick={handleMatrixCellClick}
                      selectedCell={matrixFilter}
                    />
                  </div>

                  {/* Key Highlights Section */}
                  <div id="key-highlights-section" className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs space-y-4">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div className="flex items-center gap-2.5">
                        <div className="bg-indigo-50 text-indigo-600 p-2 rounded-xl">
                          <Sparkles className="w-5 h-5" />
                        </div>
                        <div>
                          <h3 className="text-base font-bold text-slate-800">Key Highlights</h3>
                          <p className="text-xs text-slate-500">
                            Last 7 Days
                          </p>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-1">
                      {/* Highlight 1: Date Raised / New Risks in Last 7 Days */}
                      <div 
                        onClick={handleFilterNewRisks}
                        className="group bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 flex flex-col justify-between hover:border-indigo-300 hover:bg-indigo-50/30 hover:shadow-md transition-all cursor-pointer"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 group-hover:text-indigo-600 transition-colors">
                              <Calendar className="w-3.5 h-3.5 text-indigo-500" />
                              Date Raised (Last 7 Days)
                            </span>
                            <ExternalLink className="w-3 h-3 text-slate-300 group-hover:text-indigo-500 transition-colors" />
                          </div>
                          <div className="flex items-baseline gap-1.5">
                            <span className="text-2xl font-black text-slate-800 font-mono tracking-tight group-hover:text-indigo-700 transition-colors">
                              {risksRaisedLast7DaysCount}
                            </span>
                            <span className="text-xs font-semibold text-slate-500">
                              Raised in Last 7 Days
                            </span>
                          </div>
                        </div>
                        <div className="pt-3 mt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-indigo-600 font-bold group-hover:underline">
                          <span>{risksRaisedLast7DaysCount > 0 ? 'Filter Recent Raised Risks' : 'View All Raised Risks'}</span>
                          <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </div>

                      {/* Highlight 2: Date Closed (Last 7 Days) */}
                      <div 
                        onClick={handleFilterClosedRisks}
                        className="group bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 flex flex-col justify-between hover:border-emerald-300 hover:bg-emerald-50/30 hover:shadow-md transition-all cursor-pointer"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 group-hover:text-emerald-600 transition-colors">
                              <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                              Date Closed (Last 7 Days)
                            </span>
                            <ExternalLink className="w-3 h-3 text-slate-300 group-hover:text-emerald-500 transition-colors" />
                          </div>
                          <div className="flex items-baseline gap-1.5">
                            <span className="text-2xl font-black text-emerald-600 font-mono tracking-tight">
                              {risksClosedLast7DaysCount}
                            </span>
                            <span className="text-xs font-semibold text-slate-500">
                              Closed in Last 7 Days
                            </span>
                          </div>
                        </div>
                        <div className="pt-3 mt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-emerald-600 font-bold group-hover:underline">
                          <span>{risksClosedLast7DaysCount > 0 ? 'Filter Recent Closed Risks' : 'Filter Closed Register'}</span>
                          <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </div>

                      {/* Highlight 3: Risk Last Updated (Last 7 Days) */}
                      <div 
                        onClick={handleFilterLastUpdated}
                        className="group bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 flex flex-col justify-between hover:border-amber-300 hover:bg-amber-50/30 hover:shadow-md transition-all cursor-pointer"
                      >
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 group-hover:text-amber-600 transition-colors">
                              <Clock className="w-3.5 h-3.5 text-amber-500" />
                              Risk Last Updated (Last 7 Days)
                            </span>
                            <ExternalLink className="w-3 h-3 text-slate-300 group-hover:text-amber-500 transition-colors" />
                          </div>
                          <div className="flex items-baseline gap-1.5">
                            <span className="text-2xl font-black text-slate-800 font-mono tracking-tight group-hover:text-amber-700 transition-colors">
                              {risksUpdatedLast7DaysCount}
                            </span>
                            <span className="text-xs font-semibold text-slate-500">
                              Updated in Last 7 Days
                            </span>
                          </div>
                        </div>
                        <div className="pt-3 mt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-amber-600 font-bold group-hover:underline">
                          <span>{risksUpdatedLast7DaysCount > 0 ? 'Filter Recent Updated Risks' : 'Filter Updated Register'}</span>
                          <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                      </div>

                      {/* Highlight 4: Highlight to / Governance Level */}
                      <div className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 flex flex-col justify-between">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                              <Shield className="w-3.5 h-3.5 text-purple-500" />
                              Highlight to / Governance Level
                            </span>
                            <span className="text-[10px] font-medium text-slate-400">Click cell to filter</span>
                          </div>

                          {/* 4 Clickable Small Cells */}
                          <div className="grid grid-cols-2 gap-1.5 pt-0.5">
                            <button
                              type="button"
                              onClick={() => handleFilterGovernance('Internal Google')}
                              className="flex items-center justify-between bg-white hover:bg-purple-50 border border-purple-100 hover:border-purple-300 rounded-lg px-2.5 py-1.5 text-left transition-all cursor-pointer group shadow-2xs"
                              title="Filter Register by Internal Google"
                            >
                              <span className="text-[11px] font-semibold text-slate-600 group-hover:text-purple-700 truncate">Internal Google</span>
                              <span className="text-xs font-black text-purple-700 font-mono ml-1">{internalGovCount}</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => handleFilterGovernance('Team Google')}
                              className="flex items-center justify-between bg-white hover:bg-indigo-50 border border-indigo-100 hover:border-indigo-300 rounded-lg px-2.5 py-1.5 text-left transition-all cursor-pointer group shadow-2xs"
                              title="Filter Register by Team Google"
                            >
                              <span className="text-[11px] font-semibold text-slate-600 group-hover:text-indigo-700 truncate">Team Google</span>
                              <span className="text-xs font-black text-indigo-700 font-mono ml-1">{teamGovCount}</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => handleFilterGovernance('PSG')}
                              className="flex items-center justify-between bg-white hover:bg-blue-50 border border-blue-100 hover:border-blue-300 rounded-lg px-2.5 py-1.5 text-left transition-all cursor-pointer group shadow-2xs"
                              title="Filter Register by PSG"
                            >
                              <span className="text-[11px] font-semibold text-slate-600 group-hover:text-blue-700 truncate">PSG</span>
                              <span className="text-xs font-black text-blue-700 font-mono ml-1">{psgPcgGovCount}</span>
                            </button>

                            <button
                              type="button"
                              onClick={() => handleFilterGovernance('IPF')}
                              className="flex items-center justify-between bg-white hover:bg-sky-50 border border-sky-100 hover:border-sky-300 rounded-lg px-2.5 py-1.5 text-left transition-all cursor-pointer group shadow-2xs"
                              title="Filter Register by IPF"
                            >
                              <span className="text-[11px] font-semibold text-slate-600 group-hover:text-sky-700 truncate">IPF</span>
                              <span className="text-xs font-black text-sky-700 font-mono ml-1">{ipfGovCount}</span>
                            </button>
                          </div>
                        </div>

                        <div className="pt-2 mt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-purple-600 font-bold">
                          <button
                            type="button"
                            onClick={() => handleFilterGovernance('all')}
                            className="hover:underline flex items-center gap-1 cursor-pointer text-purple-600 group"
                          >
                            <span>View All Governance Levels</span>
                            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Immediate Action Needed / Critical Tickets Panel */}
                  <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-5 pb-3 border-b border-slate-100">
                      <div>
                        <h3 className="text-base font-bold text-slate-800 flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                          Critical Risk Exposure Backlog ({criticalBacklog.length})
                        </h3>
                      </div>
                      <button
                        onClick={() => setActiveTab('whole-data')}
                        className="text-xs text-indigo-600 hover:text-indigo-800 font-semibold flex items-center gap-1 cursor-pointer hover:underline self-start sm:self-center"
                      >
                        View Full Ledger
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {criticalBacklog.length > 0 ? (
                        criticalBacklog.map((t, idx) => (
                          <div key={`${t.id || 'rsk'}-${idx}`} className="border border-red-100 bg-red-50/10 rounded-xl p-4 flex flex-col justify-between hover:bg-red-50/20 transition-all">
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-xs font-bold text-red-700">{t.id}</span>
                                <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded-md font-bold uppercase">
                                  Score: {t.inherentRiskScore}
                                </span>
                              </div>
                              <h4 className="font-bold text-slate-800 text-xs line-clamp-1">{t.riskName}</h4>
                              <p className="text-[11px] text-slate-500 italic line-clamp-2 leading-relaxed">"{t.riskDescription}"</p>
                            </div>

                             <div className="flex items-center justify-between border-t border-slate-100/50 pt-3 mt-3 text-[10px] text-slate-500">
                              <div>Owner: <span className="font-semibold text-slate-700">{t.riskOwner}</span></div>
                              <button
                                onClick={() => setActiveTab('whole-data')}
                                className="text-indigo-600 hover:text-indigo-800 font-semibold cursor-pointer hover:underline"
                              >
                                View Ledger Record &rarr;
                              </button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="col-span-2 border border-dashed border-slate-200 rounded-xl py-10 flex flex-col items-center justify-center text-slate-400 text-center">
                          <HelpCircle className="w-8 h-8 text-slate-300 mb-1" />
                          <span className="font-medium text-slate-500 text-xs">Excellent: No active critical risks detected</span>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            All active tickets in the repository are governed within acceptable score thresholds.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                </div>
              )}

              {activeTab === 'whole-data' && (
                <WholeDataTab 
                  tickets={tickets}
                  onEdit={handleEditTicket}
                  onDelete={handleDeleteTicket}
                  matrixFilter={matrixFilter}
                  onClearMatrixFilter={() => setMatrixFilter(null)}
                  issues={issues}
                  onSaveIssue={handleSaveIssue}
                  onDeleteIssue={handleDeleteIssue}
                  onImportRisks={handleImportRisks}
                  onImportIssues={handleImportIssues}
                  onClearAll={handleClearAllRegisters}
                  overrideSearchTerm={overrideSearchTerm}
                  overrideStatusFilter={overrideStatusFilter}
                  overrideGovFilter={overrideGovFilter}
                  overrideDriverTreeRefFilter={overrideDriverTreeRefFilter}
                  overrideDateFilter={overrideDateFilter}
                />
              )}

              {activeTab === 'data-entry' && (
                <DataEntryTab 
                  editingTicket={editingTicket}
                  onSave={handleSaveTicket}
                  onCancel={() => {
                    setEditingTicket(null);
                    setActiveTab('whole-data');
                  }}
                  nextId={getNextId()}
                />
              )}

              {activeTab === 'trends' && (
                <TrendsTab tickets={tickets} />
              )}

              {activeTab === 'cd1-driver-tree' && (
                <CD1DriverTree 
                  tickets={tickets} 
                  issues={issues}
                  onSelectRisk={(ticketId) => {
                    setOverrideSearchTerm(ticketId);
                    setOverrideDriverTreeRefFilter('all');
                    setOverrideStatusFilter('all');
                    setOverrideGovFilter('all');
                    setMatrixFilter(null);
                    setActiveTab('whole-data');
                  }}
                  onSelectIssue={(issueId) => {
                    setOverrideIssueSearchTerm(issueId);
                    setActiveTab('issue-dashboard');
                  }}
                  onFilterLedgerByDriverRef={(driverRef) => {
                    setOverrideDriverTreeRefFilter(driverRef);
                    setOverrideSearchTerm('');
                    setOverrideStatusFilter('all');
                    setOverrideGovFilter('all');
                    setMatrixFilter(null);
                    setActiveTab('whole-data');
                  }}
                  onFilterIssuesByDriverRef={(driverRef) => {
                    setOverrideIssueSearchTerm(driverRef);
                    setActiveTab('issue-dashboard');
                  }}
                />
              )}

              {activeTab === 'issue-dashboard' && (
                <IssueRegisterView 
                  issues={issues}
                  onSaveIssue={handleSaveIssue}
                  onDeleteIssue={handleDeleteIssue}
                  onImportClick={() => setAppImportType('issue')}
                  overrideSearchTerm={overrideIssueSearchTerm}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </main>

      </div>

      {/* Global Import Data Modal */}
      {appImportType && (
        <ImportDataModal
          isOpen={!!appImportType}
          onClose={() => setAppImportType(null)}
          type={appImportType}
          existingCount={appImportType === 'risk' ? tickets.length : issues.length}
          onImportRisks={handleImportRisks}
          onImportIssues={handleImportIssues}
        />
      )}

      {/* Humble and Clean Outer Margin Info Footer */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-5 text-center text-xs text-slate-400 select-none">
        <div className="max-w-7xl mx-auto px-4">
          <p>&copy; 2026 Risk Control Systems. All rights reserved.</p>
        </div>
      </footer>

      {/* Custom React-based Delete Confirmation Modal */}
      <AnimatePresence>
        {ticketToDelete && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.15 }}
              className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-red-50 text-red-600 rounded-xl">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h3 className="text-base font-bold text-slate-900">Delete Risk Statement?</h3>
                  <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">
                    Are you sure you want to permanently delete risk statement <span className="font-mono font-bold text-slate-700">{ticketToDelete}</span>? 
                    This action is immediate and cannot be undone.
                  </p>
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  onClick={() => setTicketToDelete(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDeleteTicket}
                  className="px-4 py-2 text-xs font-semibold text-white bg-red-600 hover:bg-red-700 rounded-lg shadow-xs transition-colors cursor-pointer"
                >
                  Delete Risk
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
