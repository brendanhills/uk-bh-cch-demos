/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useRef } from 'react';
import { motion } from 'motion/react';
import { 
  RiskTicket, 
  RiskStatus, 
  CauseCategory, 
  RiskPriority, 
  GovernanceLevel, 
  RiskLevel, 
  PRIORITY_COLORS, 
  RISK_LEVEL_COLORS, 
  STATUS_COLORS,
  calculateOpenDays,
  IssueTicket,
  LIKELIHOOD_LABELS,
  CONSEQUENCE_LABELS,
  isDriverTreeRefMatch,
  DRIVER_TREE_REF_ORDERED_OPTIONS
} from '../types';
import IssueRegisterView from './IssueRegisterView';
import ImportDataModal from './ImportDataModal';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  Download, 
  Edit2, 
  Trash2, 
  RotateCcw,
  ChevronDown, 
  ChevronUp, 
  Eye, 
  Calendar, 
  User, 
  FileSpreadsheet, 
  Briefcase,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  Maximize2,
  Pencil,
  Database,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown
} from 'lucide-react';

interface WholeDataTabProps {
  tickets: RiskTicket[];
  onEdit: (ticket: RiskTicket) => void;
  onDelete: (id: string) => void;
  matrixFilter: { likelihood: number; consequence: number; type: 'inherent' | 'residual' } | null;
  onClearMatrixFilter: () => void;
  issues: IssueTicket[];
  onSaveIssue: (issue: IssueTicket) => Promise<void>;
  onDeleteIssue: (id: string) => Promise<void>;
  onImportRisks?: (newRisks: RiskTicket[]) => void;
  onImportIssues?: (newIssues: IssueTicket[]) => void;
  onClearAll?: () => void;
  overrideSearchTerm?: string;
  overrideStatusFilter?: string;
  overrideGovFilter?: string;
  overrideDriverTreeRefFilter?: string;
  overrideDateFilter?: string;
}

export default function WholeDataTab({ 
  tickets, 
  onEdit, 
  onDelete, 
  matrixFilter, 
  onClearMatrixFilter,
  issues,
  onSaveIssue,
  onDeleteIssue,
  onImportRisks,
  onImportIssues,
  onClearAll,
  overrideSearchTerm,
  overrideStatusFilter,
  overrideGovFilter,
  overrideDriverTreeRefFilter,
  overrideDateFilter
}: WholeDataTabProps) {
  // Register switcher state
  const [activeRegister, setActiveRegister] = useState<'risk' | 'issue'>('risk');

  // Drag-to-scroll handlers and states for the main risk table
  const riskTableContainerRef = useRef<HTMLDivElement>(null);
  const [isRiskDragging, setIsRiskDragging] = useState(false);
  const [riskDragStartX, setRiskDragStartX] = useState(0);
  const [riskDragStartY, setRiskDragStartY] = useState(0);
  const [riskDragScrollLeft, setRiskDragScrollLeft] = useState(0);
  const [riskDragScrollTop, setRiskDragScrollTop] = useState(0);

  const handleRiskMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only left clicks
    const target = e.target as HTMLElement;
    // Don't drag if clicking interactive elements
    if (
      target.closest('button') || 
      target.closest('select') || 
      target.closest('input') || 
      target.closest('a') ||
      target.closest('th') || // Don't drag on header sorting elements
      target.closest('.interactive-action')
    ) {
      return;
    }
    const container = riskTableContainerRef.current;
    if (!container) return;
    setIsRiskDragging(true);
    setRiskDragStartX(e.pageX - container.offsetLeft);
    setRiskDragStartY(e.pageY - container.offsetTop);
    setRiskDragScrollLeft(container.scrollLeft);
    setRiskDragScrollTop(container.scrollTop);
  };

  const handleRiskMouseMove = (e: React.MouseEvent) => {
    if (!isRiskDragging) return;
    const container = riskTableContainerRef.current;
    if (!container) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const y = e.pageY - container.offsetTop;
    const walkX = (x - riskDragStartX) * 1.5; // Sensitivity multiplier
    const walkY = (y - riskDragStartY) * 1.5;
    container.scrollLeft = riskDragScrollLeft - walkX;
    container.scrollTop = riskDragScrollTop - walkY;
  };

  const handleRiskMouseUpOrLeave = () => {
    setIsRiskDragging(false);
  };

  // Scroll handlers and drag-to-scroll for the modal 36-column table container
  const modalTableContainerRef = useRef<HTMLDivElement>(null);
  const [isModalDragging, setIsModalDragging] = useState(false);
  const [modalDragStartX, setModalDragStartX] = useState(0);
  const [modalDragStartY, setModalDragStartY] = useState(0);
  const [modalDragScrollLeft, setModalDragScrollLeft] = useState(0);
  const [modalDragScrollTop, setModalDragScrollTop] = useState(0);

  const handleModalMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return; // Only left clicks
    const target = e.target as HTMLElement;
    if (
      target.closest('button') || 
      target.closest('select') || 
      target.closest('input') || 
      target.closest('a') ||
      target.closest('th') ||
      target.closest('.interactive-action')
    ) {
      return;
    }
    const container = modalTableContainerRef.current;
    if (!container) return;
    setIsModalDragging(true);
    setModalDragStartX(e.pageX - container.offsetLeft);
    setModalDragStartY(e.pageY - container.offsetTop);
    setModalDragScrollLeft(container.scrollLeft);
    setModalDragScrollTop(container.scrollTop);
  };

  const handleModalMouseMove = (e: React.MouseEvent) => {
    if (!isModalDragging) return;
    const container = modalTableContainerRef.current;
    if (!container) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const y = e.pageY - container.offsetTop;
    const walkX = (x - modalDragStartX) * 1.5;
    const walkY = (y - modalDragStartY) * 1.5;
    container.scrollLeft = modalDragScrollLeft - walkX;
    container.scrollTop = modalDragScrollTop - walkY;
  };

  const handleModalMouseUpOrLeave = () => {
    setIsModalDragging(false);
  };

  const scrollModalTable = (direction: 'left' | 'right' | 'up' | 'down') => {
    const container = modalTableContainerRef.current;
    if (!container) return;
    
    const scrollAmountX = 400; // Amount to scroll horizontally
    const scrollAmountY = 200; // Amount to scroll vertically
    
    switch (direction) {
      case 'left':
        container.scrollBy({ left: -scrollAmountX, behavior: 'smooth' });
        break;
      case 'right':
        container.scrollBy({ left: scrollAmountX, behavior: 'smooth' });
        break;
      case 'up':
        container.scrollBy({ top: -scrollAmountY, behavior: 'smooth' });
        break;
      case 'down':
        container.scrollBy({ top: scrollAmountY, behavior: 'smooth' });
        break;
    }
  };

  // Confirmation state for clearing database
  const [confirmClear, setConfirmClear] = useState(false);

  const handleClearAllClick = () => {
    if (!confirmClear) {
      setConfirmClear(true);
      // Auto-reset confirmation after 4 seconds
      setTimeout(() => {
        setConfirmClear(false);
      }, 4000);
    } else {
      onClearAll?.();
      setConfirmClear(false);
    }
  };

  // Import Modal States
  const [showImportModal, setShowImportModal] = useState(false);
  const [importType, setImportType] = useState<'risk' | 'issue'>('risk');

  // Filters & Search
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [govFilter, setGovFilter] = useState<string>('all');
  const [riskLevelFilter, setRiskLevelFilter] = useState<string>('all');
  const [driverTreeRefFilter, setDriverTreeRefFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all');
  const [riskLevelType, setRiskLevelType] = useState<'inherent' | 'residual'>('inherent');
  const [minRiskScore, setMinRiskScore] = useState<number>(1);

  // Available Driver Tree Ref Options for dropdown in exact requested order
  const driverTreeRefOptions = useMemo(() => {
    const list = [...DRIVER_TREE_REF_ORDERED_OPTIONS];
    const knownSet = new Set(list);
    const extraRefs: string[] = [];
    tickets.forEach(t => {
      if (t.driverTreeRef && t.driverTreeRef.trim()) {
        const ref = t.driverTreeRef.trim();
        if (ref !== 'N/A' && ref !== '-') {
          ref.split(/[,;]+/).forEach(r => {
            const clean = r.trim();
            if (clean && !knownSet.has(clean)) {
              knownSet.add(clean);
              extraRefs.push(clean);
            }
          });
        }
      }
    });
    extraRefs.sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }));
    const naIndex = list.indexOf('N/A');
    if (naIndex !== -1) {
      list.splice(naIndex, 0, ...extraRefs);
    } else {
      list.push(...extraRefs);
    }
    return list;
  }, [tickets]);

  // Synchronize incoming filter overrides from Key Highlights
  React.useEffect(() => {
    if (overrideSearchTerm !== undefined) setSearchTerm(overrideSearchTerm);
  }, [overrideSearchTerm]);

  React.useEffect(() => {
    if (overrideStatusFilter !== undefined) setStatusFilter(overrideStatusFilter);
  }, [overrideStatusFilter]);

  React.useEffect(() => {
    if (overrideGovFilter !== undefined) setGovFilter(overrideGovFilter);
  }, [overrideGovFilter]);

  React.useEffect(() => {
    if (overrideDriverTreeRefFilter !== undefined) setDriverTreeRefFilter(overrideDriverTreeRefFilter);
  }, [overrideDriverTreeRefFilter]);

  React.useEffect(() => {
    if (overrideDateFilter !== undefined) setDateFilter(overrideDateFilter);
  }, [overrideDateFilter]);

  React.useEffect(() => {
    if (matrixFilter) {
      setStatusFilter('all');
      setActiveRegister('risk');
    }
  }, [matrixFilter]);

  // Issue Register States
  const [issueSearchTerm, setIssueSearchTerm] = useState('');
  const [issueStatusFilter, setIssueStatusFilter] = useState<string>('all');
  const [issuePriorityFilter, setIssuePriorityFilter] = useState<string>('all');
  const [issueSeverityFilter, setIssueSeverityFilter] = useState<string>('all');
  const [issueSortField, setIssueSortField] = useState<keyof IssueTicket>('id');
  const [issueSortDirection, setIssueSortDirection] = useState<'asc' | 'desc'>('asc');
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [editingIssue, setEditingIssue] = useState<IssueTicket | null>(null);
  const [issueForm, setIssueForm] = useState<Partial<IssueTicket>>({});

  const openAddIssueModal = () => {
    setIssueForm({
      id: getNextIssueId(),
      status: 'Open',
      relatedRiskId: '',
      issueOwner: '',
      bundle: '',
      issueName: '',
      issueDescription: '',
      causeDescription: '',
      impactCategory: '',
      consequence: '',
      trend: 'Stable',
      priorityRating: 'Prompt',
      escalateTo: '',
      severityRating: 'Medium',
      actionPlan: '',
      dateRaised: new Date().toISOString().split('T')[0],
      raisedBy: '',
      dateClosed: '',
      lastUpdated: new Date().toISOString().split('T')[0],
      protectedIssueRisk: 'No',
      dpeRefNumber: ''
    });
    setEditingIssue(null);
    setShowIssueModal(true);
  };

  const openEditIssueModal = (issue: IssueTicket) => {
    setIssueForm(issue);
    setEditingIssue(issue);
    setShowIssueModal(true);
  };


  // Sorting
  const [sortField, setSortField] = useState<keyof RiskTicket>('id');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Expanded Rows for ticket details
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  // Full Registry Modal Window State
  const [showRegistryModal, setShowRegistryModal] = useState(false);

  // Reset all filters
  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setCategoryFilter('all');
    setPriorityFilter('all');
    setGovFilter('all');
    setRiskLevelFilter('all');
    setDriverTreeRefFilter('all');
    setDateFilter('all');
    setMinRiskScore(1);
    onClearMatrixFilter();
  };

  // Toggle row expansion
  const toggleRow = (id: string) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Sort handler
  const handleSort = (field: keyof RiskTicket) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const renderSortIcon = (field: keyof RiskTicket) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 text-slate-400 group-hover:text-slate-600 transition-colors" />;
    }
    return sortDirection === 'asc' 
      ? <ChevronUp className="w-3.5 h-3.5 text-indigo-600 font-extrabold" />
      : <ChevronDown className="w-3.5 h-3.5 text-indigo-600 font-extrabold" />;
  };

  // Filtered & Sorted Tickets
  const filteredTickets = useMemo(() => {
    return tickets
      .filter(t => {
        // Search text matching ID, name, owner, bundle, description
        const text = searchTerm.toLowerCase();
        const matchesSearch = 
          t.id.toLowerCase().includes(text) ||
          t.riskName.toLowerCase().includes(text) ||
          t.riskOwner.toLowerCase().includes(text) ||
          t.bundle.toLowerCase().includes(text) ||
          t.riskDescription.toLowerCase().includes(text) ||
          (t.driverTreeRef && t.driverTreeRef.toLowerCase().includes(text));

        // Helper for matching values including NA, N/A, Unknown, No Data, -, and Blank
        const matchesFieldValue = (fieldVal: string | undefined | null, filterVal: string) => {
          if (filterVal === 'all') return true;
          const clean = (fieldVal ?? '').trim();
          if (filterVal === 'NA') return clean === 'NA' || clean === 'N/A' || clean.toLowerCase() === 'na';
          if (filterVal === 'N/A') return clean === 'N/A' || clean === 'NA' || clean.toLowerCase() === 'n/a';
          if (filterVal === 'Unknown') return clean === 'Unknown' || clean.toLowerCase() === 'unknown';
          if (filterVal === 'No Data') return clean === 'No Data' || clean.toLowerCase() === 'no data' || clean.toLowerCase() === 'none';
          if (filterVal === '-') return clean === '-' || clean === '--';
          if (filterVal === ' ') return clean === '' || clean === ' ';
          return fieldVal === filterVal;
        };

        // Standard filter dropdown matches
        const matchesStatus = matchesFieldValue(t.status, statusFilter);
        const matchesCategory = matchesFieldValue(t.causeCategory, categoryFilter);
        const matchesPriority = matchesFieldValue(t.priority, priorityFilter);
        const matchesGov = govFilter === 'all' || matchesFieldValue(t.governanceLevel, govFilter) || (govFilter === 'PSG' && t.governanceLevel === 'PCG');
        
        // Risk level matches
        let matchesRiskLevel = true;
        if (riskLevelFilter !== 'all') {
          const currentLevel = riskLevelType === 'inherent' ? t.inherentRiskLevel : t.residualRiskLevel;
          matchesRiskLevel = matchesFieldValue(currentLevel, riskLevelFilter);
        }

        // Heatmap cell matches
        let matchesMatrix = true;
        if (matrixFilter) {
          const l = matrixFilter.type === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
          const c = matrixFilter.type === 'inherent' ? t.inherentConsequence : t.residualConsequence;
          matchesMatrix = l === matrixFilter.likelihood && c === matrixFilter.consequence;
        }

        // Min risk score matches
        const currentScore = riskLevelType === 'inherent' ? t.inherentRiskScore : t.residualRiskScore;
        const matchesMinRiskScore = currentScore === null ? (minRiskScore === 1) : (currentScore >= minRiskScore);

        // Driver Tree Ref match
        let matchesDriverTreeRef = true;
        if (driverTreeRefFilter !== 'all') {
          matchesDriverTreeRef = isDriverTreeRefMatch(t.driverTreeRef, driverTreeRefFilter);
        }

        // Date range match (Links strictly to "Risk Last Updated" column only)
        let matchesDate = true;
        if (dateFilter !== 'all') {
          matchesDate = false;
          const rawDateStr = t.riskLastUpdated;
          if (rawDateStr && typeof rawDateStr === 'string') {
            const cleanStr = rawDateStr.trim();
            if (cleanStr && cleanStr !== 'N/A' && cleanStr !== 'No Data' && cleanStr !== '-' && cleanStr !== 'unknown') {
              let ticketDate: Date | null = null;
              
              const directDate = new Date(cleanStr);
              if (!isNaN(directDate.getTime()) && directDate.getFullYear() > 2000 && directDate.getFullYear() < 2100) {
                ticketDate = directDate;
              } else {
                const slashDashMatch = cleanStr.match(/^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})$/);
                if (slashDashMatch) {
                  const day = parseInt(slashDashMatch[1], 10);
                  const month = parseInt(slashDashMatch[2], 10) - 1;
                  let year = parseInt(slashDashMatch[3], 10);
                  if (year < 100) year += 2000;
                  if (month >= 0 && month < 12 && day >= 1 && day <= 31) {
                    ticketDate = new Date(year, month, day);
                  }
                } else {
                  const mmmMatch = cleanStr.match(/^(\d{1,2})[\s\-]+([A-Za-z]{3,})[\s\-]+(\d{2,4})$/);
                  if (mmmMatch) {
                    const day = parseInt(mmmMatch[1], 10);
                    const monthStr = mmmMatch[2].toLowerCase().substring(0, 3);
                    let year = parseInt(mmmMatch[3], 10);
                    if (year < 100) year += 2000;
                    const monthNames = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"];
                    const month = monthNames.indexOf(monthStr);
                    if (month >= 0 && day >= 1 && day <= 31) {
                      ticketDate = new Date(year, month, day);
                    }
                  }
                }
              }

              if (ticketDate) {
                const nowMs = new Date().getTime();
                const ticketMs = ticketDate.getTime();
                const diffDays = (nowMs - ticketMs) / (1000 * 60 * 60 * 24);
                
                if (dateFilter === '7days') matchesDate = diffDays >= 0 && diffDays <= 7 || ticketMs >= nowMs - (7 * 24 * 60 * 60 * 1000);
                else if (dateFilter === '30days') matchesDate = diffDays >= 0 && diffDays <= 30 || ticketMs >= nowMs - (30 * 24 * 60 * 60 * 1000);
                else if (dateFilter === '90days') matchesDate = diffDays >= 0 && diffDays <= 90 || ticketMs >= nowMs - (90 * 24 * 60 * 60 * 1000);
                else if (dateFilter === '1year') matchesDate = diffDays >= 0 && diffDays <= 365 || ticketMs >= nowMs - (365 * 24 * 60 * 60 * 1000);
              }
            }
          }
        }

        return matchesSearch && matchesStatus && matchesCategory && matchesPriority && matchesGov && matchesRiskLevel && matchesMatrix && matchesMinRiskScore && matchesDriverTreeRef && matchesDate;
      })
      .sort((a, b) => {
        const valA = a[sortField];
        const valB = b[sortField];

        if (valA === undefined || valA === null || valA === '') return 1;
        if (valB === undefined || valB === null || valB === '') return -1;

        if (typeof valA === 'number' && typeof valB === 'number') {
          return sortDirection === 'asc' ? valA - valB : valB - valA;
        }

        const strA = String(valA);
        const strB = String(valB);

        const comp = strA.localeCompare(strB, undefined, { numeric: true, sensitivity: 'base' });
        return sortDirection === 'asc' ? comp : -comp;
      });
  }, [tickets, searchTerm, statusFilter, categoryFilter, priorityFilter, govFilter, riskLevelFilter, driverTreeRefFilter, dateFilter, riskLevelType, minRiskScore, matrixFilter, sortField, sortDirection]);

  // CSV Exporter
  const exportToCSV = () => {
    const headers = [
      'ID', 'Status', 'Related Issue ID', 'Risk Owner', 'Bundle', 'Driver Tree Ref', 'Risk Name', 'Risk Description',
      'Cause Description', 'Cause Category', 'Consequence Description', 'Trend', 'Priority',
      'Highlight to/Governance Level', 'Inherent Likelihood Rating', 'Inherent Consequence Rating',
      'Inherent risk', 'Treatment Owner', 'Treatment/Mitigation Plan', 'Target Date',
      'Residual Likelihood Rating', 'Residual Consequence Rating', 'Residual risk', 'Date Raised',
      'Date Closed', 'Risk Last Updated', 'Comments', 'Protected Issue/Risk', 'DPE Ref Number',
      'Timelines', 'SIgn-Off Requirement', 'Executive Status', 'Next Mitigation Due date',
      'Mitigation Status', 'Strategy', 'Who Raised', 'Open Days'
    ];

    const rows = filteredTickets.map((t, idx) => [
      t.id,
      t.status,
      t.relatedIssueId || `ISS-${200 + idx}`,
      t.riskOwner,
      t.bundle || 'N/A',
      t.driverTreeRef || 'N/A',
      t.riskName,
      t.riskDescription.replace(/"/g, '""'),
      (t.causeDescription || '').replace(/"/g, '""'),
      t.causeCategory,
      (t.consequenceDescription || '').replace(/"/g, '""'),
      t.trend,
      t.priority,
      t.governanceLevel,
      t.inherentLikelihood,
      t.inherentConsequence,
      `${t.inherentRiskScore} (${t.inherentRiskLevel})`,
      t.treatmentOwner || 'Unassigned',
      (t.treatmentPlan || '').replace(/"/g, '""'),
      t.targetDate || 'N/A',
      t.residualLikelihood,
      t.residualConsequence,
      `${t.residualRiskScore} (${t.residualRiskLevel})`,
      t.dateRaised,
      t.dateClosed || 'N/A',
      t.riskLastUpdated || t.dateClosed || t.dateRaised,
      (t.comments || '').replace(/"/g, '""'),
      t.protectedIssueRisk || 'No',
      t.dpeRefNumber || 'N/A',
      t.timelines || 'N/A',
      t.signOffRequirement || 'No',
      t.executiveStatus || 'Pending',
      t.nextMitigationDueDate || t.targetDate || 'N/A',
      t.mitigationStatus || 'Pending',
      t.strategy || 'N/A',
      t.whoRaised || 'N/A',
      calculateOpenDays(t.dateRaised, t.dateClosed)
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${val}"`).join(','))].join('\n');
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `risk_register_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Issue Register Functions
  const handleIssueSort = (field: keyof IssueTicket) => {
    if (issueSortField === field) {
      setIssueSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setIssueSortField(field);
      setIssueSortDirection('asc');
    }
  };

  const filteredIssues = useMemo(() => {
    return issues
      .filter(i => {
        const text = issueSearchTerm.toLowerCase();
        const matchesSearch = 
          i.id.toLowerCase().includes(text) ||
          i.issueName.toLowerCase().includes(text) ||
          i.issueOwner.toLowerCase().includes(text) ||
          i.bundle.toLowerCase().includes(text) ||
          i.issueDescription.toLowerCase().includes(text);

        const matchesStatus = issueStatusFilter === 'all' || i.status === issueStatusFilter;
        const matchesPriority = issuePriorityFilter === 'all' || i.priorityRating === issuePriorityFilter;
        const matchesSeverity = issueSeverityFilter === 'all' || i.severityRating === issueSeverityFilter;

        return matchesSearch && matchesStatus && matchesPriority && matchesSeverity;
      })
      .sort((a, b) => {
        const valA = a[issueSortField];
        const valB = b[issueSortField];

        if (valA === undefined || valA === null || valA === '') return 1;
        if (valB === undefined || valB === null || valB === '') return -1;

        if (typeof valA === 'number' && typeof valB === 'number') {
          return issueSortDirection === 'asc' ? valA - valB : valB - valA;
        }

        const strA = String(valA);
        const strB = String(valB);

        const comp = strA.localeCompare(strB, undefined, { numeric: true, sensitivity: 'base' });
        return issueSortDirection === 'asc' ? comp : -comp;
      });
  }, [issues, issueSearchTerm, issueStatusFilter, issuePriorityFilter, issueSeverityFilter, issueSortField, issueSortDirection]);

  const exportIssuesToCSV = () => {
    const headers = [
      'ID', 'Status', 'Related Risk ID', 'Issue owner', 'Bundle', 'Issue Name', 'Issue Description',
      'Cause Description', 'Impact Category', 'Consequence', 'Trend', 'Priority Rating',
      'Escalate to:', 'Severity Rating', 'Action Plan', 'Date Raised', 'Raised by',
      'Date Closed', 'Last Updated', 'Protected Issue/Risk', 'DPE Ref Number'
    ];

    const rows = filteredIssues.map(i => [
      i.id,
      i.status,
      i.relatedRiskId,
      i.issueOwner,
      i.bundle,
      i.issueName,
      i.issueDescription,
      i.causeDescription,
      i.impactCategory,
      i.consequence,
      i.trend,
      i.priorityRating,
      i.escalateTo,
      i.severityRating,
      i.actionPlan,
      i.dateRaised,
      i.raisedBy,
      i.dateClosed || '',
      i.lastUpdated,
      i.protectedIssueRisk,
      i.dpeRefNumber
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(','), ...rows.map(e => e.map(val => `"${String(val).replace(/"/g, '""')}"`).join(','))].join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `issue_register_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const openIssueNewWindow = () => {
    const newWindow = window.open('', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
    if (!newWindow) {
      alert('Popup window blocked! Please allow popups for this site.');
      return;
    }

    const rowsHtml = filteredIssues.map((i, idx) => `
      <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100">
        <td class="px-4 py-3 text-center text-slate-400 font-mono text-[11px] bg-slate-50/20 border-r border-slate-100">${idx + 1}</td>
        <td class="px-3 py-3 font-semibold text-indigo-700 font-mono border-r border-slate-100">${i.id}</td>
        <td class="px-3 py-3 border-r border-slate-100">
          <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
            i.status === 'Closed' ? 'bg-emerald-100 text-emerald-800' :
            i.status === 'Escalated' ? 'bg-rose-100 text-rose-800' :
            i.status === 'Issue Eventuated' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-800'
          }">${i.status}</span>
        </td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-[11px] text-slate-500">${i.relatedRiskId || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-medium text-slate-800">${i.issueOwner}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.bundle}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-semibold text-slate-900">${i.issueName}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.issueDescription}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.causeDescription}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.impactCategory}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.consequence}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-semibold text-slate-700">${i.trend}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-bold text-indigo-700">${i.priorityRating}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.escalateTo}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center">
          <span class="inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
            i.severityRating === 'Critical' ? 'bg-red-600 text-white' :
            i.severityRating === 'High' ? 'bg-orange-100 text-orange-700' :
            i.severityRating === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-700'
          }">${i.severityRating}</span>
        </td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.actionPlan}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-[11px] text-slate-500">${i.dateRaised}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.raisedBy}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-[11px] text-slate-500">${i.dateClosed || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-[11px] text-slate-500">${i.lastUpdated}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-semibold text-slate-600">${i.protectedIssueRisk}</td>
        <td class="px-3 py-3 text-slate-600 font-mono text-[11px]">${i.dpeRefNumber || 'N/A'}</td>
      </tr>
    `).join('');

    newWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Corporate Issue Registry Ledger</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
          body { font-family: 'Inter', sans-serif; }
        </style>
      </head>
      <body class="bg-slate-50 text-slate-800 p-8">
        <div class="max-w-[98%] mx-auto space-y-6">
          <div class="flex items-center justify-between border-b border-slate-200 pb-5">
            <div>
              <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Corporate Issue Registry Ledger</h1>
              <p class="text-xs text-slate-500 mt-1">Live corporate audit of 21 columns of operational issues.</p>
            </div>
            <div>
              <button onclick="window.close()" class="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl cursor-pointer transition-colors shadow-sm">
                Close Window
              </button>
            </div>
          </div>

          <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div class="overflow-x-auto no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden" style="scrollbar-width:none;-ms-overflow-style:none;">
              <table class="w-full table-auto border-collapse text-left min-w-[3600px] text-xs">
                <thead>
                  <tr class="bg-slate-100 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider select-none">
                    <th class="w-12 px-4 py-3.5 text-center border-r border-slate-200 bg-slate-100">Row</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">ID</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Status</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Related Risk ID</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue Owner</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Bundle</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue Name</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Cause Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Impact Category</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Consequence</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Trend</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Priority Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Escalate To</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Severity Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Action Plan</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Date Raised</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Raised By</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Date Closed</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Last Updated</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Protected Issue/Risk</th>
                    <th class="px-3 py-3.5">DPE Ref Number</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 text-slate-700">
                  ${rowsHtml}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </body>
      </html>
    `);
    newWindow.document.close();
  };

  const resetIssueFilters = () => {
    setIssueSearchTerm('');
    setIssueStatusFilter('all');
    setIssuePriorityFilter('all');
    setIssueSeverityFilter('all');
  };

  const getNextIssueId = (): string => {
    if (issues.length === 0) return 'ISS-001';
    const ids = issues.map(i => {
      const parts = i.id.split('-');
      const numPart = parts[1];
      return parseInt(numPart) || 0;
    });
    const maxId = Math.max(...ids);
    const nextNum = maxId + 1;
    return `ISS-${String(nextNum).padStart(3, '0')}`;
  };

  const openNewWindow = () => {
    const newWindow = window.open('', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
    if (!newWindow) {
      alert('Popup window blocked! Please allow popups for this site, or view complete columns using the inline "Open Registry Window" modal.');
      return;
    }

    const title = "Risk Ledger - Corporate Registry";
    
    const rowsHtml = filteredTickets.map((t, idx) => {
      const openDays = calculateOpenDays(t.dateRaised, t.dateClosed);
      return `
        <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100">
          <td class="px-4 py-3 text-center text-slate-400 font-mono text-[11px] bg-slate-50/20 border-r border-slate-100">${idx + 1}</td>
          <td class="px-3 py-3 font-semibold text-indigo-600 font-mono border-r border-slate-100">${t.id}</td>
          <td class="px-3 py-3 border-r border-slate-100">
            <span class="px-2.5 py-1 text-[10px] font-bold border rounded-full uppercase status-${t.status.toLowerCase().replace(/\s+/g, '-')}">${t.status}</span>
          </td>
          <td class="px-3 py-3 font-mono text-slate-600 border-r border-slate-100">${t.relatedIssueId || `ISS-${200 + idx}`}</td>
          <td class="px-3 py-3 text-slate-700 border-r border-slate-100 font-medium">${t.riskOwner}</td>
          <td class="px-3 py-3 border-r border-slate-100">
            <span class="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-medium">${t.bundle || 'N/A'}</span>
          </td>
          <td class="px-3 py-3 border-r border-slate-100 font-mono text-slate-600">${t.driverTreeRef || 'N/A'}</td>
          <td class="px-3 py-3 font-semibold text-slate-800 border-r border-slate-100">${t.riskName}</td>
          <td class="px-3 py-3 text-slate-600 border-r border-slate-100 italic">${t.riskDescription}</td>
          <td class="px-3 py-3 text-slate-500 border-r border-slate-100">${t.causeDescription || 'N/A'}</td>
          <td class="px-3 py-3 border-r border-slate-100">
            <span class="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-medium">${t.causeCategory}</span>
          </td>
          <td class="px-3 py-3 text-slate-500 border-r border-slate-100">${t.consequenceDescription || 'N/A'}</td>
          <td class="px-3 py-3 border-r border-slate-100 font-semibold trend-${t.trend.toLowerCase()}">${t.trend}</td>
          <td class="px-3 py-3 border-r border-slate-100">
            <span class="px-2 py-0.5 text-[10px] font-semibold border rounded priority-${t.priority.toLowerCase().replace(' ', '-')}">${t.priority}</span>
          </td>
          <td class="px-3 py-3 text-slate-600 border-r border-slate-100 font-medium">${t.governanceLevel}</td>
          <td class="px-3 py-3 text-center font-bold border-r border-slate-100">${LIKELIHOOD_LABELS[t.inherentLikelihood] || t.inherentLikelihood}</td>
          <td class="px-3 py-3 text-center font-bold border-r border-slate-100">${CONSEQUENCE_LABELS[t.inherentConsequence] || t.inherentConsequence}</td>
          <td class="px-3 py-3 text-center border-r border-slate-100">
            <span class="text-[10px] px-2 py-0.5 rounded-sm font-semibold uppercase risk-level-${t.inherentRiskLevel.toLowerCase()}">${t.inherentRiskScore} (${t.inherentRiskLevel})</span>
          </td>
          <td class="px-3 py-3 text-slate-700 border-r border-slate-100 font-medium">${t.treatmentOwner || 'Unassigned'}</td>
          <td class="px-3 py-3 text-slate-500 border-r border-slate-100">${t.treatmentPlan || 'N/A'}</td>
          <td class="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">${t.targetDate || 'N/A'}</td>
          <td class="px-3 py-3 text-center font-bold border-r border-slate-100">${LIKELIHOOD_LABELS[t.residualLikelihood] || t.residualLikelihood}</td>
          <td class="px-3 py-3 text-center font-bold border-r border-slate-100">${CONSEQUENCE_LABELS[t.residualConsequence] || t.residualConsequence}</td>
          <td class="px-3 py-3 text-center border-r border-slate-100">
            <span class="text-[10px] px-2 py-0.5 rounded-sm font-semibold uppercase risk-level-${t.residualRiskLevel.toLowerCase()}">${t.residualRiskScore} (${t.residualRiskLevel})</span>
          </td>
          <td class="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">${t.dateRaised}</td>
          <td class="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">${t.dateClosed || 'N/A'}</td>
          <td class="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">${t.riskLastUpdated || t.dateClosed || t.dateRaised}</td>
          <td class="px-3 py-3 text-slate-500 border-r border-slate-100">${t.comments || 'N/A'}</td>
          <td class="px-3 py-3 border-r border-slate-100 text-slate-600 font-medium">${t.protectedIssueRisk || 'No'}</td>
          <td class="px-3 py-3 font-mono text-slate-600 border-r border-slate-100">${t.dpeRefNumber || 'N/A'}</td>
          <td class="px-3 py-3 text-slate-600 border-r border-slate-100">${t.timelines || 'N/A'}</td>
          <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${t.signOffRequirement || 'No'}</td>
          <td class="px-3 py-3 border-r border-slate-100">
            <span class="px-2 py-0.5 text-[10px] font-semibold rounded border exec-status-${(t.executiveStatus || 'Pending').toLowerCase().replace(' ', '-')}">${t.executiveStatus || 'Pending'}</span>
          </td>
          <td class="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">${t.nextMitigationDueDate || t.targetDate || 'N/A'}</td>
          <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${t.mitigationStatus || 'Pending'}</td>
          <td class="px-3 py-3 border-r border-slate-100 text-slate-600 font-medium">${t.strategy || 'N/A'}</td>
          <td class="px-3 py-3 text-slate-600 border-r border-slate-100 font-medium">${t.whoRaised || 'N/A'}</td>
          <td class="px-3 py-3 text-center font-mono font-bold text-slate-700 bg-slate-50/10">${openDays}</td>
        </tr>
      `;
    }).join('');

    newWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>${title}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
          tailwind.config = {
            theme: {
              extend: {
                fontFamily: {
                  sans: ['Inter', 'sans-serif'],
                  mono: ['JetBrains Mono', 'monospace'],
                }
              }
            }
          }
        </script>
        <style>
          body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
          }
          .status-active { background-color: #f0fdf4; color: #166534; border-color: #dcfce7; }
          .status-closed { background-color: #f1f5f9; color: #475569; border-color: #e2e8f0; }
          .status-issue-eventuated { background-color: #fffbeb; color: #b45309; border-color: #fef3c7; }
          
          .risk-level-low { background-color: #f0fdf4; color: #15803d; }
          .risk-level-medium { background-color: #fffbeb; color: #b45309; }
          .risk-level-high { background-color: #fff5f5; color: #c53030; }
          .risk-level-critical { background-color: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }

          .trend-increasing { color: #dc2626; }
          .trend-stable { color: #475569; }
          .trend-decreasing { color: #16a34a; }

          .priority-immediate { background-color: #fef2f2; color: #991b1b; border-color: #fee2e2; }
          .priority-urgent { background-color: #fff7ed; color: #c2410c; border-color: #ffedd5; }
          .priority-prompt { background-color: #eff6ff; color: #1d4ed8; border-color: #dbeafe; }
          .priority-not-urgent { background-color: #f8fafc; color: #64748b; border-color: #f1f5f9; }

          .exec-status-approved { background-color: #ecfdf5; color: #047857; border-color: #d1fae5; }
          .exec-status-under-review { background-color: #fffbeb; color: #b45309; border-color: #fef3c7; }
          .exec-status-pending { background-color: #f8fafc; color: #64748b; border-color: #f1f5f9; }

          ::-webkit-scrollbar {
            height: 10px;
            width: 10px;
          }
          ::-webkit-scrollbar-track {
            background: #f1f5f9;
          }
          ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 5px;
          }
          ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
          }
        </style>
      </head>
      <body class="p-6 text-slate-800">
        <div class="max-w-[100%] mx-auto">
          <!-- Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm mb-6">
            <div>
              <div class="flex items-center gap-2.5">
                <div class="w-2.5 h-2.5 bg-indigo-600 rounded-full"></div>
                <h1 class="text-xl font-bold text-slate-900 tracking-tight">Corporate Risk Ledger Registry</h1>
              </div>
              <p class="text-xs text-slate-500 mt-1">
                Displaying complete 36-column metadata across all filtered records. Generated on ${new Date().toLocaleDateString()} ${new Date().toLocaleTimeString()}.
              </p>
            </div>
            <div class="flex items-center gap-3">
              <button onclick="window.print()" class="px-4 py-2 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-xl cursor-pointer transition-colors">
                Print Registry
              </button>
              <button onclick="window.close()" class="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl cursor-pointer transition-colors shadow-sm">
                Close Window
              </button>
            </div>
          </div>

          <!-- Summary stats bar -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Total Items</span>
              <span class="text-xl font-extrabold text-slate-950 mt-1 font-mono">${filteredTickets.length}</span>
            </div>
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Active Status</span>
              <span class="text-xl font-extrabold text-emerald-600 mt-1 font-mono">${filteredTickets.filter(t => t.status === 'Active').length}</span>
            </div>
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Very High / High Risks</span>
              <span class="text-xl font-extrabold text-red-600 mt-1 font-mono">${filteredTickets.filter(t => t.inherentRiskLevel === 'Very High' || t.inherentRiskLevel === 'Critical' || t.inherentRiskLevel === 'High').length}</span>
            </div>
            <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Avg Open Duration</span>
              <span class="text-xl font-extrabold text-indigo-600 mt-1 font-mono">
                ${Math.round(filteredTickets.reduce((acc, t) => acc + calculateOpenDays(t.dateRaised, t.dateClosed), 0) / (filteredTickets.length || 1))} days
              </span>
            </div>
          </div>

          <!-- Info bar -->
          <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs mb-6 flex items-center justify-between">
            <div class="text-xs text-slate-500">
              Showing <strong class="text-slate-800">${filteredTickets.length}</strong> entries. Use <kbd class="px-1.5 py-0.5 bg-slate-100 border rounded text-[10px] font-mono">Ctrl + F</kbd> to search dynamically.
            </div>
            <div class="text-[11px] text-slate-400 italic">
              * Note: All columns are fully populated according to the 36-column spreadsheet format.
            </div>
          </div>

          <!-- Table Wrapper -->
          <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
            <div class="overflow-x-auto no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden" style="scrollbar-width:none;-ms-overflow-style:none;">
              <table class="w-full table-auto border-collapse text-left min-w-[4000px] text-xs">
                <thead>
                  <tr class="bg-slate-100 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider select-none">
                    <th class="w-12 px-4 py-3.5 text-center border-r border-slate-200 bg-slate-100">Row</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">ID</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Status</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Related Issue ID</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Risk Owner</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Bundle</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Driver Tree Ref</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Risk Name</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Risk Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Cause Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Cause Category</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Consequence Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Trend</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Priority</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Highlight to/Governance Level</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Inherent Likelihood Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Inherent Consequence Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Inherent risk</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Treatment Owner</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Treatment/Mitigation Plan</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Target Date</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Residual Likelihood Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Residual Consequence Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Residual risk</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Date Raised</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Date Closed</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 font-mono">Risk Last Updated</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Comments</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Protected Issue/Risk</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">DPE Ref Number</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Timelines</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">SIgn-Off Requirement</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Executive Status</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Next Mitigation Due date</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Mitigation Status</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Strategy</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Who Raised</th>
                    <th class="px-3 py-3.5 text-center">Open Days</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 text-slate-700">
                  ${rowsHtml}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </body>
      </html>
    `);
    newWindow.document.close();
  };

  return (
    <div id="whole-data-panel" className="space-y-4 bg-slate-50/40 p-6 rounded-2xl border border-slate-200/60 shadow-xs transition-all duration-300">
      
      {/* Register Switcher Buttons at the Top */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-200 pb-4 mb-2">
        <div>
          <h2 className="text-base font-bold text-slate-800">
            {activeRegister === 'risk' ? 'Corporate Risk Register' : 'Project Issue Register'}
          </h2>
          <p className="text-xs text-slate-500">
            {activeRegister === 'risk' 
              ? 'Comprehensive treatment log of inherent and residual risk items.' 
              : 'Totally separate live list of real-time operational issues and escalation states.'}
          </p>
        </div>
        
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleClearAllClick}
            className={`flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold border rounded-lg transition-all duration-250 cursor-pointer shadow-xs ${
              confirmClear
                ? 'bg-rose-600 border-rose-600 text-white hover:bg-rose-700 animate-pulse'
                : 'text-rose-750 bg-rose-50/70 border-rose-100 hover:bg-rose-100/80 hover:text-rose-800'
            }`}
            title="Clear custom dataset from local storage and restore default baseline mock dataset"
          >
            <RotateCcw className={`w-4 h-4 ${confirmClear ? 'text-white' : 'text-rose-600'}`} />
            {confirmClear ? 'Click to CONFIRM RESET' : 'Reset to Default'}
          </button>

          <div className="relative flex bg-slate-100 p-1 rounded-xl text-xs font-semibold border border-slate-200 shadow-inner overflow-x-auto no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
            <button
              id="btn-switch-risk"
              onClick={() => setActiveRegister('risk')}
              className={`relative px-4 py-2 rounded-lg transition-colors cursor-pointer select-none z-10 ${
                activeRegister === 'risk' ? 'text-indigo-700 font-bold' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Risk Register
              {activeRegister === 'risk' && (
                <motion.div
                  layoutId="activeRegisterIndicator"
                  className="absolute inset-0 bg-white rounded-lg shadow-xs -z-10"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
            </button>
            <button
              id="btn-switch-issue"
              onClick={() => setActiveRegister('issue')}
              className={`relative px-4 py-2 rounded-lg transition-colors cursor-pointer select-none z-10 ${
                activeRegister === 'issue' ? 'text-indigo-700 font-bold' : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Issue Register
              {activeRegister === 'issue' && (
                <motion.div
                  layoutId="activeRegisterIndicator"
                  className="absolute inset-0 bg-white rounded-lg shadow-xs -z-10"
                  transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                />
              )}
            </button>
          </div>
        </div>
      </div>

      {activeRegister === 'issue' ? (
        <IssueRegisterView 
          issues={issues}
          onSaveIssue={onSaveIssue}
          onDeleteIssue={onDeleteIssue}
          onImportClick={() => { setImportType('issue'); setShowImportModal(true); }}
        />
      ) : (
        <>
      
      {/* Search & Action Bar */}
      <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search risk ID, name, owner, statement, workstream..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 placeholder:text-slate-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {matrixFilter && (
            <div className="flex items-center gap-1.5 bg-indigo-50 border border-indigo-100 text-indigo-700 px-3 py-1.5 rounded-lg text-xs">
              <span className="font-semibold">Heatmap:</span>
              <span>L{matrixFilter.likelihood} &times; C{matrixFilter.consequence} ({matrixFilter.type})</span>
              <button 
                onClick={onClearMatrixFilter}
                className="text-indigo-500 hover:text-indigo-800 font-bold ml-1 cursor-pointer"
                title="Clear heatmap filter"
              >
                &times;
              </button>
            </div>
          )}

          <button
            onClick={resetFilters}
            className="px-3.5 py-2 text-xs font-semibold text-slate-600 bg-slate-50 border border-slate-200 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            Clear Filters
          </button>

          <button
            onClick={exportToCSV}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-indigo-700 bg-indigo-50 border border-indigo-100 hover:bg-indigo-100 rounded-lg transition-colors cursor-pointer"
            title="Export full register as CSV"
          >
            <FileSpreadsheet className="w-4 h-4 text-indigo-600" />
            Export Ledger CSV
          </button>

          <button
            onClick={() => { setImportType('risk'); setShowImportModal(true); }}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-indigo-600 rounded-lg transition-colors cursor-pointer shadow-xs"
            title="Import risks from spreadsheet copy-paste or CSV file"
          >
            <Database className="w-4 h-4 text-indigo-500" />
            Import Risks
          </button>

          <button
            onClick={() => setShowRegistryModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-emerald-700 bg-emerald-50 border border-emerald-100 hover:bg-emerald-100 rounded-lg transition-colors cursor-pointer"
            title="Open complete registration details window across every column"
          >
            <Maximize2 className="w-4 h-4 text-emerald-600" />
            Open Registry Window
          </button>
        </div>
      </div>

      {/* Granular Filters Dropdown Bar */}
      <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-xs">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3.5">
          <Filter className="w-3.5 h-3.5 text-indigo-500" />
          Refine Ledger Records
        </div>

        {/* Min Risk Score Range Slider (Separated & Placed Above Dropdowns) */}
        <div className="bg-slate-50/70 border border-slate-100 rounded-xl p-3.5 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex-1">
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                Filter by Minimum Risk Score ({riskLevelType === 'inherent' ? 'Inherent' : 'Residual'})
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md font-extrabold font-mono">
                  &ge; {minRiskScore}
                </span>
                {minRiskScore > 1 && (
                  <button
                    onClick={() => setMinRiskScore(1)}
                    className="text-[10px] text-slate-400 hover:text-indigo-600 transition-colors font-semibold cursor-pointer"
                  >
                    Reset to 1
                  </button>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-slate-400 font-mono font-medium">1 (Negligible)</span>
              <input
                type="range"
                min="1"
                max="25"
                value={minRiskScore}
                onChange={(e) => setMinRiskScore(parseInt(e.target.value))}
                className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 focus:outline-hidden"
              />
              <span className="text-[10px] text-slate-400 font-mono font-medium">25 (Critical)</span>
            </div>
          </div>
        </div>

        {/* Dropdown filters grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-7 gap-3.5">
          {/* Date Range Filter */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1 flex items-center justify-between">
              <span>Date Range</span>
              {dateFilter !== 'all' && (
                <span className="text-[9px] text-indigo-600 font-semibold cursor-pointer hover:underline" onClick={() => setDateFilter('all')}>
                  Reset
                </span>
              )}
            </label>
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full text-xs p-2 bg-indigo-50/40 border border-indigo-200/80 rounded-lg text-indigo-950 font-medium focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Times (Default - Includes No Data)</option>
              <option value="7days">Last 7 Days</option>
              <option value="30days">Last 30 Days</option>
              <option value="90days">Last 90 Days</option>
              <option value="1year">Last 1 Year</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="Active">Active</option>
              <option value="Issue Eventuated">Issue Eventuated</option>
              <option value="Closed">Closed</option>
              <option value="Transferred">Transferred</option>
              <option value="Retired">Retired</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* Driver Tree Ref */}
          <div>
            <label className="block text-[10px] font-bold text-indigo-600 mb-1 flex items-center gap-1">
              Driver Tree Ref
            </label>
            <select
              value={driverTreeRefFilter}
              onChange={(e) => setDriverTreeRefFilter(e.target.value)}
              className="w-full text-xs p-2 bg-indigo-50/50 border border-indigo-200 rounded-lg text-indigo-900 font-mono font-semibold focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Driver Tree Refs</option>
              {driverTreeRefOptions.map(refVal => (
                <option key={refVal} value={refVal}>{refVal}</option>
              ))}
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Cause Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Categories</option>
              <option value="Contract & Legal">Contract & Legal</option>
              <option value="Cost">Cost</option>
              <option value="Eng capability">Eng capability</option>
              <option value="Governance Assurance">Governance Assurance</option>
              <option value="Industry">Industry</option>
              <option value="Interoperability">Interoperability</option>
              <option value="Legal/Contract">Legal/Contract</option>
              <option value="Prime Governance">Prime Governance</option>
              <option value="Product">Product</option>
              <option value="Reputation">Reputation</option>
              <option value="Schedule">Schedule</option>
              <option value="Scope">Scope</option>
              <option value="Security">Security</option>
              <option value="Security & Cyber">Security & Cyber</option>
              <option value="SovOps">SovOps</option>
              <option value="Technical Maturity">Technical Maturity</option>
              <option value="Technical Performance">Technical Performance</option>
              <option value="NA">NA</option>
              <option value="N/A">N/A</option>
              <option value="Unknown">Unknown</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Priorities</option>
              <option value="Immediate">Immediate</option>
              <option value="Urgent">Urgent</option>
              <option value="Prompt">Prompt</option>
              <option value="Not Urgent">Not Urgent</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* Governance */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Governance Level</label>
            <select
              value={govFilter}
              onChange={(e) => setGovFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Levels</option>
              <option value="Internal Google">Internal Google</option>
              <option value="Team Google">Team Google</option>
              <option value="PSG">PSG</option>
              <option value="PCG">PCG</option>
              <option value="IPF">IPF</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* Risk Level Filter with Select Type */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-[10px] font-bold text-slate-500">Risk Severity</label>
              <button
                onClick={() => setRiskLevelType(prev => prev === 'inherent' ? 'residual' : 'inherent')}
                className="text-[9px] text-indigo-600 hover:underline font-semibold cursor-pointer"
              >
                Use {riskLevelType === 'inherent' ? 'Residual' : 'Inherent'}
              </button>
            </div>
            <select
              value={riskLevelFilter}
              onChange={(e) => setRiskLevelFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Severity levels ({riskLevelType === 'inherent' ? 'Inherent' : 'Residual'})</option>
              <option value="Very High">Very High</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
              <option value="Very Low">Very Low</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-white border border-slate-100 rounded-xl shadow-xs overflow-hidden">
        <div 
          ref={riskTableContainerRef}
          onMouseDown={handleRiskMouseDown}
          onMouseMove={handleRiskMouseMove}
          onMouseUp={handleRiskMouseUpOrLeave}
          onMouseLeave={handleRiskMouseUpOrLeave}
          style={{ cursor: isRiskDragging ? 'grabbing' : 'grab' }}
          className="overflow-x-auto overflow-y-auto max-h-[650px] no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
        >
          <table className="w-full table-auto border-collapse text-left min-w-[3200px]">
            <thead className="sticky top-0 z-20 bg-slate-50 shadow-[0_1px_0_0_rgba(226,232,240,1)]">
              <tr className="bg-slate-50 text-slate-500 font-semibold text-xs border-b border-slate-100 select-none">
                <th className="w-12 px-4 py-3 text-center bg-slate-50 border-r border-slate-200">Row</th>
                <th onClick={() => handleSort('id')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">ID <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('status')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Status <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('relatedIssueId' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Related Issue ID <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('riskOwner')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Risk Owner <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('bundle')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Bundle <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('driverTreeRef' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Driver Tree Ref <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('riskName')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Risk Name <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('riskDescription')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Risk Description <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('causeDescription')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Cause Description <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('causeCategory')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Cause Category <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('consequenceDescription')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Consequence Description <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('trend')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Trend <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('priority')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Priority <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('governanceLevel')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Highlight to/Governance Level <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('inherentLikelihood')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Inherent Likelihood Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('inherentConsequence')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Inherent Consequence Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('inherentRiskScore')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Inherent risk <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('treatmentOwner')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Treatment Owner <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('treatmentPlan')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Treatment/Mitigation Plan <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('targetDate')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Target Date <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('residualLikelihood')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Residual Likelihood Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('residualConsequence')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Residual Consequence Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('residualRiskScore')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 text-center">
                  <div className="flex items-center justify-center gap-1">Residual risk <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('dateRaised')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Date Raised <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('dateClosed' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Date Closed <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('riskLastUpdated' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Risk Last Updated <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('comments' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Comments <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('protectedIssueRisk' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Protected Issue/Risk <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('dpeRefNumber' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">DPE Ref Number <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('timelines' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Timelines <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('signOffRequirement' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">SIgn-Off Requirement <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('executiveStatus' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 border-r border-slate-200">
                  <div className="flex items-center gap-1">Executive Status <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('nextMitigationDueDate' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Next Mitigation Due date <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('mitigationStatus' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Mitigation Status <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('strategy' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Strategy <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('whoRaised' as keyof RiskTicket)} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Who Raised <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-3 bg-slate-50 border-r border-slate-200 font-bold text-center">
                  <div className="flex items-center justify-center gap-1">Open Days</div>
                </th>
                <th className="px-4 py-3 text-right bg-slate-50 sticky right-0 z-10 w-24">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {filteredTickets.length > 0 ? (
                filteredTickets.map((t, index) => {
                  const isExpanded = !!expandedRows[t.id];
                  
                  return (
                    <React.Fragment key={`${t.id || 'rsk'}-${index}`}>
                      {/* Main Row */}
                      <tr className={`hover:bg-slate-50/60 transition-colors ${isExpanded ? 'bg-indigo-50/10' : ''}`}>
                        <td className="px-4 py-3.5 text-center text-slate-400 font-mono text-[11px] border-r border-slate-100 bg-slate-50/20">
                          {index + 1}
                        </td>
                        <td className="px-3 py-3.5 font-semibold text-slate-700 font-mono border-r border-slate-100 select-all">
                          {t.id}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100">
                          <span className={`px-2.5 py-1 text-[10px] font-bold border rounded-full uppercase ${STATUS_COLORS[t.status]}`}>
                            {t.status}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-600 border-r border-slate-100">
                          {t.relatedIssueId || `ISS-${200 + index}`}
                        </td>
                        <td className="px-3 py-3.5 text-slate-700 border-r border-slate-100 font-medium">
                          {t.riskOwner}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100">
                          <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-medium">
                            {t.bundle || 'N/A'}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-600 border-r border-slate-100">
                          {t.driverTreeRef || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 font-semibold text-slate-800 max-w-[200px] truncate border-r border-slate-100" title={t.riskName}>
                          {t.riskName}
                        </td>
                        <td className="px-3 py-3.5 text-slate-600 max-w-[250px] truncate border-r border-slate-100 italic" title={t.riskDescription}>
                          {t.riskDescription}
                        </td>
                        <td className="px-3 py-3.5 text-slate-500 max-w-[250px] truncate border-r border-slate-100" title={t.causeDescription}>
                          {t.causeDescription || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100">
                          <span className="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-medium">
                            {t.causeCategory}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 text-slate-500 max-w-[250px] truncate border-r border-slate-100" title={t.consequenceDescription}>
                          {t.consequenceDescription || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100 font-semibold">
                          <span className={`${t.trend === 'Increasing' ? 'text-red-600' : t.trend === 'Decreasing' ? 'text-emerald-600' : 'text-slate-600'}`}>
                            {t.trend}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100">
                          <span className={`px-2 py-0.5 text-[10px] font-semibold border rounded ${PRIORITY_COLORS[t.priority]}`}>
                            {t.priority}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 text-slate-600 border-r border-slate-100 font-medium">
                          {t.governanceLevel}
                        </td>
                        {/* Ratings */}
                        <td className="px-3 py-3.5 text-center font-semibold border-r border-slate-100">
                          {t.inherentLikelihood ? (LIKELIHOOD_LABELS[t.inherentLikelihood] || t.inherentLikelihood) : 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center font-semibold border-r border-slate-100">
                          {t.inherentConsequence ? (CONSEQUENCE_LABELS[t.inherentConsequence] || t.inherentConsequence) : 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center border-r border-slate-100">
                          <span className={`text-[10px] px-2 py-0.5 rounded-sm font-semibold uppercase ${RISK_LEVEL_COLORS[t.inherentRiskLevel]?.bg || 'bg-slate-100'} ${RISK_LEVEL_COLORS[t.inherentRiskLevel]?.text || 'text-slate-600'}`}>
                            {t.inherentRiskScore ? `${t.inherentRiskScore} (${t.inherentRiskLevel})` : '-'}
                          </span>
                        </td>
                        {/* Treatments */}
                        <td className="px-3 py-3.5 text-slate-700 border-r border-slate-100 font-medium">
                          {t.treatmentOwner || 'Unassigned'}
                        </td>
                        <td className="px-3 py-3.5 text-slate-500 max-w-[250px] truncate border-r border-slate-100" title={t.treatmentPlan}>
                          {t.treatmentPlan || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-500 border-r border-slate-100">
                          {t.targetDate || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center font-semibold border-r border-slate-100">
                          {t.residualLikelihood ? (LIKELIHOOD_LABELS[t.residualLikelihood] || t.residualLikelihood) : 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center font-semibold border-r border-slate-100">
                          {t.residualConsequence ? (CONSEQUENCE_LABELS[t.residualConsequence] || t.residualConsequence) : 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center border-r border-slate-100">
                          <span className={`text-[10px] px-2 py-0.5 rounded-sm font-semibold uppercase ${RISK_LEVEL_COLORS[t.residualRiskLevel]?.bg || 'bg-slate-100'} ${RISK_LEVEL_COLORS[t.residualRiskLevel]?.text || 'text-slate-600'}`}>
                            {t.residualRiskScore ? `${t.residualRiskScore} (${t.residualRiskLevel})` : '-'}
                          </span>
                        </td>
                        {/* Extra Attributes */}
                        <td className="px-3 py-3.5 font-mono text-slate-500 border-r border-slate-100">
                          {t.dateRaised}
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-500 border-r border-slate-100">
                          {t.dateClosed || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-500 border-r border-slate-100">
                          {t.riskLastUpdated || t.dateClosed || t.dateRaised}
                        </td>
                        <td className="px-3 py-3.5 text-slate-500 max-w-[250px] truncate border-r border-slate-100" title={t.comments}>
                          {t.comments || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100 text-slate-600 font-medium">
                          {t.protectedIssueRisk || 'No'}
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-600 border-r border-slate-100">
                          {t.dpeRefNumber || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-slate-600 border-r border-slate-100">
                          {t.timelines || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100 text-slate-600">
                          {t.signOffRequirement || 'No'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100">
                          <span className={`px-2 py-0.5 text-[10px] font-semibold rounded border ${t.executiveStatus === 'Approved' ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-slate-50 text-slate-600 border-slate-100'}`}>
                            {t.executiveStatus || 'Pending'}
                          </span>
                        </td>
                        <td className="px-3 py-3.5 font-mono text-slate-500 border-r border-slate-100">
                          {t.nextMitigationDueDate || t.targetDate || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100 text-slate-600">
                          {t.mitigationStatus || 'Pending'}
                        </td>
                        <td className="px-3 py-3.5 border-r border-slate-100 text-slate-600 font-medium">
                          {t.strategy || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-slate-600 border-r border-slate-100 font-medium">
                          {t.whoRaised || 'N/A'}
                        </td>
                        <td className="px-3 py-3.5 text-center font-mono font-bold text-slate-700 bg-slate-50/10 border-r border-slate-100">
                          {calculateOpenDays(t.dateRaised, t.dateClosed)}
                        </td>
                        {/* Row Actions */}
                        <td className="px-4 py-3.5 text-right sticky right-0 z-10 bg-white shadow-[-4px_0_12px_-4px_rgba(0,0,0,0.1)]">
                          <div className="flex items-center justify-end gap-1.5">
                            <button
                              onClick={() => toggleRow(t.id)}
                              className="p-1.5 rounded-lg text-indigo-650 hover:bg-indigo-50 transition-all duration-150 cursor-pointer flex items-center gap-1 text-[11px] font-bold"
                              title="Toggle Detail View"
                            >
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                              {isExpanded ? 'Hide' : 'View'}
                            </button>
                          </div>
                        </td>
                      </tr>
 
                      {/* Expandable Detail View */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={38} className="bg-slate-50 border-t border-b border-indigo-50 p-4 sticky left-0 max-w-[calc(100vw-80px)]">
                            <div className="grid grid-cols-1 md:grid-cols-12 gap-5 text-xs text-slate-600">
                              
                              {/* Left details panel: Risk & Cause */}
                              <div className="md:col-span-6 space-y-3 bg-white p-4 rounded-xl border border-slate-100 shadow-2xs">
                                <div>
                                  <h4 className="font-bold text-slate-800 flex items-center gap-1">
                                    <AlertCircle className="w-4 h-4 text-indigo-500" />
                                    Risk Formulation Statement (IF - THEN)
                                  </h4>
                                  <p className="mt-1 bg-slate-50 p-2.5 rounded border border-slate-100 italic leading-relaxed text-slate-700">
                                    {t.riskDescription}
                                  </p>
                                </div>

                                <div className="grid grid-cols-2 gap-4 pt-1">
                                  <div>
                                    <span className="font-bold text-slate-800 block">Root Cause Description</span>
                                    <p className="mt-1 text-slate-600">{t.causeDescription || 'No detailed cause provided.'}</p>
                                  </div>
                                  <div>
                                    <span className="font-bold text-slate-800 block">Consequence / Impact Description</span>
                                    <p className="mt-1 text-slate-600">{t.consequenceDescription || 'No detailed consequence provided.'}</p>
                                  </div>
                                </div>

                                <div className="grid grid-cols-3 gap-2.5 border-t border-slate-100 pt-3 text-[11px]">
                                  <div>
                                    <strong className="text-slate-400 block">Trend Indicator</strong>
                                    <span className={`font-semibold ${t.trend === 'Increasing' ? 'text-red-600' : t.trend === 'Decreasing' ? 'text-emerald-600' : 'text-slate-600'}`}>
                                      {t.trend}
                                    </span>
                                  </div>
                                  <div>
                                    <strong className="text-slate-400 block">Date Raised</strong>
                                    <span>{t.dateRaised}</span>
                                  </div>
                                  <div>
                                    <strong className="text-slate-400 block">Governance Level</strong>
                                    <span className="font-medium">{t.governanceLevel}</span>
                                  </div>
                                </div>
                              </div>

                              {/* Right details panel: Treatment & Residuals */}
                              <div className="md:col-span-6 space-y-3 bg-white p-4 rounded-xl border border-slate-100 shadow-2xs flex flex-col justify-between">
                                <div className="space-y-3">
                                  <h4 className="font-bold text-slate-800 flex items-center gap-1 border-b border-slate-50 pb-1.5">
                                    <FileSpreadsheet className="w-4 h-4 text-emerald-500" />
                                    Risk Treatment & Mitigation Control
                                  </h4>
                                  
                                  <div className="grid grid-cols-2 gap-2.5">
                                    <div>
                                      <span className="font-bold text-slate-800 block text-[11px]">Treatment Owner</span>
                                      <p className="mt-0.5 text-slate-600 font-medium">{t.treatmentOwner || 'Unassigned'}</p>
                                    </div>
                                    <div>
                                      <span className="font-bold text-slate-800 block text-[11px]">Target Date</span>
                                      <p className="mt-0.5 text-slate-600 font-mono">{t.targetDate || 'No date set'}</p>
                                    </div>
                                  </div>

                                  <div>
                                    <span className="font-bold text-slate-800 block">Action Control Plan</span>
                                    <p className="mt-1 bg-emerald-50/20 p-2 border border-emerald-100/50 rounded text-slate-700 leading-relaxed">
                                      {t.treatmentPlan || 'No control actions defined.'}
                                    </p>
                                  </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100 text-center">
                                  <div>
                                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Inherent Matrix Rating</span>
                                    <span className="font-bold text-slate-800">
                                      L{t.inherentLikelihood} & C{t.inherentConsequence} &rarr; Score: {t.inherentRiskScore}
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Residual Matrix Rating</span>
                                    <span className="font-bold text-emerald-700">
                                      L{t.residualLikelihood} & C{t.residualConsequence} &rarr; Score: {t.residualRiskScore}
                                    </span>
                                  </div>
                                </div>
                              </div>

                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-400">
                    <div className="flex flex-col items-center justify-center gap-1.5">
                      <HelpCircle className="w-8 h-8 text-slate-300" />
                      <span className="font-medium text-slate-500">No matching risk statements found</span>
                      <p className="text-[11px] text-slate-400">
                        Try adjusting your search criteria or clear the filter attributes.
                      </p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Table Summary Footer */}
        <div className="bg-slate-50 border-t border-slate-100 px-4 py-3 text-[11px] text-slate-500 flex items-center justify-between">
          <div>
            Showing <strong className="text-slate-700">{filteredTickets.length}</strong> of <strong className="text-slate-700">{tickets.length}</strong> registered risk statements
          </div>
          <div>
            Data is persisted in client localStorage.
          </div>
        </div>
      </div>

      {/* 36-COLUMN FULL REGISTRY MODAL WINDOW OVERLAY */}
      {showRegistryModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 md:p-6 animate-fadeIn">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full h-[90vh] flex flex-col overflow-hidden max-w-[96vw]">
            
            {/* Modal Header */}
            <div className="bg-slate-900 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                <div>
                  <h2 className="text-sm font-extrabold tracking-tight uppercase text-slate-100 flex items-center gap-2">
                    Corporate Risk Registry — Master Ledger View
                  </h2>
                  <p className="text-[10px] text-slate-400 mt-0.5 font-medium">
                    Displaying 36 high-fidelity database columns across {filteredTickets.length} active matching ledger records
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* Master Ledger Directional Scroll Controls */}
                <div className="flex items-center bg-slate-800/80 p-1 rounded-xl border border-slate-700/60 mr-1.5 shadow-inner">
                  <span className="text-[9px] text-slate-400 uppercase tracking-wider font-extrabold px-2.5 font-mono select-none">
                    Navigate:
                  </span>
                  <div className="flex items-center gap-0.5">
                    <button
                      onClick={() => scrollModalTable('left')}
                      className="p-1.5 text-slate-300 hover:text-emerald-400 hover:bg-slate-750 rounded-lg transition-all duration-150 cursor-pointer border border-transparent hover:border-slate-700/50 active:scale-95"
                      title="Scroll Left (400px)"
                    >
                      <ArrowLeft className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => scrollModalTable('right')}
                      className="p-1.5 text-slate-300 hover:text-emerald-400 hover:bg-slate-750 rounded-lg transition-all duration-150 cursor-pointer border border-transparent hover:border-slate-700/50 active:scale-95"
                      title="Scroll Right (400px)"
                    >
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => scrollModalTable('up')}
                      className="p-1.5 text-slate-300 hover:text-emerald-400 hover:bg-slate-750 rounded-lg transition-all duration-150 cursor-pointer border border-transparent hover:border-slate-700/50 active:scale-95"
                      title="Scroll Up (200px)"
                    >
                      <ArrowUp className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => scrollModalTable('down')}
                      className="p-1.5 text-slate-300 hover:text-emerald-400 hover:bg-slate-750 rounded-lg transition-all duration-150 cursor-pointer border border-transparent hover:border-slate-700/50 active:scale-95"
                      title="Scroll Down (200px)"
                    >
                      <ArrowDown className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <button
                  onClick={openNewWindow}
                  className="flex items-center gap-1.5 px-3.5 py-2 text-[11px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-950/50 border border-indigo-900 hover:border-indigo-800 rounded-lg transition-colors cursor-pointer"
                  title="Open in a new standalone browser tab/window"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Launch Pop-out Tab
                </button>

                <button
                  onClick={exportToCSV}
                  className="flex items-center gap-1.5 px-3.5 py-2 text-[11px] font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded-lg transition-colors cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  Download CSV
                </button>

                <button
                  onClick={() => setShowRegistryModal(false)}
                  className="px-3.5 py-2 text-[11px] font-bold bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors cursor-pointer"
                >
                  Close Window
                </button>
              </div>
            </div>

            {/* Quick Context / Instruction Bar */}
            <div className="bg-slate-50 border-b border-slate-100 px-6 py-2.5 text-[11px] text-slate-500 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-1.5">
                <span>Active Filters:</span>
                <span className="font-semibold text-slate-700 bg-slate-200/60 px-2 py-0.5 rounded text-[10px]">
                  {searchTerm ? `Search: "${searchTerm}"` : "All Records"}
                </span>
                {statusFilter !== 'all' && (
                  <span className="font-semibold text-slate-700 bg-slate-200/60 px-2 py-0.5 rounded text-[10px]">
                    Status: {statusFilter}
                  </span>
                )}
                {categoryFilter !== 'all' && (
                  <span className="font-semibold text-slate-700 bg-slate-200/60 px-2 py-0.5 rounded text-[10px]">
                    Category: {categoryFilter}
                  </span>
                )}
              </div>
              <div className="font-mono text-[10px] text-slate-400">
                * Scroll horizontally and vertically to view all 36 spreadsheet columns in high density.
              </div>
            </div>

            {/* Table Container */}
            <div className="flex-1 overflow-auto bg-slate-100/30 p-2">
              <div className="bg-white border border-slate-200/80 rounded-xl overflow-hidden shadow-sm h-full flex flex-col">
                <div 
                  ref={modalTableContainerRef}
                  onMouseDown={handleModalMouseDown}
                  onMouseMove={handleModalMouseMove}
                  onMouseUp={handleModalMouseUpOrLeave}
                  onMouseLeave={handleModalMouseUpOrLeave}
                  style={{ cursor: isModalDragging ? 'grabbing' : 'grab' }}
                  className="overflow-auto flex-1 no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
                >
                  <table className="w-full table-auto border-collapse text-left min-w-[4500px] text-xs">
                    <thead className="sticky top-0 z-10">
                      <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider select-none text-[10px]">
                        <th className="w-12 px-4 py-3 text-center border-r border-slate-200 bg-slate-100 sticky left-0 z-20">Row</th>
                        <th onClick={() => handleSort('id')} className="px-3 py-3 border-r border-slate-200 sticky left-12 bg-slate-100 z-20 cursor-pointer hover:bg-slate-200 transition-colors">
                          <div className="flex items-center gap-1">ID {renderSortIcon('id')}</div>
                        </th>
                        <th className="px-3 py-3 border-r border-slate-200">Status</th>
                        <th className="px-3 py-3 border-r border-slate-200">Related Issue ID</th>
                        <th className="px-3 py-3 border-r border-slate-200">Risk Owner</th>
                        <th className="px-3 py-3 border-r border-slate-200">Bundle</th>
                        <th className="px-3 py-3 border-r border-slate-200">Driver Tree Ref</th>
                        <th className="px-3 py-3 border-r border-slate-200">Risk Name</th>
                        <th className="px-3 py-3 border-r border-slate-200">Risk Description</th>
                        <th className="px-3 py-3 border-r border-slate-200">Cause Description</th>
                        <th className="px-3 py-3 border-r border-slate-200">Cause Category</th>
                        <th className="px-3 py-3 border-r border-slate-200">Consequence Description</th>
                        <th className="px-3 py-3 border-r border-slate-200">Trend</th>
                        <th className="px-3 py-3 border-r border-slate-200">Priority</th>
                        <th className="px-3 py-3 border-r border-slate-200">Highlight to/Governance Level</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Inherent Likelihood Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Inherent Consequence Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Inherent risk</th>
                        <th className="px-3 py-3 border-r border-slate-200">Treatment Owner</th>
                        <th className="px-3 py-3 border-r border-slate-200">Treatment/Mitigation Plan</th>
                        <th className="px-3 py-3 border-r border-slate-200">Target Date</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Residual Likelihood Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Residual Consequence Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Residual risk</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Date Raised</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Date Closed</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Risk Last Updated</th>
                        <th className="px-3 py-3 border-r border-slate-200">Comments</th>
                        <th className="px-3 py-3 border-r border-slate-200">Protected Issue/Risk</th>
                        <th className="px-3 py-3 border-r border-slate-200">DPE Ref Number</th>
                        <th className="px-3 py-3 border-r border-slate-200">Timelines</th>
                        <th className="px-3 py-3 border-r border-slate-200">SIgn-Off Requirement</th>
                        <th className="px-3 py-3 border-r border-slate-200">Executive Status</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Next Mitigation Due date</th>
                        <th className="px-3 py-3 border-r border-slate-200">Mitigation Status</th>
                        <th className="px-3 py-3 border-r border-slate-200">Strategy</th>
                        <th className="px-3 py-3 border-r border-slate-200">Who Raised</th>
                        <th className="px-3 py-3 text-center">Open Days</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {filteredTickets.map((t, idx) => {
                        const openDays = calculateOpenDays(t.dateRaised, t.dateClosed);
                        const isEven = idx % 2 === 0;
                        const rowBg = isEven ? 'bg-white' : 'bg-slate-50/30';
                        return (
                          <tr key={`${t.id || 'rsk'}-${idx}`} className={`${rowBg} hover:bg-slate-50 transition-colors`}>
                            <td className="px-4 py-2.5 text-center text-slate-400 font-mono text-[11px] bg-slate-50 border-r border-slate-200 sticky left-0 z-10">{idx + 1}</td>
                            <td 
                              onClick={() => {
                                onEdit(t);
                                setShowRegistryModal(false);
                              }}
                              className="px-3 py-2.5 font-bold text-indigo-600 font-mono border-r border-slate-200 sticky left-12 bg-slate-50 hover:bg-indigo-50/50 hover:text-indigo-800 transition-all duration-150 z-10 cursor-pointer group"
                              title="Click to Edit Risk"
                            >
                              <div className="flex items-center justify-between gap-1.5">
                                <span>{t.id}</span>
                                <Pencil className="w-2.5 h-2.5 text-indigo-500 opacity-0 group-hover:opacity-100 transition-all duration-150 transform translate-x-1 group-hover:translate-x-0 cursor-pointer" />
                              </div>
                            </td>
                            <td className="px-3 py-2.5 border-r border-slate-200">
                              <span className={`px-2 py-0.5 text-[9px] font-bold border rounded-full uppercase ${
                                t.status === 'Active' ? 'bg-sky-50 text-sky-700 border-sky-200' :
                                t.status === 'Closed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                t.status === 'Issue Eventuated' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                                'bg-slate-50 text-slate-500 border-slate-200'
                              }`}>{t.status}</span>
                            </td>
                            <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{t.relatedIssueId || `ISS-${200 + idx}`}</td>
                            <td className="px-3 py-2.5 text-slate-700 border-r border-slate-200 font-semibold">{t.riskOwner}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200">
                              <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-medium">{t.bundle || 'N/A'}</span>
                            </td>
                            <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{t.driverTreeRef || 'N/A'}</td>
                            <td className="px-3 py-2.5 font-bold text-slate-800 border-r border-slate-200">{t.riskName}</td>
                            <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200 italic max-w-sm truncate" title={t.riskDescription}>{t.riskDescription}</td>
                            <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-xs truncate" title={t.causeDescription}>{t.causeDescription || 'N/A'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200">
                              <span className="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-medium">{t.causeCategory}</span>
                            </td>
                            <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-xs truncate" title={t.consequenceDescription}>{t.consequenceDescription || 'N/A'}</td>
                            <td className={`px-3 py-2.5 border-r border-slate-200 font-semibold ${
                              t.trend === 'Increasing' ? 'text-rose-600' :
                              t.trend === 'Decreasing' ? 'text-emerald-600' : 'text-slate-500'
                            }`}>{t.trend}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200">
                              <span className={`px-2 py-0.5 text-[9px] font-semibold border rounded ${
                                t.priority === 'Immediate' ? 'bg-red-50 text-red-700 border-red-200' :
                                t.priority === 'Urgent' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                                t.priority === 'Prompt' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                                'bg-slate-50 text-slate-500 border-slate-200'
                              }`}>{t.priority}</span>
                            </td>
                            <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200 font-medium">{t.governanceLevel}</td>
                            <td className="px-3 py-2.5 text-center font-semibold border-r border-slate-200 text-slate-700 bg-slate-50/40">{LIKELIHOOD_LABELS[t.inherentLikelihood] || t.inherentLikelihood}</td>
                            <td className="px-3 py-2.5 text-center font-semibold border-r border-slate-200 text-slate-700 bg-slate-50/40">{CONSEQUENCE_LABELS[t.inherentConsequence] || t.inherentConsequence}</td>
                            <td className="px-3 py-2.5 text-center border-r border-slate-200 bg-slate-50/60">
                              <span className={`text-[9px] px-2 py-0.5 rounded-sm font-bold uppercase ${
                                t.inherentRiskLevel === 'Very High' || t.inherentRiskLevel === 'Critical' ? 'bg-[#ea4335] text-white' :
                                t.inherentRiskLevel === 'High' ? 'bg-[#ff9900] text-white' :
                                t.inherentRiskLevel === 'Medium' ? 'bg-[#eedb33] text-amber-950 border border-amber-300/30' :
                                t.inherentRiskLevel === 'Low' ? 'bg-[#34a853] text-white' :
                                'bg-[#93c47d] text-slate-900'
                              }`}>{t.inherentRiskScore} ({t.inherentRiskLevel})</span>
                            </td>
                            <td className="px-3 py-2.5 text-slate-700 border-r border-slate-200 font-semibold">{t.treatmentOwner || 'Unassigned'}</td>
                            <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-sm truncate" title={t.treatmentPlan}>{t.treatmentPlan || 'N/A'}</td>
                            <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{t.targetDate || 'N/A'}</td>
                            <td className="px-3 py-2.5 text-center font-semibold border-r border-slate-200 text-slate-700 bg-slate-50/40">{LIKELIHOOD_LABELS[t.residualLikelihood] || t.residualLikelihood}</td>
                            <td className="px-3 py-2.5 text-center font-semibold border-r border-slate-200 text-slate-700 bg-slate-50/40">{CONSEQUENCE_LABELS[t.residualConsequence] || t.residualConsequence}</td>
                            <td className="px-3 py-2.5 text-center border-r border-slate-200 bg-slate-50/60">
                              <span className={`text-[9px] px-2 py-0.5 rounded-sm font-bold uppercase ${
                                t.residualRiskLevel === 'Very High' || t.residualRiskLevel === 'Critical' ? 'bg-[#ea4335] text-white' :
                                t.residualRiskLevel === 'High' ? 'bg-[#ff9900] text-white' :
                                t.residualRiskLevel === 'Medium' ? 'bg-[#eedb33] text-amber-950 border border-amber-300/30' :
                                t.residualRiskLevel === 'Low' ? 'bg-[#34a853] text-white' :
                                'bg-[#93c47d] text-slate-900'
                              }`}>{t.residualRiskScore} ({t.residualRiskLevel})</span>
                            </td>
                            <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{t.dateRaised}</td>
                            <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{t.dateClosed || 'N/A'}</td>
                            <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{t.riskLastUpdated || t.dateClosed || t.dateRaised}</td>
                            <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-xs truncate" title={t.comments}>{t.comments || 'N/A'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200 text-slate-600 font-medium">{t.protectedIssueRisk || 'No'}</td>
                            <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{t.dpeRefNumber || 'N/A'}</td>
                            <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200">{t.timelines || 'N/A'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200 text-slate-600">{t.signOffRequirement || 'No'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200">
                              <span className={`px-2 py-0.5 text-[9px] font-semibold border rounded ${
                                (t.executiveStatus || 'Pending') === 'Approved' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                                (t.executiveStatus || 'Pending') === 'Under Review' ? 'bg-amber-50 text-amber-700 border-amber-200' :
                                'bg-slate-50 text-slate-500 border-slate-200'
                              }`}>{t.executiveStatus || 'Pending'}</span>
                            </td>
                            <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{t.nextMitigationDueDate || t.targetDate || 'N/A'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200 text-slate-600">{t.mitigationStatus || 'Pending'}</td>
                            <td className="px-3 py-2.5 border-r border-slate-200 text-slate-600 font-medium">{t.strategy || 'N/A'}</td>
                            <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200 font-medium">{t.whoRaised || 'N/A'}</td>
                            <td className="px-3 py-2.5 text-center font-mono font-bold text-slate-700 bg-slate-50">{openDays}</td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Modal Footer Summary */}
                <div className="bg-slate-50 border-t border-slate-200 px-6 py-3 text-xs text-slate-500 flex items-center justify-between">
                  <div>
                    Displaying <strong>{filteredTickets.length}</strong> risk entries with complete columns
                  </div>
                  <div>
                    Use scrollbars to navigate columns and rows
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      )}
        </>
      )}

      {/* Import Data Modal */}
      <ImportDataModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        type={importType}
        existingCount={importType === 'risk' ? tickets.length : issues.length}
        onImportRisks={onImportRisks}
        onImportIssues={onImportIssues}
      />
    </div>
  );
}
