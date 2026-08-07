/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useRef, useEffect } from 'react';
import { RiskTicket, calculateRiskLevel, RISK_LEVEL_COLORS, getMatrixScore } from '../types';
import { parseFlexibleDate, formatDateShort } from '../utils/dateUtils';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, LineChart, Line, ComposedChart, Cell
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Minus, ShieldAlert, CheckCircle, 
  Layers, AlertOctagon, HelpCircle, ArrowUpRight, Flame, Calendar,
  ChevronDown, Check, Filter, X
} from 'lucide-react';

interface TrendsTabProps {
  tickets: RiskTicket[];
}

interface PeriodMetric {
  label: string;
  startDate: string;
  endDate: string;
  activeCount: number;
  newRaised: number;
  newClosed: number;
  avgInherentScore: number;
  avgResidualScore: number;
  riskReduction: number; // Inherent - Residual
  isCurrent: boolean;
}

// Helper component for highlighting current date/week dot on Line charts
const renderHighlightDot = (strokeColor: string) => {
  return (props: any) => {
    const { cx, cy, payload } = props;
    if (cx === undefined || cy === undefined) return null;

    if (payload?.isCurrent) {
      return (
        <g key={`current-dot-${cx}-${cy}`}>
          <circle cx={cx} cy={cy} r={10} fill={strokeColor} fillOpacity={0.25} />
          <circle cx={cx} cy={cy} r={6} fill="#ffffff" stroke={strokeColor} strokeWidth={2.5} />
          <circle cx={cx} cy={cy} r={2.5} fill={strokeColor} />
        </g>
      );
    }
    return <circle key={`dot-${cx}-${cy}`} cx={cx} cy={cy} r={3} fill={strokeColor} />;
  };
};

const renderCustomXAxisTick = (props: any) => {
  const { x, y, payload } = props;
  const rawText: string = payload?.value || '';
  const isCurrent = rawText.includes('(Current)');
  const cleanText = rawText.replace(' (Current)', '');

  return (
    <g transform={`translate(${x},${y})`}>
      <text 
        x={0} 
        y={0} 
        dy={12} 
        textAnchor="middle" 
        fill={isCurrent ? "#4f46e5" : "#94a3b8"} 
        fontSize={10} 
        fontWeight={isCurrent ? "700" : "400"}
      >
        {cleanText}
      </text>
      {isCurrent && (
        <circle cx={0} cy={20} r={3} fill="#4f46e5" />
      )}
    </g>
  );
};

export default function TrendsTab({ tickets }: TrendsTabProps) {
  const [granularity, setGranularity] = useState<'monthly' | 'biweekly' | 'weekly'>('monthly');

  // Calculate dynamic time period metrics up to the current date (today)
  const periods = useMemo<PeriodMetric[]>(() => {
    const validDates: number[] = [];
    tickets.forEach(t => {
      const dRaised = parseFlexibleDate(t.dateRaised);
      if (dRaised) validDates.push(dRaised.getTime());
      const dClosed = parseFlexibleDate(t.dateClosed);
      if (dClosed) validDates.push(dClosed.getTime());
      const dUpdated = parseFlexibleDate(t.riskLastUpdated);
      if (dUpdated) validDates.push(dUpdated.getTime());
    });

    let minDate: Date;

    if (validDates.length > 0) {
      minDate = new Date(Math.min(...validDates));
    } else {
      minDate = new Date(2025, 10, 1); // Nov 1, 2025 fallback
    }

    const today = new Date();
    const todayEnd = new Date(today);
    todayEnd.setHours(23, 59, 59, 999);

    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const ranges: { label: string; start: Date; end: Date; isCurrent: boolean }[] = [];

    if (granularity === 'monthly') {
      let curr = new Date(minDate.getFullYear(), minDate.getMonth(), 1, 0, 0, 0, 0);
      const todayMonthEnd = new Date(today.getFullYear(), today.getMonth() + 1, 0, 23, 59, 59, 999);

      while (curr.getTime() <= todayMonthEnd.getTime()) {
        const start = new Date(curr);
        const end = new Date(curr.getFullYear(), curr.getMonth() + 1, 0, 23, 59, 59, 999);
        const isCurrent = (todayEnd.getTime() >= start.getTime() && todayEnd.getTime() <= end.getTime());
        const label = `${monthNames[curr.getMonth()]} ${curr.getFullYear()}${isCurrent ? ' (Current)' : ''}`;

        ranges.push({ label, start, end, isCurrent });
        curr = new Date(curr.getFullYear(), curr.getMonth() + 1, 1, 0, 0, 0, 0);
      }
    } else if (granularity === 'biweekly') {
      let curr = new Date(minDate);
      curr.setHours(0, 0, 0, 0);
      const day = curr.getDay();
      const diffToMon = curr.getDate() - day + (day === 0 ? -6 : 1);
      curr.setDate(diffToMon);

      while (curr.getTime() <= todayEnd.getTime()) {
        const start = new Date(curr);
        const end = new Date(curr.getTime() + 13 * 24 * 60 * 60 * 1000);
        end.setHours(23, 59, 59, 999);

        const isCurrent = (todayEnd.getTime() >= start.getTime() && todayEnd.getTime() <= end.getTime());
        const startStr = `${start.getDate()} ${monthNames[start.getMonth()]}`;
        const endStr = `${end.getDate()} ${monthNames[end.getMonth()]}`;
        const label = `${startStr} - ${endStr}${isCurrent ? ' (Current)' : ''}`;

        ranges.push({ label, start, end, isCurrent });
        curr = new Date(curr.getTime() + 14 * 24 * 60 * 60 * 1000);
      }
    } else {
      // Weekly
      let curr = new Date(minDate);
      curr.setHours(0, 0, 0, 0);
      const day = curr.getDay();
      const diffToMon = curr.getDate() - day + (day === 0 ? -6 : 1);
      curr.setDate(diffToMon);

      while (curr.getTime() <= todayEnd.getTime()) {
        const start = new Date(curr);
        const end = new Date(curr.getTime() + 6 * 24 * 60 * 60 * 1000);
        end.setHours(23, 59, 59, 999);

        const isCurrent = (todayEnd.getTime() >= start.getTime() && todayEnd.getTime() <= end.getTime());
        const startStr = `${start.getDate()} ${monthNames[start.getMonth()]}`;
        const endStr = `${end.getDate()} ${monthNames[end.getMonth()]}`;
        const label = `${startStr} - ${endStr}${isCurrent ? ' (Current)' : ''}`;

        ranges.push({ label, start, end, isCurrent });
        curr = new Date(curr.getTime() + 7 * 24 * 60 * 60 * 1000);
      }
    }

    return ranges.map(range => {
      // Find active tickets in this period
      const activeInPeriod = tickets.filter(t => {
        const dRaised = parseFlexibleDate(t.dateRaised);
        if (!dRaised) return false;

        const raisedOnOrBefore = dRaised.getTime() <= range.end.getTime();
        const dClosed = parseFlexibleDate(t.dateClosed);
        const notClosedOrClosedLater = !dClosed || dClosed.getTime() > range.end.getTime();

        return raisedOnOrBefore && notClosedOrClosedLater;
      });

      // Find tickets newly raised in this period
      const newRaised = tickets.filter(t => {
        const dRaised = parseFlexibleDate(t.dateRaised);
        if (!dRaised) return false;
        return dRaised.getTime() >= range.start.getTime() && dRaised.getTime() <= range.end.getTime();
      }).length;

      // Find tickets newly closed in this period
      const newClosed = tickets.filter(t => {
        const dClosed = parseFlexibleDate(t.dateClosed);
        if (!dClosed) return false;
        return dClosed.getTime() >= range.start.getTime() && dClosed.getTime() <= range.end.getTime();
      }).length;

      // Calculate averages safely
      const totalInherent = activeInPeriod.reduce((sum, t) => sum + (t.inherentRiskScore || 0), 0);
      const totalResidual = activeInPeriod.reduce((sum, t) => sum + (t.residualRiskScore || 0), 0);
      const count = activeInPeriod.length;

      const avgInherentScore = count > 0 ? parseFloat((totalInherent / count).toFixed(1)) : 0;
      const avgResidualScore = count > 0 ? parseFloat((totalResidual / count).toFixed(1)) : 0;
      const riskReduction = count > 0 ? parseFloat((avgInherentScore - avgResidualScore).toFixed(1)) : 0;

      return {
        label: range.label,
        startDate: range.start.toISOString().split('T')[0],
        endDate: range.end.toISOString().split('T')[0],
        activeCount: count,
        newRaised,
        newClosed,
        avgInherentScore,
        avgResidualScore,
        riskReduction,
        isCurrent: range.isCurrent,
      };
    });
  }, [tickets, granularity]);

  // Severity profile toggle states
  const [severityMatrixType, setSeverityMatrixType] = useState<'inherent' | 'residual'>('inherent');
  const [severityScope, setSeverityScope] = useState<'open' | 'active' | 'all'>('open');
  const [categoryScope, setCategoryScope] = useState<'open' | 'active' | 'all'>('open');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['Scope', 'Cost', 'Schedule']);
  const [isCategoryDropdownOpen, setIsCategoryDropdownOpen] = useState(false);
  const [categorySearchQuery, setCategorySearchQuery] = useState('');
  const categoryDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (categoryDropdownRef.current && !categoryDropdownRef.current.contains(event.target as Node)) {
        setIsCategoryDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Current active tickets summary statistics aligned with 5x5 Matrix ratings
  const summary = useMemo(() => {
    const openTickets = tickets.filter(t => t.status !== 'Closed');
    const activeTickets = tickets.filter(t => t.status === 'Active');
    const closedTickets = tickets.filter(t => t.status === 'Closed');
    
    // Choose dataset based on selected severity scope for the severity breakdown card
    const severityTargetTickets = severityScope === 'open' 
      ? openTickets 
      : severityScope === 'active' 
        ? activeTickets 
        : tickets;

    let veryHighCount = 0;
    let highCount = 0;
    let mediumCount = 0;
    let lowCount = 0;
    let veryLowCount = 0;
    let unratedCount = 0;

    severityTargetTickets.forEach(t => {
      const l = severityMatrixType === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
      const c = severityMatrixType === 'inherent' ? t.inherentConsequence : t.residualConsequence;
      const rawScore = severityMatrixType === 'inherent' ? t.inherentRiskScore : t.residualRiskScore;

      const score = (l !== null && c !== null) ? getMatrixScore(l, c) : rawScore;
      const level = calculateRiskLevel(score);

      if (level === 'Very High' || level === 'Critical') veryHighCount++;
      else if (level === 'High') highCount++;
      else if (level === 'Medium') mediumCount++;
      else if (level === 'Low') lowCount++;
      else if (level === 'Very Low') veryLowCount++;
      else unratedCount++;
    });

    // Overall active metrics
    const totalActiveInherentScore = activeTickets.reduce((sum, t) => sum + (t.inherentRiskScore || 0), 0);
    const totalActiveResidualScore = activeTickets.reduce((sum, t) => sum + (t.residualRiskScore || 0), 0);
    const count = activeTickets.length;

    const avgInherent = count > 0 ? (totalActiveInherentScore / count).toFixed(1) : '0';
    const avgResidual = count > 0 ? (totalActiveResidualScore / count).toFixed(1) : '0';
    
    // SLA Compliance: Overdue count using parseFlexibleDate against today's date
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const overdueCount = activeTickets.filter(t => {
      const dTarget = parseFlexibleDate(t.targetDate);
      return dTarget !== null && dTarget < today;
    }).length;

    // Period delta
    const currentPeriod = periods[periods.length - 1];
    const prevPeriod = periods[periods.length - 2];
    const backlogChange = (currentPeriod?.activeCount || 0) - (prevPeriod?.activeCount || 0);

    const highPriorityCount = veryHighCount + highCount;

    return {
      activeCount: count,
      openCount: openTickets.length,
      closedCount: closedTickets.length,
      severityTotalCount: severityTargetTickets.length,
      highPriorityCount,
      overdueCount,
      avgInherent,
      avgResidual,
      veryHighCount,
      highCount,
      mediumCount,
      lowCount,
      veryLowCount,
      unratedCount,
      backlogChange,
    };
  }, [tickets, periods, severityMatrixType, severityScope]);

  // Available Cause Categories for dropdown filter
  const availableCategories = useMemo(() => {
    const set = new Set<string>();
    tickets.forEach(t => {
      const c = (t.causeCategory || '').trim() || 'Unknown';
      set.add(c);
    });

    const standardCategories = [
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
    standardCategories.forEach(c => set.add(c));

    const bottomValues = ['na', 'n/a', 'unknown', 'no data', '-', ' '];
    return Array.from(set).sort((a, b) => {
      const aIsBottom = bottomValues.includes(a.toLowerCase());
      const bIsBottom = bottomValues.includes(b.toLowerCase());
      if (aIsBottom && !bIsBottom) return 1;
      if (!aIsBottom && bIsBottom) return -1;
      return a.localeCompare(b);
    });
  }, [tickets]);

  const toggleCategorySelection = (category: string) => {
    setSelectedCategories(prev => {
      if (prev.includes(category)) {
        return prev.filter(c => c !== category);
      } else {
        return [...prev, category];
      }
    });
  };

  const categoryData = useMemo(() => {
    const filtered = tickets.filter(t => {
      if (categoryScope === 'open') return t.status !== 'Closed';
      if (categoryScope === 'active') return t.status === 'Active';
      return true; // 'all'
    });

    const counts: Record<string, number> = {};
    filtered.forEach(t => {
      const rawCat = (t.causeCategory || '').trim();
      const cat = rawCat || 'Unknown';
      counts[cat] = (counts[cat] || 0) + 1;
    });

    const palette = [
      '#4f46e5', // Indigo
      '#f59e0b', // Amber
      '#0d9488', // Teal
      '#e11d48', // Rose
      '#8b5cf6', // Purple
      '#06b6d4', // Cyan
      '#10b981', // Emerald
      '#f97316', // Orange
      '#6366f1', // Indigo Light
      '#ec4899', // Pink
    ];

    const isNeutralCategory = (catName: string) => {
      const norm = catName.trim().toLowerCase();
      return norm === 'n/a' || norm === 'na' || norm === 'unknown' || norm === 'no data' || norm === '-' || norm === '(blank)' || norm === '';
    };

    let paletteIndex = 0;
    const allItems = Object.entries(counts)
      .map(([name, count]) => {
        const displayName = name === ' ' ? '(Blank)' : name;
        const color = isNeutralCategory(displayName)
          ? '#94a3b8' // Slate / light charcoal grey for N/A
          : palette[paletteIndex++ % palette.length];

        return {
          name: displayName,
          count,
          color,
          percentage: filtered.length > 0 ? Math.round((count / filtered.length) * 100) : 0,
        };
      })
      .sort((a, b) => b.count - a.count);

    if (selectedCategories.length === 0) {
      return allItems;
    }

    // Return only the selected categories with their respective counts
    let selectedPaletteIndex = 0;
    return selectedCategories.map((cat) => {
      const targetName = cat === ' ' ? '(Blank)' : cat;
      const matchingItem = allItems.find(item => item.name === targetName || item.name === cat);
      const count = matchingItem ? matchingItem.count : (counts[cat] || counts[' '] || 0);
      const color = isNeutralCategory(targetName)
        ? '#94a3b8'
        : palette[selectedPaletteIndex++ % palette.length];

      return {
        name: targetName,
        count,
        color,
        percentage: filtered.length > 0 ? Math.round((count / filtered.length) * 100) : 0,
      };
    }).sort((a, b) => b.count - a.count);
  }, [tickets, categoryScope, selectedCategories]);

  return (
    <div id="trends-dashboard" className="space-y-6">
      
      {/* Granularity Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 bg-white border border-slate-100 rounded-xl p-4 shadow-2xs">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-600" />
              Risk Timeline & Trend Analytics
            </h2>
            {periods.find(p => p.isCurrent) && (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-600"></span>
                </span>
                Today: {periods.find(p => p.isCurrent)?.label.replace(' (Current)', '')}
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Current week is highlighted with a glowing indicator
          </p>
        </div>
        <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-lg text-xs font-medium self-start sm:self-auto">
          <span className="text-[11px] text-slate-500 font-semibold px-2">Granularity:</span>
          <button
            type="button"
            onClick={() => setGranularity('monthly')}
            className={`px-3 py-1.5 rounded-md transition-all text-xs font-semibold ${granularity === 'monthly' ? 'bg-white text-indigo-700 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Monthly
          </button>
          <button
            type="button"
            onClick={() => setGranularity('biweekly')}
            className={`px-3 py-1.5 rounded-md transition-all text-xs font-semibold ${granularity === 'biweekly' ? 'bg-white text-indigo-700 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Bi-Weekly
          </button>
          <button
            type="button"
            onClick={() => setGranularity('weekly')}
            className={`px-3 py-1.5 rounded-md transition-all text-xs font-semibold ${granularity === 'weekly' ? 'bg-white text-indigo-700 shadow-xs font-bold' : 'text-slate-600 hover:text-slate-900'}`}
          >
            Weekly
          </button>
        </div>
      </div>

      {/* Main Trends Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* CHART 1: Active Backlog, Intake & Closure Rates */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-slate-800">Risk Volume & Intake vs. Closures</h3>
            <p className="text-[11px] text-slate-400">
              Active backlog bar and line compared to newly opened and closed tickets per period.
            </p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={periods} margin={{ top: 10, right: 10, left: -25, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="label" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} tick={renderCustomXAxisTick} height={36} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '11px' }}
                />
                <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                
                {/* Active Risk Bars */}
                <Bar name="Active Risks" dataKey="activeCount" radius={[4, 4, 0, 0]} barSize={14}>
                  {periods.map((entry, index) => (
                    <Cell 
                      key={`cell-active-${index}`} 
                      fill={entry.isCurrent ? '#4338ca' : '#6366f1'} 
                      stroke={entry.isCurrent ? '#312e81' : undefined}
                      strokeWidth={entry.isCurrent ? 1.5 : 0}
                    />
                  ))}
                </Bar>
                
                {/* Intake and Closures Bars */}
                <Bar name="New Risks Opened" dataKey="newRaised" fill="#f87171" radius={[4, 4, 0, 0]} barSize={14} />
                <Bar name="Risks Closed" dataKey="newClosed" fill="#34d399" radius={[4, 4, 0, 0]} barSize={14} />

                {/* Active Risk Trend Line */}
                <Line type="monotone" name="Active Risk Trend" dataKey="activeCount" stroke="#312e81" strokeWidth={2.5} dot={renderHighlightDot('#312e81')} />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* CHART 2: Mitigation Burndown (Inherent vs Residual) */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-xs flex flex-col">
          <div className="mb-4">
            <h3 className="text-sm font-bold text-slate-800">Risk Mitigation Score Performance</h3>
            <p className="text-[11px] text-slate-400">
              Tracks the gap between Average Inherent Score (Pre-control) and Average Residual Score (Post-control).
            </p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={periods} margin={{ top: 10, right: 10, left: -25, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="label" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} tick={renderCustomXAxisTick} height={36} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} domain={[0, 25]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '11px' }}
                />
                <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                
                <Line type="monotone" name="Inherent Avg Risk (Pre-Control)" dataKey="avgInherentScore" stroke="#ef4444" strokeWidth={2.5} dot={renderHighlightDot('#ef4444')} />
                <Line type="monotone" name="Residual Avg Risk (Post-Control)" dataKey="avgResidualScore" stroke="#10b981" strokeWidth={2.5} dot={renderHighlightDot('#10b981')} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Cause Category and Severity Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        
        {/* Left Side: Cause Category Distribution */}
        <div className="md:col-span-7 bg-white border border-slate-100 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Risk Cause Category Concentration</h3>
                <p className="text-[11px] text-slate-400">
                  Showing volume breakdown directly from Cause Category field.
                </p>
              </div>

              {/* Category Dropdown & Scope Toggles */}
              <div className="flex flex-wrap items-center gap-2 self-start sm:self-auto">
                {/* Multi-Select Category Dropdown */}
                <div className="relative" ref={categoryDropdownRef}>
                  <button
                    type="button"
                    onClick={() => setIsCategoryDropdownOpen(!isCategoryDropdownOpen)}
                    className="flex items-center gap-1.5 text-[11px] font-medium p-1.5 px-2.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-md text-slate-700 focus:outline-indigo-500 cursor-pointer shadow-2xs max-w-[210px]"
                    title="Filter Cause Categories"
                  >
                    <Filter className="w-3 h-3 text-slate-400 shrink-0" />
                    <span className="truncate">
                      {selectedCategories.length === 0
                        ? 'All Cause Categories'
                        : selectedCategories.length === 1
                        ? (selectedCategories[0] === ' ' ? '(Blank)' : selectedCategories[0])
                        : `${selectedCategories.length} Categories Selected`}
                    </span>
                    <ChevronDown className="w-3 h-3 text-slate-400 shrink-0 ml-auto" />
                  </button>

                  {isCategoryDropdownOpen && (
                    <div className="absolute right-0 top-full mt-1 w-64 bg-white border border-slate-200 rounded-lg shadow-xl p-2 z-40 max-h-80 flex flex-col">
                      <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-100 px-1">
                        <span className="text-[11px] font-bold text-slate-700">Filter Categories</span>
                        <div className="flex items-center gap-2">
                          {selectedCategories.length > 0 && (
                            <button
                              type="button"
                              onClick={() => setSelectedCategories([])}
                              className="text-[10px] font-semibold text-indigo-600 hover:text-indigo-800 cursor-pointer"
                            >
                              Reset All
                            </button>
                          )}
                          <button
                            type="button"
                            onClick={() => setIsCategoryDropdownOpen(false)}
                            className="text-slate-400 hover:text-slate-600 p-0.5 rounded cursor-pointer"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      <input
                        type="text"
                        placeholder="Search categories..."
                        value={categorySearchQuery}
                        onChange={(e) => setCategorySearchQuery(e.target.value)}
                        className="w-full text-[11px] p-1.5 px-2 bg-slate-50 border border-slate-200 rounded mb-1.5 text-slate-700 focus:outline-indigo-500"
                      />

                      <div className="overflow-y-auto flex-1 space-y-0.5 pr-0.5">
                        <label
                          className="flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-50 text-[11px] cursor-pointer font-medium text-slate-800"
                        >
                          <input
                            type="checkbox"
                            checked={selectedCategories.length === 0}
                            onChange={() => setSelectedCategories([])}
                            className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 cursor-pointer"
                          />
                          <span>All Categories</span>
                        </label>

                        {availableCategories
                          .filter(cat => {
                            if (!categorySearchQuery) return true;
                            const displayName = cat === ' ' ? '(Blank)' : cat;
                            return displayName.toLowerCase().includes(categorySearchQuery.toLowerCase());
                          })
                          .map(cat => {
                            const displayName = cat === ' ' ? '(Blank)' : cat;
                            const isChecked = selectedCategories.includes(cat);
                            return (
                              <label
                                key={cat}
                                className="flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-50 text-[11px] cursor-pointer text-slate-700"
                              >
                                <input
                                  type="checkbox"
                                  checked={isChecked}
                                  onChange={() => toggleCategorySelection(cat)}
                                  className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5 cursor-pointer"
                                />
                                <span className="truncate">{displayName}</span>
                              </label>
                            );
                          })}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex bg-slate-100 p-0.5 rounded-md text-[10px] font-medium">
                  <button
                    type="button"
                    onClick={() => setCategoryScope('open')}
                    className={`px-2.5 py-0.5 rounded transition-all ${categoryScope === 'open' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="Open Risks (Active + Eventuated)"
                  >
                    Open
                  </button>
                  <button
                    type="button"
                    onClick={() => setCategoryScope('active')}
                    className={`px-2.5 py-0.5 rounded transition-all ${categoryScope === 'active' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="Active Risks Only"
                  >
                    Active
                  </button>
                  <button
                    type="button"
                    onClick={() => setCategoryScope('all')}
                    className={`px-2.5 py-0.5 rounded transition-all ${categoryScope === 'all' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="All Risks"
                  >
                    All
                  </button>
                </div>
              </div>
            </div>

            <div className="h-64 w-full mt-2">
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                    <XAxis type="number" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis dataKey="name" type="category" stroke="#334155" fontSize={11} fontWeight={600} tickLine={false} axisLine={false} width={120} />
                    <Tooltip 
                      formatter={(value: any, name: any, props: any) => [`${value} risks (${props.payload.percentage}%)`, 'Count']}
                      contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '11px' }}
                    />
                    <Bar dataKey="count" radius={[0, 6, 6, 0]} barSize={16}>
                      {categoryData.map((entry) => (
                        <Cell key={`cell-${entry.name}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-full flex items-center justify-center text-xs text-slate-400 italic">
                  No risks to display for the selected filter scope.
                </div>
              )}
            </div>

            {/* Quick summary pill cards */}
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-100 max-h-36 overflow-y-auto pr-1">
              {categoryData.map((cat) => (
                <div key={cat.name} className="bg-slate-50 border border-slate-100 rounded-lg p-2 text-center">
                  <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider truncate" title={cat.name}>{cat.name}</div>
                  <div className="text-sm font-bold font-mono text-slate-800 flex items-center justify-center gap-1 mt-0.5">
                    <span className="w-2 h-2 rounded-full inline-block shrink-0" style={{ backgroundColor: cat.color }}></span>
                    {cat.count} <span className="text-[10px] font-normal text-slate-400">({cat.percentage}%)</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-100 pt-3 mt-3 text-[10px] text-slate-400 italic text-center">
            Evaluating {tickets.filter(t => categoryScope === 'open' ? t.status !== 'Closed' : categoryScope === 'active' ? t.status === 'Active' : true).length} {categoryScope} risks {selectedCategories.length > 0 ? `across ${selectedCategories.length} selected Cause Categories` : 'grouped directly by Cause Category'}.
          </div>
        </div>

        {/* Right Side: Severity Breakdown Grid list */}
        <div className="md:col-span-5 bg-white border border-slate-100 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-800">Risk Severity Profile</h3>
                <p className="text-[11px] text-slate-400">
                  Aligned with 5&times;5 Heatmap score matrix.
                </p>
              </div>

              {/* Toggles for Matrix Type and Status Scope */}
              <div className="flex flex-wrap items-center gap-1.5 self-start sm:self-auto">
                <div className="flex bg-slate-100 p-0.5 rounded-md text-[10px] font-medium">
                  <button
                    type="button"
                    onClick={() => setSeverityScope('open')}
                    className={`px-2 py-0.5 rounded transition-all ${severityScope === 'open' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="Open Risks (Active + Eventuated)"
                  >
                    Open
                  </button>
                  <button
                    type="button"
                    onClick={() => setSeverityScope('active')}
                    className={`px-2 py-0.5 rounded transition-all ${severityScope === 'active' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="Active Risks Only"
                  >
                    Active
                  </button>
                  <button
                    type="button"
                    onClick={() => setSeverityScope('all')}
                    className={`px-2 py-0.5 rounded transition-all ${severityScope === 'all' ? 'bg-white text-slate-800 font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                    title="All Risks"
                  >
                    All
                  </button>
                </div>

                <div className="flex bg-slate-100 p-0.5 rounded-md text-[10px] font-medium">
                  <button
                    type="button"
                    onClick={() => setSeverityMatrixType('inherent')}
                    className={`px-2 py-0.5 rounded transition-all ${severityMatrixType === 'inherent' ? 'bg-indigo-600 text-white font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                  >
                    Inherent
                  </button>
                  <button
                    type="button"
                    onClick={() => setSeverityMatrixType('residual')}
                    className={`px-2 py-0.5 rounded transition-all ${severityMatrixType === 'residual' ? 'bg-emerald-600 text-white font-bold shadow-2xs' : 'text-slate-500 hover:text-slate-800'}`}
                  >
                    Residual
                  </button>
                </div>
              </div>
            </div>

            <div className="space-y-3.5 my-4">
              {/* Very High */}
              <div className="flex items-center gap-3">
                <span className={`w-28 font-bold text-xs ${RISK_LEVEL_COLORS['Very High'].text} uppercase`}>
                  Very High (23–25)
                </span>
                <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#ea4335] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${summary.severityTotalCount > 0 ? (summary.veryHighCount / summary.severityTotalCount) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="w-8 text-right text-xs font-bold font-mono">{summary.veryHighCount}</span>
              </div>

              {/* High */}
              <div className="flex items-center gap-3">
                <span className={`w-28 font-bold text-xs ${RISK_LEVEL_COLORS['High'].text} uppercase`}>
                  High (18–22)
                </span>
                <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#ff9900] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${summary.severityTotalCount > 0 ? (summary.highCount / summary.severityTotalCount) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="w-8 text-right text-xs font-bold font-mono">{summary.highCount}</span>
              </div>

              {/* Medium */}
              <div className="flex items-center gap-3">
                <span className={`w-28 font-bold text-xs ${RISK_LEVEL_COLORS['Medium'].text} uppercase`}>
                  Medium (13–17)
                </span>
                <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#eedb33] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${summary.severityTotalCount > 0 ? (summary.mediumCount / summary.severityTotalCount) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="w-8 text-right text-xs font-bold font-mono">{summary.mediumCount}</span>
              </div>

              {/* Low */}
              <div className="flex items-center gap-3">
                <span className={`w-28 font-bold text-xs ${RISK_LEVEL_COLORS['Low'].text} uppercase`}>
                  Low (7–12)
                </span>
                <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#34a853] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${summary.severityTotalCount > 0 ? (summary.lowCount / summary.severityTotalCount) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="w-8 text-right text-xs font-bold font-mono">{summary.lowCount}</span>
              </div>

              {/* Very Low */}
              <div className="flex items-center gap-3">
                <span className={`w-28 font-bold text-xs ${RISK_LEVEL_COLORS['Very Low'].text} uppercase`}>
                  Very Low (1–6)
                </span>
                <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                  <div 
                    className="bg-[#93c47d] h-full rounded-full transition-all duration-500" 
                    style={{ width: `${summary.severityTotalCount > 0 ? (summary.veryLowCount / summary.severityTotalCount) * 100 : 0}%` }}
                  ></div>
                </div>
                <span className="w-8 text-right text-xs font-bold font-mono">{summary.veryLowCount}</span>
              </div>

              {/* Unrated / Missing ratings */}
              {summary.unratedCount > 0 && (
                <div className="flex items-center gap-3 pt-1 border-t border-slate-100">
                  <span className="w-28 font-semibold text-xs text-slate-400 uppercase">
                    Unrated / Pending
                  </span>
                  <div className="flex-1 bg-slate-100 h-2.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-slate-300 h-full rounded-full transition-all duration-500" 
                      style={{ width: `${summary.severityTotalCount > 0 ? (summary.unratedCount / summary.severityTotalCount) * 100 : 0}%` }}
                    ></div>
                  </div>
                  <span className="w-8 text-right text-xs font-bold font-mono text-slate-400">{summary.unratedCount}</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="border-t border-slate-100 pt-3 text-[10px] text-slate-400 italic text-center">
            {summary.severityTotalCount} {severityScope} risks evaluated across 5&times;5 heatmap cells. Total {severityMatrixType} score: {tickets.filter(t => severityScope === 'open' ? t.status !== 'Closed' : severityScope === 'active' ? t.status === 'Active' : true).reduce((sum, t) => sum + ((severityMatrixType === 'inherent' ? t.inherentRiskScore : t.residualRiskScore) || 0), 0)}.
          </div>
        </div>

      </div>

      {/* Dynamic Summary Cards (Moved to Bottom) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
        {/* Active Backlog */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-2xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Risk Backlog</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-slate-800">{summary.activeCount}</span>
              <span className={`text-xs font-semibold flex items-center gap-0.5 ${summary.backlogChange > 0 ? 'text-red-500' : summary.backlogChange < 0 ? 'text-emerald-500' : 'text-slate-400'}`}>
                {summary.backlogChange > 0 ? <TrendingUp className="w-3.5 h-3.5" /> : summary.backlogChange < 0 ? <TrendingDown className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
                {summary.backlogChange !== 0 ? Math.abs(summary.backlogChange) : '0'} vs prev period
              </span>
            </div>
          </div>
          <div className="bg-indigo-50 p-3 rounded-xl">
            <Layers className="w-5 h-5 text-indigo-600" />
          </div>
        </div>

        {/* High-Priority Risks Card */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-2xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">High-Priority Risks</span>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-rose-600">{summary.highPriorityCount}</span>
              <span className="text-xs text-slate-400 font-semibold">Score &ge; 10 (High+)</span>
            </div>
          </div>
          <div className="bg-rose-50 p-3 rounded-xl">
            <Flame className="w-5 h-5 text-rose-600 animate-pulse" />
          </div>
        </div>

        {/* Average Mitigation Efficiency */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-2xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Mitigation Efficiency</span>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-extrabold text-slate-800">
                {parseFloat(summary.avgInherent) > 0 ? (((parseFloat(summary.avgInherent) - parseFloat(summary.avgResidual)) / parseFloat(summary.avgInherent)) * 100).toFixed(0) : 0}%
              </span>
              <span className="text-xs text-slate-400 font-semibold">avg risk reduction</span>
            </div>
          </div>
          <div className="bg-purple-50 p-3 rounded-xl">
            <TrendingDown className="w-5 h-5 text-purple-600" />
          </div>
        </div>

        {/* Overdue Treatments */}
        <div className="bg-white border border-slate-100 rounded-xl p-5 shadow-2xs flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Overdue Target Dates</span>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl font-extrabold ${summary.overdueCount > 0 ? 'text-red-600' : 'text-slate-800'}`}>
                {summary.overdueCount}
              </span>
              <span className="text-xs text-slate-400 font-semibold">Requires attention</span>
            </div>
          </div>
          <div className="bg-red-50 p-3 rounded-xl">
            <AlertOctagon className="w-5 h-5 text-red-600" />
          </div>
        </div>
      </div>
    </div>
  );
}

