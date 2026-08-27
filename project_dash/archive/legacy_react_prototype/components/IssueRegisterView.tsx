import React, { useState, useMemo, useRef, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  Download, 
  Edit2, 
  Trash2, 
  ChevronDown, 
  ChevronUp, 
  Calendar, 
  User, 
  FileSpreadsheet, 
  Briefcase,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  Maximize2,
  Pencil,
  PlusCircle,
  Activity,
  ShieldAlert,
  TrendingUp,
  X,
  Database
} from 'lucide-react';
import { IssueTicket, isDriverTreeRefMatch, DRIVER_TREE_REF_ORDERED_OPTIONS } from '../types';

interface IssueRegisterViewProps {
  issues: IssueTicket[];
  onSaveIssue: (issue: IssueTicket) => Promise<void>;
  onDeleteIssue: (id: string) => Promise<void>;
  onImportClick?: () => void;
  overrideSearchTerm?: string;
}

export default function IssueRegisterView({ 
  issues, 
  onSaveIssue, 
  onDeleteIssue,
  onImportClick,
  overrideSearchTerm
}: IssueRegisterViewProps) {
  // Drag-to-scroll handlers and states for the issue table
  const issueTableContainerRef = useRef<HTMLDivElement>(null);
  const [isIssueDragging, setIsIssueDragging] = useState(false);
  const [issueDragStartX, setIssueDragStartX] = useState(0);
  const [issueDragStartY, setIssueDragStartY] = useState(0);
  const [issueDragScrollLeft, setIssueDragScrollLeft] = useState(0);
  const [issueDragScrollTop, setIssueDragScrollTop] = useState(0);

  const handleIssueMouseDown = (e: React.MouseEvent) => {
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
    const container = issueTableContainerRef.current;
    if (!container) return;
    setIsIssueDragging(true);
    setIssueDragStartX(e.pageX - container.offsetLeft);
    setIssueDragStartY(e.pageY - container.offsetTop);
    setIssueDragScrollLeft(container.scrollLeft);
    setIssueDragScrollTop(container.scrollTop);
  };

  const handleIssueMouseMove = (e: React.MouseEvent) => {
    if (!isIssueDragging) return;
    const container = issueTableContainerRef.current;
    if (!container) return;
    e.preventDefault();
    const x = e.pageX - container.offsetLeft;
    const y = e.pageY - container.offsetTop;
    const walkX = (x - issueDragStartX) * 1.5; // Sensitivity multiplier
    const walkY = (y - issueDragStartY) * 1.5;
    container.scrollLeft = issueDragScrollLeft - walkX;
    container.scrollTop = issueDragScrollTop - walkY;
  };

  const handleIssueMouseUpOrLeave = () => {
    setIsIssueDragging(false);
  };

  // Filters & Search
  const [searchTerm, setSearchTerm] = useState(overrideSearchTerm || '');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [driverTreeRefFilter, setDriverTreeRefFilter] = useState<string>('all');
  const [minSeverity, setMinSeverity] = useState<number>(1);

  // Available Driver Tree Ref Options for dropdown in exact requested order
  const driverTreeRefOptions = useMemo(() => {
    const list = [...DRIVER_TREE_REF_ORDERED_OPTIONS];
    const knownSet = new Set(list);
    const extraRefs: string[] = [];
    issues.forEach(i => {
      if (i.driverTreeRef && i.driverTreeRef.trim()) {
        const ref = i.driverTreeRef.trim();
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
  }, [issues]);

  useEffect(() => {
    if (overrideSearchTerm !== undefined) {
      setSearchTerm(overrideSearchTerm);
    }
  }, [overrideSearchTerm]);

  // Sorting
  const [sortField, setSortField] = useState<keyof IssueTicket>('id');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Row Expansion State
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});

  // Issue Form & Modal Overlay
  const [showModal, setShowModal] = useState(false);
  const [editingIssue, setEditingIssue] = useState<IssueTicket | null>(null);
  const [form, setForm] = useState<Partial<IssueTicket>>({});

  // Standalone window popup modal
  const [showRegistryModal, setShowRegistryModal] = useState(false);

  // Sorting handler
  const handleSort = (field: keyof IssueTicket) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Toggle detail rows
  const toggleRow = (id: string) => {
    setExpandedRows(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // Filter & Sort computation
  const filteredIssues = useMemo(() => {
    return issues
      .filter(i => {
        const text = searchTerm.toLowerCase();
        const matchesSearch = 
          i.id.toLowerCase().includes(text) ||
          i.issueName.toLowerCase().includes(text) ||
          i.issueOwner.toLowerCase().includes(text) ||
          i.bundle.toLowerCase().includes(text) ||
          i.issueDescription.toLowerCase().includes(text) ||
          (i.relatedRiskId && i.relatedRiskId.toLowerCase().includes(text)) ||
          (i.driverTreeRef && i.driverTreeRef.toLowerCase().includes(text)) ||
          (i.impactCategory && i.impactCategory.toLowerCase().includes(text));

        const matchesStatus = statusFilter === 'all' || i.status === statusFilter;
        const matchesPriority = priorityFilter === 'all' || i.priorityRating === priorityFilter;
        const matchesSeverity = severityFilter === 'all' || i.severityRating === severityFilter;

        const severityScores: Record<string, number> = { 'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4 };
        const currentSeverityScore = severityScores[i.severityRating] || 1;
        const matchesMinSeverity = currentSeverityScore >= minSeverity;

        let matchesDriverTreeRef = true;
        if (driverTreeRefFilter !== 'all') {
          matchesDriverTreeRef = isDriverTreeRefMatch(i.driverTreeRef, driverTreeRefFilter);
        }

        return matchesSearch && matchesStatus && matchesPriority && matchesSeverity && matchesMinSeverity && matchesDriverTreeRef;
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
  }, [issues, searchTerm, statusFilter, priorityFilter, severityFilter, driverTreeRefFilter, minSeverity, sortField, sortDirection]);

  // Next consecutive issue ID helper
  const getNextId = () => {
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

  // Add issue helper
  const handleAddClick = () => {
    setForm({
      id: getNextId(),
      status: 'Open',
      relatedRiskId: '',
      issueOwner: '',
      bundle: '',
      issueName: '',
      issueDescription: '',
      causeDescription: '',
      impactCategory: 'Operational',
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
    setShowModal(true);
  };

  // Edit issue helper
  const handleEditClick = (issue: IssueTicket) => {
    setForm({ ...issue });
    setEditingIssue(issue);
    setShowModal(true);
  };

  // Submit form handler
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.id || !form.issueName || !form.issueOwner) return;
    
    // Auto populate last updated
    const updatedForm = {
      ...form,
      lastUpdated: new Date().toISOString().split('T')[0]
    } as IssueTicket;

    await onSaveIssue(updatedForm);
    setShowModal(false);
  };

  // Export CSV
  const exportToCSV = () => {
    const headers = [
      'ID', 'Status', 'Related Risk ID', 'Issue owner', 'Bundle', 'Driver Tree Ref', 'Issue Name', 'Issue Description',
      'Cause Description', 'Impact Category', 'Consequence', 'Trend', 'Priority Rating',
      'Escalate to:', 'Severity Rating', 'Action Plan ( What, When, Who)', 'Next Action owner', 'Date Raised', 'Raised by',
      'Date Closed', 'Last Updated', 'Protected Issue/Risk', 'DPE Ref Number'
    ];

    const rows = filteredIssues.map(i => [
      i.id,
      i.status,
      i.relatedRiskId || 'N/A',
      i.issueOwner,
      i.bundle || 'N/A',
      i.driverTreeRef || 'N/A',
      i.issueName,
      i.issueDescription,
      i.causeDescription,
      i.impactCategory || 'N/A',
      i.consequence || 'N/A',
      i.trend,
      i.priorityRating,
      i.escalateTo || 'N/A',
      i.severityRating,
      i.actionPlan,
      i.nextActionOwner || i.issueOwner || 'N/A',
      i.dateRaised,
      i.raisedBy,
      i.dateClosed || 'N/A',
      i.lastUpdated,
      i.protectedIssueRisk,
      i.dpeRefNumber || 'N/A'
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

  // Open standalone popup browser tab
  const openPopOutWindow = () => {
    const newWindow = window.open('', '_blank', 'width=1400,height=900,scrollbars=yes,resizable=yes');
    if (!newWindow) {
      alert('Popup window blocked! Please allow popups for this site.');
      return;
    }

    const rowsHtml = filteredIssues.map((i, idx) => `
      <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100 text-[11px]">
        <td class="px-4 py-3 text-center text-slate-400 font-mono border-r border-slate-100">${idx + 1}</td>
        <td class="px-3 py-3 font-semibold text-indigo-700 font-mono border-r border-slate-100">${i.id}</td>
        <td class="px-3 py-3 border-r border-slate-100">
          <span class="inline-block px-2.5 py-0.5 rounded-full font-bold uppercase ${
            i.status === 'Closed' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
            i.status === 'Escalated' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
            i.status === 'In Progress' ? 'bg-sky-100 text-sky-800 border border-sky-200' : 
            'bg-slate-100 text-slate-700 border border-slate-200'
          }">${i.status}</span>
        </td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-slate-500">${i.relatedRiskId || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-medium text-slate-800">${i.issueOwner}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.bundle || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-indigo-700 font-bold">${i.driverTreeRef || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-bold text-slate-900">${i.issueName}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.issueDescription}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.causeDescription}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.impactCategory || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.consequence || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-semibold text-slate-700">${i.trend}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-bold text-indigo-700">${i.priorityRating}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.escalateTo || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center">
          <span class="inline-block px-2.5 py-0.5 rounded text-[10px] font-bold uppercase ${
            i.severityRating === 'Critical' ? 'bg-red-600 text-white' :
            i.severityRating === 'High' ? 'bg-orange-100 text-orange-700' :
            i.severityRating === 'Medium' ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
          }">${i.severityRating}</span>
        </td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600 max-w-xs truncate">${i.actionPlan}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-medium text-slate-800">${i.nextActionOwner || i.issueOwner || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-slate-500">${i.dateRaised}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-slate-600">${i.raisedBy}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-slate-500">${i.dateClosed || 'N/A'}</td>
        <td class="px-3 py-3 border-r border-slate-100 font-mono text-slate-500">${i.lastUpdated}</td>
        <td class="px-3 py-3 border-r border-slate-100 text-center font-semibold text-slate-600">${i.protectedIssueRisk}</td>
        <td class="px-3 py-3 text-slate-600 font-mono">${i.dpeRefNumber || 'N/A'}</td>
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
              <p class="text-xs text-slate-500 mt-1">Live corporate audit of all 23 core operational columns.</p>
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
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue owner</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Bundle</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Driver Tree Ref</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue Name</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Issue Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Cause Description</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Impact Category</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Consequence</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Trend</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Priority Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Escalate to:</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 text-center">Severity Rating</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Action Plan ( What, When, Who)</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Next Action owner</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 font-mono">Date Raised</th>
                    <th class="px-3 py-3.5 border-r border-slate-200">Raised by</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 font-mono">Date Closed</th>
                    <th class="px-3 py-3.5 border-r border-slate-200 font-mono">Last Updated</th>
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

  // Reset filter variables
  const resetFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setPriorityFilter('all');
    setSeverityFilter('all');
    setDriverTreeRefFilter('all');
    setMinSeverity(1);
  };

  return (
    <div className="space-y-4">
      {/* Search & Actions Panel */}
      <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search issue ID, name, owner, description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 placeholder:text-slate-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={resetFilters}
            className="px-3.5 py-2 text-xs font-semibold text-slate-600 bg-slate-50 border border-slate-200 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            Clear Filters
          </button>




          {onImportClick && (
            <button
              onClick={onImportClick}
              className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 hover:text-indigo-600 rounded-lg transition-colors cursor-pointer shadow-xs"
              title="Import issues from spreadsheet copy-paste or CSV file"
            >
              <Database className="w-4 h-4 text-indigo-500" />
              Import Issues
            </button>
          )}
        </div>
      </div>

      {/* KPI Stats Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-100 p-4 rounded-xl shadow-xs flex items-center justify-between">
          <div>
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Total Issues</span>
            <span className="text-xl font-black text-slate-800">{issues.length}</span>
          </div>
          <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
            <AlertCircle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-slate-100 p-4 rounded-xl shadow-xs flex items-center justify-between">
          <div>
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Open Issues</span>
            <span className="text-xl font-black text-slate-800">
              {issues.filter(i => i.status === 'Open' || i.status === 'Active').length}
            </span>
          </div>
          <div className="p-2 bg-sky-50 rounded-lg text-sky-600">
            <Activity className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-slate-100 p-4 rounded-xl shadow-xs flex items-center justify-between">
          <div>
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Critical Severity</span>
            <span className="text-xl font-black text-red-600">
              {issues.filter(i => i.severityRating === 'Critical').length}
            </span>
          </div>
          <div className="p-2 bg-red-50 rounded-lg text-red-600">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white border border-slate-100 p-4 rounded-xl shadow-xs flex items-center justify-between">
          <div>
            <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Escalated Issues</span>
            <span className="text-xl font-black text-rose-600">
              {issues.filter(i => i.status === 'Escalated').length}
            </span>
          </div>
          <div className="p-2 bg-rose-50 rounded-lg text-rose-600">
            <TrendingUp className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Issue Register Diagnostics & Severity Profile Panel */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-3 border-b border-slate-100">
          <div>
            <h4 className="text-sm font-bold uppercase text-slate-700 tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-600" />
              Issue Register Diagnostics &amp; Severity Profile
            </h4>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Real-time feedback and high-fidelity severity breakdown synchronized from the active Issue Register.
            </p>
          </div>
          {/* Quick status badges */}
          <div className="flex gap-2">
            <span className="text-[11px] bg-red-50 text-red-700 border border-red-100 px-2.5 py-1 rounded-lg font-bold">
              Critical Severity: {issues.filter(i => i.severityRating === 'Critical' && i.status !== 'Closed').length}
            </span>
            <span className="text-[11px] bg-amber-50 text-amber-700 border border-amber-100 px-2.5 py-1 rounded-lg font-bold">
              Issue Eventuated: {issues.filter(i => i.status === 'Issue Eventuated').length}
            </span>
          </div>
        </div>

        {/* Quick numbers + Graph layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-1">
          {/* Numbers section */}
          <div className="lg:col-span-5 grid grid-cols-2 gap-3.5">
            <div className="bg-slate-50/70 border border-slate-100 rounded-xl p-3.5 hover:bg-slate-50 transition-colors">
              <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Open Issues</span>
              <span className="text-2xl font-black text-slate-800 tracking-tight font-mono">
                {issues.filter(i => i.status !== 'Closed').length}
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">Requiring resolution</span>
            </div>
            <div className="bg-amber-50/30 border border-amber-100 rounded-xl p-3.5 hover:bg-amber-50/50 transition-colors">
              <span className="text-[10px] text-amber-600 font-bold uppercase block">Issue Eventuated</span>
              <span className="text-2xl font-black text-amber-700 tracking-tight font-mono">
                {issues.filter(i => i.status === 'Issue Eventuated').length}
              </span>
              <span className="text-[10px] text-amber-500 block mt-1">Eventuated into issues</span>
            </div>
            <div className="bg-emerald-50/20 border border-emerald-100/50 rounded-xl p-3.5 hover:bg-emerald-50/45 transition-colors">
              <span className="text-[10px] text-emerald-500 font-bold uppercase block">Resolved (Closed)</span>
              <span className="text-2xl font-black text-emerald-600 tracking-tight font-mono">
                {issues.filter(i => i.status === 'Closed').length}
              </span>
              <span className="text-[10px] text-emerald-500 block mt-1">Properly closed out</span>
            </div>
            <div className="bg-slate-50/70 border border-slate-100 rounded-xl p-3.5 hover:bg-slate-50 transition-colors">
              <span className="text-[10px] text-slate-400 font-bold uppercase block">Total Registers</span>
              <span className="text-2xl font-black text-slate-800 tracking-tight font-mono">
                {issues.length}
              </span>
              <span className="text-[10px] text-slate-400 block mt-1">Cumulative registered</span>
            </div>
          </div>

          {/* Graph section */}
          <div className="lg:col-span-7 bg-slate-50/50 border border-slate-150 rounded-xl p-4 flex flex-col justify-between">
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase block mb-3.5">Issue Severity Profile</span>
              
              {/* Horizontal Bar Chart */}
              <div className="space-y-3">
                {(['Critical', 'High', 'Medium', 'Low'] as const).map(sev => {
                  const count = issues.filter(i => i.severityRating === sev).length;
                  const maxCount = Math.max(...['Critical', 'High', 'Medium', 'Low'].map(s => issues.filter(i => i.severityRating === s).length), 1);
                  const percentage = (count / maxCount) * 100;
                  
                  const barColors = {
                    Critical: 'bg-[#ea4335]',
                    High: 'bg-[#ff9900]',
                    Medium: 'bg-[#ffeb3b]',
                    Low: 'bg-[#34a853]'
                  };

                  const textColors = {
                    Critical: 'text-red-700 font-bold',
                    High: 'text-amber-700 font-bold',
                    Medium: 'text-yellow-800 font-semibold',
                    Low: 'text-emerald-700 font-bold'
                  };

                  return (
                    <div key={sev} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className={`${textColors[sev]} text-[11px] uppercase tracking-wider`}>{sev}</span>
                        <span className="font-mono font-bold text-slate-600">{count} issue{count !== 1 ? 's' : ''}</span>
                      </div>
                      <div className="h-2 w-full bg-slate-200/60 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${barColors[sev]} rounded-full transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="text-[10px] text-slate-400 mt-4 border-t border-slate-100/80 pt-2 flex justify-between">
              <span>Data dynamically linked with active Issue ledger records</span>
              <span className="font-semibold text-indigo-600">Active Monitoring</span>
            </div>
          </div>
        </div>
      </div>

      {/* Dropdown Filters Bar */}
      <div className="bg-white border border-slate-100 rounded-xl p-4 shadow-xs">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3.5">
          <Filter className="w-3.5 h-3.5 text-indigo-500" />
          Refine Ledger Records
        </div>

        {/* Min Severity Rating Slider (Separated & Placed Above Dropdowns) */}
        <div className="bg-slate-50/70 border border-slate-100 rounded-xl p-3.5 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex-1">
            <div className="flex justify-between items-center mb-1.5">
              <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                Filter by Minimum Severity Rating
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-md font-extrabold font-mono">
                  &ge; {['None', 'Low', 'Medium', 'High', 'Critical'][minSeverity]}
                </span>
                {minSeverity > 1 && (
                  <button
                    onClick={() => setMinSeverity(1)}
                    className="text-[10px] text-slate-400 hover:text-indigo-600 transition-colors font-semibold cursor-pointer"
                  >
                    Reset to Low
                  </button>
                )}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-slate-400 font-mono font-medium">Low</span>
              <input
                type="range"
                min="1"
                max="4"
                value={minSeverity}
                onChange={(e) => setMinSeverity(parseInt(e.target.value))}
                className="flex-1 h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600 focus:outline-hidden"
              />
              <span className="text-[10px] text-slate-400 font-mono font-medium">Critical</span>
            </div>
          </div>
        </div>

        {/* Dropdown filters grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {/* Status */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Issue Eventuated">Issue Eventuated</option>
              <option value="Closed">Closed</option>
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

          {/* Priority */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Priority Rating</label>
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

          {/* Severity */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 mb-1">Severity Rating</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full text-xs p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="all">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid Data Table */}
      <div className="bg-white border border-slate-100 rounded-xl shadow-xs overflow-hidden">
        <div 
          ref={issueTableContainerRef}
          onMouseDown={handleIssueMouseDown}
          onMouseMove={handleIssueMouseMove}
          onMouseUp={handleIssueMouseUpOrLeave}
          onMouseLeave={handleIssueMouseUpOrLeave}
          style={{ cursor: isIssueDragging ? 'grabbing' : 'grab' }}
          className="overflow-x-auto overflow-y-auto max-h-[650px] no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
        >
          <table className="w-full table-auto border-collapse text-left min-w-[1400px]">
            <thead className="sticky top-0 z-20 bg-slate-50 shadow-[0_1px_0_0_rgba(226,232,240,1)]">
              <tr className="bg-slate-50 text-slate-500 font-semibold text-xs border-b border-slate-100 select-none">
                <th className="w-12 px-4 py-3 text-center bg-slate-50 border-r border-slate-200">Row</th>
                <th onClick={() => handleSort('id')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">ID <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('status')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Status <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('relatedRiskId')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 font-mono text-[11px]">
                  <div className="flex items-center gap-1">Related Risk ID <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('issueOwner')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Issue owner <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('bundle')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Bundle <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('driverTreeRef')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Driver Tree Ref <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('issueName')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Issue Name <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('severityRating')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Severity Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('priorityRating')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Priority Rating <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('escalateTo')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Escalate to: <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('nextActionOwner')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200">
                  <div className="flex items-center gap-1">Next Action owner <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('dateRaised')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors border-r border-slate-200 font-mono text-[11px]">
                  <div className="flex items-center gap-1">Date Raised <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th onClick={() => handleSort('lastUpdated')} className="px-3 py-3 cursor-pointer hover:bg-slate-100 hover:text-slate-700 transition-colors font-mono text-[11px] border-r border-slate-200">
                  <div className="flex items-center gap-1">Last Updated <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700 text-xs">
              {filteredIssues.map((i, index) => {
                const isExpanded = !!expandedRows[i.id];
                return (
                  <React.Fragment key={`${i.id || 'iss'}-${index}`}>
                    <tr className={`hover:bg-slate-50/75 transition-colors cursor-pointer ${isExpanded ? 'bg-indigo-50/20' : ''}`}>
                      <td onClick={() => toggleRow(i.id)} className="px-4 py-3 text-center text-slate-400 font-mono border-r border-slate-100">
                        {index + 1}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-bold text-indigo-600 font-mono border-r border-slate-100">
                        {i.id}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 border-r border-slate-100">
                        <span className={`px-2.5 py-0.5 text-[10px] font-bold border rounded-full uppercase ${
                          i.status === 'Closed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                          i.status === 'Escalated' ? 'bg-rose-50 text-rose-700 border-rose-200 animate-pulse' :
                          i.status === 'In Progress' ? 'bg-sky-50 text-sky-700 border-sky-200' :
                          'bg-slate-50 text-slate-600 border-slate-200'
                        }`}>{i.status}</span>
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-mono text-slate-600 border-r border-slate-100">
                        {i.relatedRiskId || 'N/A'}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 text-slate-800 font-medium border-r border-slate-100">
                        {i.issueOwner}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 border-r border-slate-100">
                        <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-medium">{i.bundle || 'N/A'}</span>
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-mono text-indigo-700 font-bold border-r border-slate-100">
                        {i.driverTreeRef || 'N/A'}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-bold text-slate-800 border-r border-slate-100 max-w-xs truncate" title={i.issueName}>
                        {i.issueName}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 border-r border-slate-100 text-center">
                        <span className={`text-[10px] px-2 py-0.5 rounded font-extrabold uppercase ${
                          i.severityRating === 'Critical' ? 'bg-red-600 text-white' :
                          i.severityRating === 'High' ? 'bg-red-100 text-red-700' :
                          i.severityRating === 'Medium' ? 'bg-amber-100 text-amber-700' :
                          'bg-emerald-100 text-emerald-700'
                        }`}>{i.severityRating}</span>
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 border-r border-slate-100">
                        <span className={`px-2 py-0.5 text-[9px] font-semibold border rounded ${
                          i.priorityRating === 'Immediate' ? 'bg-red-50 text-red-700 border-red-200' :
                          i.priorityRating === 'Urgent' ? 'bg-orange-50 text-orange-700 border-orange-200' :
                          i.priorityRating === 'Prompt' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                          'bg-slate-50 text-slate-500 border-slate-200'
                        }`}>{i.priorityRating}</span>
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 text-slate-600 border-r border-slate-100 font-medium">
                        {i.escalateTo || 'No Escalation'}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 text-slate-800 font-medium border-r border-slate-100">
                        {i.nextActionOwner || i.issueOwner || 'N/A'}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">
                        {i.dateRaised}
                      </td>
                      <td onClick={() => toggleRow(i.id)} className="px-3 py-3 font-mono text-slate-500 border-r border-slate-100">
                        {i.lastUpdated}
                      </td>
                      <td className="px-3 py-3 text-center">
                        <div className="flex items-center justify-center gap-1.5">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditClick(i);
                            }}
                            className="px-2.5 py-1 rounded-lg text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-200 transition-all duration-150 cursor-pointer flex items-center gap-1 text-[11px] font-bold shadow-2xs"
                            title="Edit issue in form view"
                          >
                            <Edit2 className="w-3.5 h-3.5 text-amber-600" />
                            Edit
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleRow(i.id);
                            }}
                            className="px-2.5 py-1 rounded-lg text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 transition-all duration-150 cursor-pointer flex items-center gap-1 text-[11px] font-bold"
                            title="Toggle Detail View"
                          >
                            {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            {isExpanded ? 'Hide' : 'View'}
                          </button>
                        </div>
                      </td>
                    </tr>

                    {/* EXPANDED ROW FULL DETAIL DETAILS PANEL */}
                    {isExpanded && (
                      <tr>
                        <td colSpan={15} className="bg-indigo-50/10 px-6 py-4 border-b border-indigo-50/50">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fadeIn">
                            <div className="space-y-3">
                              <div>
                                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Issue Description</span>
                                <p className="text-slate-700 italic leading-relaxed bg-white border border-slate-100 p-2.5 rounded-lg text-xs shadow-xs">{i.issueDescription}</p>
                              </div>
                              <div>
                                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Cause Description</span>
                                <p className="text-slate-600 leading-relaxed bg-white border border-slate-100 p-2.5 rounded-lg text-xs shadow-xs">{i.causeDescription}</p>
                              </div>
                            </div>

                            <div className="space-y-3">
                              <div>
                                <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">Action Treatment Plan</span>
                                <p className="text-indigo-900 font-medium leading-relaxed bg-indigo-50/30 border border-indigo-100/50 p-2.5 rounded-lg text-xs shadow-xs">{i.actionPlan}</p>
                              </div>
                              <div className="grid grid-cols-2 gap-3">
                                <div>
                                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Impact Category</span>
                                  <span className="inline-block mt-0.5 font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{i.impactCategory || 'N/A'}</span>
                                </div>
                                <div>
                                  <span className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider">Consequence</span>
                                  <span className="inline-block mt-0.5 font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">{i.consequence || 'N/A'}</span>
                                </div>
                              </div>
                            </div>

                            <div className="space-y-3 text-xs">
                              <div className="bg-white border border-slate-100 rounded-lg p-3 shadow-xs space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Trend</span>
                                  <span className="font-semibold text-slate-700">{i.trend}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Who Raised</span>
                                  <span className="font-semibold text-slate-700">{i.raisedBy}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date Closed</span>
                                  <span className="font-semibold text-slate-700">{i.dateClosed || 'Still Open'}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Protected Issue</span>
                                  <span className="font-semibold text-slate-700">{i.protectedIssueRisk}</span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">DPE Ref Number</span>
                                  <span className="font-semibold text-indigo-700 font-mono">{i.dpeRefNumber || 'N/A'}</span>
                                </div>
                              </div>

                              <div className="pt-2 flex items-center justify-end gap-2">
                                <button
                                  onClick={() => handleEditClick(i)}
                                  className="px-3 py-1.5 rounded-lg text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors flex items-center gap-1.5 cursor-pointer shadow-xs"
                                >
                                  <Pencil className="w-3.5 h-3.5" />
                                  Edit Issue in Form
                                </button>
                                <button
                                  onClick={async () => {
                                    if (confirm(`Are you sure you want to delete issue ${i.id}?`)) {
                                      await onDeleteIssue(i.id);
                                    }
                                  }}
                                  className="px-3 py-1.5 rounded-lg text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 transition-colors flex items-center gap-1.5 cursor-pointer"
                                >
                                  <Trash2 className="w-3.5 h-3.5 text-rose-600" />
                                  Delete
                                </button>
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {filteredIssues.length === 0 && (
          <div className="py-12 text-center text-slate-400 font-medium text-xs select-none bg-slate-50/50">
            No issues found matching your current filter criteria.
          </div>
        )}

        <div className="bg-slate-50 border-t border-slate-100 px-4 py-3 text-[10px] font-bold text-slate-400 flex items-center justify-between uppercase tracking-wider">
          <div>
            Showing <strong>{filteredIssues.length}</strong> of <strong>{issues.length}</strong> registered issues
          </div>
          <div>
            * Click row row index or ID to expand and inspect full 21 columns
          </div>
        </div>
      </div>

      {/* SPREADSHEET LEDGER FULLSCREEN MODAL */}
      {showRegistryModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 md:p-6 animate-fadeIn">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full h-[90vh] flex flex-col overflow-hidden max-w-[96vw]">
            <div className="bg-slate-900 text-white px-6 py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800">
              <div>
                <h2 className="text-sm font-extrabold tracking-tight uppercase text-slate-100">
                  Operational Issue Registry — Master Spreadsheet View
                </h2>
                <p className="text-[10px] text-slate-400 mt-0.5">
                  Displaying all 21 operational compliance columns across {filteredIssues.length} active matching ledger records.
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  onClick={openPopOutWindow}
                  className="flex items-center gap-1.5 px-3.5 py-2 text-[11px] font-bold text-indigo-400 hover:text-indigo-300 bg-indigo-950/50 border border-indigo-900 hover:border-indigo-800 rounded-lg transition-colors cursor-pointer"
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

            <div className="flex-1 overflow-auto p-3 bg-slate-150/40">
              <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm h-full flex flex-col">
                <div className="overflow-auto flex-1 no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
                  <table className="w-full table-auto border-collapse text-left min-w-[3400px] text-xs">
                    <thead className="sticky top-0 z-10">
                      <tr className="bg-slate-100 text-slate-600 font-bold border-b border-slate-200 uppercase tracking-wider text-[10px]">
                        <th className="w-12 px-4 py-3 text-center border-r border-slate-200 bg-slate-100 sticky left-0 z-20">Row</th>
                        <th className="px-3 py-3 border-r border-slate-200 sticky left-12 bg-slate-100 z-20">ID</th>
                        <th className="px-3 py-3 border-r border-slate-200">Status</th>
                        <th className="px-3 py-3 border-r border-slate-200">Related Risk ID</th>
                        <th className="px-3 py-3 border-r border-slate-200">Issue owner</th>
                        <th className="px-3 py-3 border-r border-slate-200">Bundle</th>
                        <th className="px-3 py-3 border-r border-slate-200">Driver Tree Ref</th>
                        <th className="px-3 py-3 border-r border-slate-200">Issue Name</th>
                        <th className="px-3 py-3 border-r border-slate-200">Issue Description</th>
                        <th className="px-3 py-3 border-r border-slate-200">Cause Description</th>
                        <th className="px-3 py-3 border-r border-slate-200">Impact Category</th>
                        <th className="px-3 py-3 border-r border-slate-200">Consequence</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Trend</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Priority Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200">Escalate to:</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Severity Rating</th>
                        <th className="px-3 py-3 border-r border-slate-200">Action Plan ( What, When, Who)</th>
                        <th className="px-3 py-3 border-r border-slate-200">Next Action owner</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Date Raised</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Raised by</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Date Closed</th>
                        <th className="px-3 py-3 border-r border-slate-200 font-mono">Last Updated</th>
                        <th className="px-3 py-3 border-r border-slate-200 text-center">Protected Issue/Risk</th>
                        <th className="px-3 py-3 border-r border-slate-200">DPE Ref Number</th>
                        <th className="px-3 py-3 text-center sticky right-0 bg-slate-100 z-20 shadow-[-2px_0_4px_rgba(0,0,0,0.05)]">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-slate-700">
                      {filteredIssues.map((i, idx) => (
                        <tr key={`${i.id || 'iss'}-${idx}`} className="hover:bg-slate-50 transition-colors text-xs">
                          <td className="px-4 py-2.5 text-center text-slate-400 font-mono bg-slate-50 border-r border-slate-200 sticky left-0 z-10">{idx + 1}</td>
                          <td className="px-3 py-2.5 font-bold text-indigo-600 font-mono border-r border-slate-200 sticky left-12 bg-slate-50 z-10">{i.id}</td>
                          <td className="px-3 py-2.5 border-r border-slate-200">
                            <span className={`px-2 py-0.5 text-[9px] font-bold border rounded-full uppercase ${
                              i.status === 'Closed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                              i.status === 'Escalated' ? 'bg-rose-50 text-rose-700 border-rose-200' :
                              'bg-slate-50 text-slate-600 border-slate-200'
                            }`}>{i.status}</span>
                          </td>
                          <td className="px-3 py-2.5 font-mono text-slate-600 border-r border-slate-200">{i.relatedRiskId || 'N/A'}</td>
                          <td className="px-3 py-2.5 text-slate-700 border-r border-slate-200 font-semibold">{i.issueOwner}</td>
                          <td className="px-3 py-2.5 border-r border-slate-200">
                            <span className="text-[10px] bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded font-medium">{i.bundle || 'N/A'}</span>
                          </td>
                          <td className="px-3 py-2.5 font-mono text-indigo-700 font-bold border-r border-slate-200">{i.driverTreeRef || 'N/A'}</td>
                          <td className="px-3 py-2.5 font-bold text-slate-800 border-r border-slate-200">{i.issueName}</td>
                          <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200 italic max-w-sm truncate" title={i.issueDescription}>{i.issueDescription}</td>
                          <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-xs truncate" title={i.causeDescription}>{i.causeDescription}</td>
                          <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200">{i.impactCategory || 'N/A'}</td>
                          <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200">{i.consequence || 'N/A'}</td>
                          <td className="px-3 py-2.5 border-r border-slate-200 text-center">{i.trend}</td>
                          <td className="px-3 py-2.5 border-r border-slate-200 text-center font-bold text-indigo-700">{i.priorityRating}</td>
                          <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200">{i.escalateTo || 'N/A'}</td>
                          <td className="px-3 py-2.5 text-center border-r border-slate-200">
                            <span className="text-[9px] px-2 py-0.5 rounded font-extrabold uppercase bg-amber-100 text-amber-800">{i.severityRating}</span>
                          </td>
                          <td className="px-3 py-2.5 text-slate-500 border-r border-slate-200 max-w-xs truncate" title={i.actionPlan}>{i.actionPlan}</td>
                          <td className="px-3 py-2.5 text-slate-700 border-r border-slate-200 font-medium">{i.nextActionOwner || i.issueOwner || 'N/A'}</td>
                          <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{i.dateRaised}</td>
                          <td className="px-3 py-2.5 text-slate-600 border-r border-slate-200">{i.raisedBy}</td>
                          <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{i.dateClosed || 'N/A'}</td>
                          <td className="px-3 py-2.5 font-mono text-slate-500 border-r border-slate-200">{i.lastUpdated}</td>
                          <td className="px-3 py-2.5 border-r border-slate-200 text-center">{i.protectedIssueRisk}</td>
                          <td className="px-3 py-2.5 text-slate-600 font-mono border-r border-slate-200">{i.dpeRefNumber || 'N/A'}</td>
                          <td className="px-3 py-2.5 text-center sticky right-0 bg-slate-50 z-10 border-l border-slate-200 shadow-[-2px_0_4px_rgba(0,0,0,0.05)]">
                            <button
                              onClick={() => {
                                setShowRegistryModal(false);
                                handleEditClick(i);
                              }}
                              className="px-2.5 py-1 text-[11px] font-bold text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded cursor-pointer transition-colors flex items-center gap-1 mx-auto"
                              title="Edit issue in form view"
                            >
                              <Edit2 className="w-3 h-3 text-amber-600" />
                              Edit
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ISSUE ADD/EDIT MODAL OVERLAY */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden my-8">
            <div className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between border-b border-slate-800">
              <div>
                <h2 className="text-sm font-extrabold tracking-tight uppercase text-slate-100 flex items-center gap-2">
                  {editingIssue ? `Edit Operational Issue - ${form.id}` : 'Raise New Operational Issue'}
                </h2>
                <p className="text-[10px] text-slate-400 mt-0.5">
                  Complete all 21 core ledger attributes to maintain issue compliance.
                </p>
              </div>
              <button 
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white transition-colors cursor-pointer text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4 text-xs">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Issue ID *</label>
                  <input
                    type="text"
                    required
                    disabled={!!editingIssue}
                    value={form.id || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, id: e.target.value }))}
                    className="w-full p-2 bg-slate-100 border border-slate-200 rounded-lg text-slate-700 font-mono disabled:opacity-75 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Status *</label>
                  <select
                    required
                    value={form.status || 'Open'}
                    onChange={(e) => setForm(prev => ({ ...prev, status: e.target.value as any }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
                  >
                    <option value="Open">Open</option>
                    <option value="Issue Eventuated">Issue Eventuated</option>
                    <option value="Closed">Closed</option>
                    <option value="N/A">N/A</option>
                    <option value="No Data">No Data</option>
                    <option value="-">-</option>
                    <option value=" "> (Blank)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Related Risk ID</label>
                  <input
                    type="text"
                    value={form.relatedRiskId || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, relatedRiskId: e.target.value }))}
                    placeholder="e.g. RSK-001"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-mono focus:outline-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Issue Name *</label>
                  <input
                    type="text"
                    required
                    value={form.issueName || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, issueName: e.target.value }))}
                    placeholder="Enter short, descriptive name"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Bundle / Workstream</label>
                  <input
                    type="text"
                    value={form.bundle || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, bundle: e.target.value }))}
                    placeholder="e.g. Technology"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Driver Tree Ref</label>
                  <input
                    type="text"
                    value={form.driverTreeRef || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, driverTreeRef: e.target.value }))}
                    placeholder="e.g. DTR-1.1"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 font-mono focus:outline-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Issue Description *</label>
                  <textarea
                    required
                    rows={3}
                    value={form.issueDescription || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, issueDescription: e.target.value }))}
                    placeholder="Describe issue details..."
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Cause Description *</label>
                  <textarea
                    required
                    rows={3}
                    value={form.causeDescription || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, causeDescription: e.target.value }))}
                    placeholder="Describe the root cause..."
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Issue Owner *</label>
                  <input
                    type="text"
                    required
                    value={form.issueOwner || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, issueOwner: e.target.value }))}
                    placeholder="Responsible owner"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Impact Category</label>
                  <input
                    type="text"
                    value={form.impactCategory || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, impactCategory: e.target.value }))}
                    placeholder="e.g. Operational"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Consequence</label>
                  <input
                    type="text"
                    value={form.consequence || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, consequence: e.target.value }))}
                    placeholder="Business consequence"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Trend *</label>
                  <select
                    required
                    value={form.trend || 'Stable'}
                    onChange={(e) => setForm(prev => ({ ...prev, trend: e.target.value as any }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
                  >
                    <option value="Increasing">Increasing</option>
                    <option value="Stable">Stable</option>
                    <option value="Decreasing">Decreasing</option>
                    <option value="N/A">N/A</option>
                    <option value="No Data">No Data</option>
                    <option value="-">-</option>
                    <option value=" "> (Blank)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Priority Rating *</label>
                  <select
                    required
                    value={form.priorityRating || 'Prompt'}
                    onChange={(e) => setForm(prev => ({ ...prev, priorityRating: e.target.value as any }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
                  >
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

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Severity Rating *</label>
                  <select
                    required
                    value={form.severityRating || 'Medium'}
                    onChange={(e) => setForm(prev => ({ ...prev, severityRating: e.target.value as any }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
                  >
                    <option value="Critical">Critical</option>
                    <option value="High">High</option>
                    <option value="Medium">Medium</option>
                    <option value="Low">Low</option>
                    <option value="N/A">N/A</option>
                    <option value="No Data">No Data</option>
                    <option value="-">-</option>
                    <option value=" "> (Blank)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Escalate To</label>
                  <input
                    type="text"
                    value={form.escalateTo || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, escalateTo: e.target.value }))}
                    placeholder="e.g. CTO, ExCo"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Protected Issue / Risk *</label>
                  <select
                    required
                    value={form.protectedIssueRisk || 'No'}
                    onChange={(e) => setForm(prev => ({ ...prev, protectedIssueRisk: e.target.value as any }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
                  >
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                    <option value="N/A">N/A</option>
                    <option value="No Data">No Data</option>
                    <option value="-">-</option>
                    <option value=" "> (Blank)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Action Plan ( What, When, Who) *</label>
                  <textarea
                    required
                    rows={2}
                    value={form.actionPlan || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, actionPlan: e.target.value }))}
                    placeholder="Outline immediate step-by-step mitigation plan..."
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Next Action owner</label>
                  <input
                    type="text"
                    value={form.nextActionOwner || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, nextActionOwner: e.target.value }))}
                    placeholder="Next action owner name"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Date Raised *</label>
                  <input
                    type="date"
                    required
                    value={form.dateRaised || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, dateRaised: e.target.value }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Raised By *</label>
                  <input
                    type="text"
                    required
                    value={form.raisedBy || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, raisedBy: e.target.value }))}
                    placeholder="Person raising issue"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">Date Closed</label>
                  <input
                    type="date"
                    value={form.dateClosed || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, dateClosed: e.target.value }))}
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-slate-500 mb-1">DPE Ref Number</label>
                  <input
                    type="text"
                    value={form.dpeRefNumber || ''}
                    onChange={(e) => setForm(prev => ({ ...prev, dpeRefNumber: e.target.value }))}
                    placeholder="e.g. DPE-904"
                    className="w-full p-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
                  />
                </div>
              </div>

              <div className="pt-4 flex items-center justify-end gap-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl transition-colors cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded-xl transition-colors cursor-pointer shadow-sm"
                >
                  {editingIssue ? 'Save Operational Changes' : 'Publish New Issue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
