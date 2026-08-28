/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { RiskTicket, IssueTicket, LIKELIHOOD_LABELS, CONSEQUENCE_LABELS, calculateRiskLevel, RISK_LEVEL_COLORS, getMatrixScore } from '../types';
import { ShieldAlert, ShieldCheck, Flame, Clock, ChevronDown, ChevronUp, Layers, Info, X } from 'lucide-react';

interface RiskMatrixProps {
  tickets: RiskTicket[];
  issues?: IssueTicket[];
  onCellClick?: (likelihood: number, consequence: number, type: 'inherent' | 'residual') => void;
  selectedCell?: { likelihood: number; consequence: number; type: 'inherent' | 'residual' } | null;
}

export default function RiskMatrix({ tickets, issues, onCellClick, selectedCell }: RiskMatrixProps) {
  const [matrixType, setMatrixType] = useState<'inherent' | 'residual'>('inherent');
  const [statusScope, setStatusScope] = useState<'open' | 'active' | 'eventuated' | 'closed' | 'all'>('open');
  const [expandedTab, setExpandedTab] = useState<'top' | 'unactioned' | null>(null);
  const [showInterpretationModal, setShowInterpretationModal] = useState(false);

  // Filter display tickets based on status scope
  const displayTickets = tickets.filter(t => {
    if (statusScope === 'open') return t.status !== 'Closed';
    if (statusScope === 'active') return t.status === 'Active';
    if (statusScope === 'eventuated') return t.status === 'Issue Eventuated';
    if (statusScope === 'closed') return t.status === 'Closed';
    return true; // 'all'
  });

  // Top risks: display risks with score 23, 24, 25
  const topRisks = displayTickets.filter(t => {
    const l = matrixType === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
    const c = matrixType === 'inherent' ? t.inherentConsequence : t.residualConsequence;
    const score = getMatrixScore(l, c);
    return score !== null && (score === 23 || score === 24 || score === 25);
  });

  // Unactioned risks: display risks not updated/raised in the last 7 days
  const unactionedRisks = displayTickets.filter(t => {
    const lastDateStr = t.riskLastUpdated || t.dateRaised;
    if (!lastDateStr || lastDateStr === '-') return true;
    const lastDate = new Date(lastDateStr);
    if (isNaN(lastDate.getTime())) return false;
    const diffTime = new Date().getTime() - lastDate.getTime();
    const diffDays = diffTime / (1000 * 60 * 60 * 24);
    return diffDays > 7;
  });

  const getDaysSince = (dateStr?: string) => {
    if (!dateStr || dateStr === '-') return 0;
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return 0;
    const diffTime = new Date().getTime() - date.getTime();
    return Math.max(0, Math.floor(diffTime / (1000 * 60 * 60 * 24)));
  };

  // Count tickets in each cell (likelihood x consequence)
  const getCellTickets = (likelihood: number, consequence: number) => {
    return displayTickets.filter(t => {
      const l = matrixType === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
      const c = matrixType === 'inherent' ? t.inherentConsequence : t.residualConsequence;
      return l === likelihood && c === consequence;
    });
  };

  const getCellColor = (likelihood: number, consequence: number) => {
    const score = getMatrixScore(likelihood, consequence);
    
    if (score !== null && score >= 23) {
      // Very High (23-25): ea4335 (Red)
      return 'bg-[#ea4335] hover:bg-[#ea4335]/90 text-white border-[#ea4335]';
    } else if (score !== null && score >= 18) {
      // High (18-22): ff9900 (Orange)
      return 'bg-[#ff9900] hover:bg-[#ff9900]/90 text-white border-[#ff9900]';
    } else if (score !== null && score >= 13) {
      // Medium (13-17): fdfdb9 (Yellow)
      return 'bg-[#fdfdb9] hover:bg-[#fdfdb9]/90 text-amber-950 border-[#eaeaa3] font-medium';
    } else if (score !== null && score >= 7) {
      // Low (7-12): 34a853 (Dark Green)
      return 'bg-[#34a853] hover:bg-[#34a853]/90 text-white border-[#34a853]';
    } else {
      // Very Low (1-6): 93c47d (Light Green)
      return 'bg-[#93c47d] hover:bg-[#93c47d]/90 text-slate-900 border-[#85b570]';
    }
  };

  const getCellLabelColor = (likelihood: number, consequence: number) => {
    const score = getMatrixScore(likelihood, consequence);
    
    if (score !== null && score >= 23) {
      return 'bg-[#c2362a] text-white';
    } else if (score !== null && score >= 18) {
      return 'bg-[#d98200] text-white';
    } else if (score !== null && score >= 13) {
      return 'bg-[#dede95] text-amber-950 border border-amber-300/30';
    } else if (score !== null && score >= 7) {
      return 'bg-[#298542] text-white';
    } else {
      return 'bg-[#82b36c] text-slate-900';
    }
  };

  return (
    <div id="risk-matrix-panel" className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm relative overflow-hidden transition-all duration-300 hover:shadow-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
            {matrixType === 'inherent' ? (
              <ShieldAlert className="w-5 h-5 text-red-500" />
            ) : (
              <ShieldCheck className="w-5 h-5 text-emerald-500" />
            )}
            5x5 Risk Heatmap ({displayTickets.length} Risks)
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Tap any cell to inspect
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-start sm:self-center">
          {/* Status Scope Selector */}
          <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
            <button
              onClick={() => setStatusScope('open')}
              className={`px-2.5 py-1.5 rounded-md transition-all cursor-pointer ${
                statusScope === 'open'
                  ? 'bg-white text-slate-800 shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
              title="Includes Active and Issue Eventuated (All Open Risks)"
            >
              Open ({tickets.filter(t => t.status !== 'Closed').length})
            </button>
            <button
              onClick={() => setStatusScope('active')}
              className={`px-2.5 py-1.5 rounded-md transition-all cursor-pointer ${
                statusScope === 'active'
                  ? 'bg-white text-slate-800 shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Active ({tickets.filter(t => t.status === 'Active').length})
            </button>
            <button
              onClick={() => setStatusScope('eventuated')}
              className={`px-2.5 py-1.5 rounded-md transition-all cursor-pointer ${
                statusScope === 'eventuated'
                  ? 'bg-white text-slate-800 shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Eventuated ({tickets.filter(t => t.status === 'Issue Eventuated').length})
            </button>
            <button
              onClick={() => setStatusScope('all')}
              className={`px-2.5 py-1.5 rounded-md transition-all cursor-pointer ${
                statusScope === 'all'
                  ? 'bg-white text-slate-800 shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              All ({tickets.length})
            </button>
          </div>

          {/* Matrix Type Switcher */}
          <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium">
            <button
              onClick={() => setMatrixType('inherent')}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                matrixType === 'inherent'
                  ? 'bg-indigo-600 text-white shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Inherent
            </button>
            <button
              onClick={() => setMatrixType('residual')}
              className={`px-3 py-1.5 rounded-md transition-all cursor-pointer ${
                matrixType === 'residual'
                  ? 'bg-emerald-600 text-white shadow-xs font-semibold'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Residual
            </button>
          </div>
        </div>
      </div>

      {/* Interactive Data Tabs (Extreme Score 23-25 & Idle Risks) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {/* Tab 1: Top Risks (Score 23-25) - High Visibility */}
        <button
          onClick={() => setExpandedTab(expandedTab === 'top' ? null : 'top')}
          className={`relative overflow-hidden flex items-center justify-between p-4 pl-5 rounded-2xl border text-left transition-all duration-300 cursor-pointer ${
            expandedTab === 'top'
              ? 'bg-gradient-to-r from-red-100/90 via-red-50 to-white border-red-400 ring-2 ring-red-400/40 shadow-md scale-[1.01]'
              : 'bg-gradient-to-r from-red-50/80 via-rose-50/30 to-white border-red-200/90 hover:border-red-300 hover:shadow-md hover:bg-red-50/90 shadow-xs'
          }`}
        >
          {/* Accent left indicator bar */}
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-red-500 via-rose-500 to-red-600 rounded-l-2xl" />

          <div className="flex items-center gap-3.5">
            <div className={`p-2.5 rounded-xl transition-all duration-300 shadow-xs ${
              expandedTab === 'top' 
                ? 'bg-gradient-to-br from-red-600 to-rose-700 text-white ring-2 ring-red-300' 
                : 'bg-gradient-to-br from-red-500 to-rose-600 text-white'
            }`}>
              <Flame className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="text-[10px] font-extrabold text-red-700/80 uppercase tracking-wider block">
                Extreme Top Risks
              </span>
              <span className="text-2xl font-black text-slate-900 tracking-tight block font-mono leading-tight">
                {topRisks.length} <span className="text-xs font-semibold text-red-600/90">Active</span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="text-xs font-extrabold text-white bg-gradient-to-r from-red-600 to-rose-600 px-2.5 py-1 rounded-lg font-mono shadow-xs tracking-wide">
              Score 23–25
            </span>
            {expandedTab === 'top' ? (
              <ChevronUp className="w-4 h-4 text-red-600" />
            ) : (
              <ChevronDown className="w-4 h-4 text-red-400" />
            )}
          </div>
        </button>

        {/* Tab 2: Unactioned Risks (>7 Days Idle) */}
        <button
          onClick={() => setExpandedTab(expandedTab === 'unactioned' ? null : 'unactioned')}
          className={`relative overflow-hidden flex items-center justify-between p-4 pl-5 rounded-2xl border text-left transition-all duration-300 cursor-pointer ${
            expandedTab === 'unactioned'
              ? 'bg-gradient-to-r from-amber-100/90 via-amber-50 to-white border-amber-400 ring-2 ring-amber-400/40 shadow-md scale-[1.01]'
              : 'bg-gradient-to-r from-amber-50/60 via-amber-50/20 to-white border-amber-200/80 hover:border-amber-300 hover:shadow-md hover:bg-amber-50/80 shadow-xs'
          }`}
        >
          {/* Accent left indicator bar */}
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-amber-400 to-amber-500 rounded-l-2xl" />

          <div className="flex items-center gap-3.5">
            <div className={`p-2.5 rounded-xl transition-all duration-300 shadow-xs ${
              expandedTab === 'unactioned' 
                ? 'bg-gradient-to-br from-amber-500 to-amber-600 text-white ring-2 ring-amber-300' 
                : 'bg-gradient-to-br from-amber-400 to-amber-500 text-white'
            }`}>
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] font-extrabold text-amber-700/80 uppercase tracking-wider block">
                Idle / Unactioned Risks
              </span>
              <span className="text-2xl font-black text-slate-900 tracking-tight block font-mono leading-tight">
                {unactionedRisks.length} <span className="text-xs font-semibold text-amber-600/90">Active</span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <span className="text-xs font-bold text-amber-800 bg-amber-100 border border-amber-200/80 px-2.5 py-1 rounded-lg font-mono shadow-2xs">
              &gt;7 Days Idle
            </span>
            {expandedTab === 'unactioned' ? (
              <ChevronUp className="w-4 h-4 text-amber-600" />
            ) : (
              <ChevronDown className="w-4 h-4 text-amber-400" />
            )}
          </div>
        </button>
      </div>

      {/* Expanded Breakdown Accordion Panel */}
      {expandedTab && (
        <div className={`mb-6 p-4 rounded-xl border transition-all duration-200 ${
          expandedTab === 'top' ? 'bg-red-50/20 border-red-200/60' : 'bg-amber-50/20 border-amber-200/60'
        }`}>
          <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-100">
            <h5 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
              {expandedTab === 'top' ? (
                <>
                  <Flame className="w-4 h-4 text-[#ea4335]" />
                  Extreme Risks Breakdown ({topRisks.length})
                </>
              ) : (
                <>
                  <Clock className="w-4 h-4 text-[#ff9900]" />
                  Unactioned Risks Breakdown (&gt;7 days idle) ({unactionedRisks.length})
                </>
              )}
            </h5>
            <button
              onClick={() => setExpandedTab(null)}
              className="text-xs text-slate-400 hover:text-slate-600 font-medium cursor-pointer"
            >
              Close
            </button>
          </div>

          <div className="max-h-64 overflow-y-auto space-y-2 pr-1">
            {expandedTab === 'top' ? (
              topRisks.length > 0 ? (
                topRisks.map(t => {
                  const l = matrixType === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
                  const c = matrixType === 'inherent' ? t.inherentConsequence : t.residualConsequence;
                  const score = getMatrixScore(l, c);
                  return (
                    <div key={t.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-white border border-red-100/50 rounded-lg hover:border-red-200 hover:shadow-xs transition-all text-xs gap-2">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-red-700 bg-red-50 px-1.5 py-0.5 rounded text-[10px]">{t.id}</span>
                          <span className="font-semibold text-slate-800 line-clamp-1">{t.riskName}</span>
                        </div>
                        <div className="text-slate-500 text-[11px] line-clamp-1">Owner: <span className="font-medium text-slate-700">{t.riskOwner}</span> | Cause: {t.causeCategory}</div>
                      </div>
                      <div className="flex items-center gap-2.5 self-start sm:self-center">
                        <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded font-bold">
                          Score: {score}
                        </span>
                        <button
                          onClick={() => onCellClick?.(l || 0, c || 0, matrixType)}
                          className="text-[11px] text-indigo-600 hover:text-indigo-800 hover:underline font-semibold cursor-pointer"
                        >
                          Highlight Cell &rarr;
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-slate-400 italic text-center py-4">No active risks currently score 23-25 in the {matrixType} matrix.</p>
              )
            ) : (
              unactionedRisks.length > 0 ? (
                unactionedRisks.map(t => {
                  const days = getDaysSince(t.riskLastUpdated || t.dateRaised);
                  const l = matrixType === 'inherent' ? t.inherentLikelihood : t.residualLikelihood;
                  const c = matrixType === 'inherent' ? t.inherentConsequence : t.residualConsequence;
                  return (
                    <div key={t.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-white border border-amber-100/50 rounded-lg hover:border-amber-200 hover:shadow-xs transition-all text-xs gap-2">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono font-bold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded text-[10px]">{t.id}</span>
                          <span className="font-semibold text-slate-800 line-clamp-1">{t.riskName}</span>
                        </div>
                        <div className="text-slate-500 text-[11px] line-clamp-1">
                          Owner: <span className="font-medium text-slate-700">{t.riskOwner}</span> | Raised: <span className="font-medium text-slate-700">{t.dateRaised}</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2.5 self-start sm:self-center">
                        <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold font-mono">
                          {days} days idle
                        </span>
                        <button
                          onClick={() => onCellClick?.(l || 0, c || 0, matrixType)}
                          className="text-[11px] text-indigo-600 hover:text-indigo-800 hover:underline font-semibold cursor-pointer"
                        >
                          Highlight Cell &rarr;
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <p className="text-xs text-slate-400 italic text-center py-4">All active risks have been actioned or updated in the last 7 days.</p>
              )
            )}
          </div>
        </div>
      )}

      <div className="w-full flex flex-col gap-6">
        {/* The Matrix Grid Container */}
        <div className="w-full">
          {/* Main Matrix with Consequence on Y-axis and Likelihood on X-axis */}
          <div className="flex flex-col gap-2.5 w-full">
            {/* X-Axis Labels at the top (Likelihoods 1 to 5, left to right) */}
            <div className="flex items-center h-8 mb-1">
              {/* Spacer matching Y-axis labels width */}
              <div className="w-32"></div>
              <div className="flex-1 grid grid-cols-5 gap-2.5">
                {[1, 2, 3, 4, 5].map((likelihood) => (
                  <div key={likelihood} className="text-center text-[11px] font-bold text-slate-500 uppercase tracking-wider select-none">
                    {LIKELIHOOD_LABELS[likelihood]}
                  </div>
                ))}
              </div>
            </div>

            {/* 5 Rows for Consequence, from 5 down to 1 (Catastrophic to Minor) */}
            {[5, 4, 3, 2, 1].map((consequence) => (
              <div key={consequence} className="flex items-stretch h-16">
                {/* Y-Axis Label: Consequence (bottom to top, so top is Catastrophic, bottom is Minor) */}
                <div className="w-32 flex items-center justify-end pr-3 text-right text-xs font-semibold text-slate-500 select-none">
                  <span className="truncate" title={CONSEQUENCE_LABELS[consequence]}>
                    {CONSEQUENCE_LABELS[consequence]}
                  </span>
                </div>

                {/* 5 cells for Likelihood, from 1 to 5 */}
                <div className="flex-1 grid grid-cols-5 gap-2.5">
                  {[1, 2, 3, 4, 5].map((likelihood) => {
                    const cellTickets = getCellTickets(likelihood, consequence);
                    const isSelected = selectedCell && 
                                      selectedCell.likelihood === likelihood && 
                                      selectedCell.consequence === consequence &&
                                      selectedCell.type === matrixType;
                    const matrixScoreValue = getMatrixScore(likelihood, consequence);
                    
                    return (
                      <button
                        key={likelihood}
                        onClick={() => onCellClick?.(likelihood, consequence, matrixType)}
                        className={`border rounded-lg flex flex-col items-center justify-center p-1 relative transition-all cursor-pointer ${getCellColor(
                          likelihood,
                          consequence
                        )} ${
                          isSelected
                            ? 'ring-2 ring-indigo-600 ring-offset-1 border-indigo-500 scale-[1.02] z-10 shadow-sm'
                            : 'hover:scale-[1.01]'
                        }`}
                      >
                        {/* Score Indicator */}
                        <span className={`absolute top-1 right-1.5 text-xs font-mono font-bold ${
                          matrixScoreValue >= 23 ? 'text-white/95' :
                          matrixScoreValue >= 18 ? 'text-white/95' :
                          matrixScoreValue >= 13 ? 'text-amber-950/90' :
                          matrixScoreValue >= 7  ? 'text-white/95' :
                          'text-slate-950/85'
                        }`}>
                          {matrixScoreValue}
                        </span>

                        {/* Ticket count dot/badge */}
                        {cellTickets.length > 0 ? (
                          <div className={`flex items-center justify-center w-7 h-7 rounded-full font-extrabold text-sm shadow-2xs transition-transform ${getCellLabelColor(likelihood, consequence)}`}>
                            {cellTickets.length}
                          </div>
                        ) : (
                          <span className="text-xs text-slate-400 font-medium">-</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}

            {/* Matrix Labels */}
            <div className="flex justify-center mt-0 mb-0 pr-[5px] border-solid border-0 text-xs font-semibold text-slate-600 select-none gap-2">
              <span className="pl-0 pr-[5px] text-[14px]">&larr; Likelihood Axis (Horizontal)</span>
              <span>|</span>
              <span className="text-[14px]">Consequence Axis (Vertical) &rarr;</span>
            </div>
          </div>
        </div>


      </div>



      {/* Dynamic Interpretation Modal Popup */}
      {showInterpretationModal && (
        <div id="matrix-interpretation-modal" className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-lg w-full p-6 relative overflow-hidden animate-in zoom-in-95 duration-200">
            {/* Close trigger button */}
            <button
              onClick={() => setShowInterpretationModal(false)}
              className="absolute top-4 right-4 p-2 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors cursor-pointer"
              title="Close modal"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3 mb-5 pb-3 border-b border-slate-100">
              <div className="p-2.5 rounded-xl bg-indigo-50 text-indigo-600">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-800">Matrix Interpretation Guide</h3>
                <p className="text-xs text-slate-500 mt-0.5">Heatmap scoring levels & classification thresholds.</p>
              </div>
            </div>

            {/* Content List containing the five custom categories */}
            <div className="space-y-4 my-2 max-h-[60vh] overflow-y-auto pr-1">
              {/* Very High */}
              <div className="p-3.5 bg-red-50/45 border border-red-100 rounded-2xl flex gap-3.5 items-start">
                <span className="w-3.5 h-3.5 rounded-full bg-[#ea4335] mt-1 flex-shrink-0 animate-pulse" />
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold text-slate-800 text-sm">Very High Exposure</span>
                    <span className="text-xs text-red-600 font-bold bg-red-50 px-1.5 py-0.5 rounded-md font-mono">Score 19–25</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Extremely severe impact and very high likelihood. Requires immediate executive containment action, active containment plans, and real-time mitigation auditing.
                  </p>
                </div>
              </div>

              {/* High */}
              <div className="p-3.5 bg-orange-50/45 border border-orange-100 rounded-2xl flex gap-3.5 items-start">
                <span className="w-3.5 h-3.5 rounded-full bg-[#ff9900] mt-1 flex-shrink-0" />
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold text-slate-800 text-sm">High Exposure</span>
                    <span className="text-xs text-amber-700 font-bold bg-amber-50 px-1.5 py-0.5 rounded-md font-mono">Score 14–18</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Significant business danger. Prompt resolution actions must be assigned with clear target delivery milestones and monitored weekly.
                  </p>
                </div>
              </div>

              {/* Medium */}
              <div className="p-3.5 bg-yellow-50/45 border border-yellow-100 rounded-2xl flex gap-3.5 items-start">
                <span className="w-3.5 h-3.5 rounded-full bg-[#fdfdb9] border border-amber-300 mt-1 flex-shrink-0" />
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold text-slate-800 text-sm">Medium Exposure</span>
                    <span className="text-xs text-yellow-800 font-bold bg-yellow-100/40 px-1.5 py-0.5 rounded-md font-mono">Score 10–13</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Standard operational risks. Managed effectively through regular procedural controls, mitigation workflows, and periodic ledger reviews.
                  </p>
                </div>
              </div>

              {/* Low */}
              <div className="p-3.5 bg-green-50/30 border border-green-100/60 rounded-2xl flex gap-3.5 items-start">
                <span className="w-3.5 h-3.5 rounded-full bg-[#34a853] mt-1 flex-shrink-0" />
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold text-slate-800 text-sm">Low Exposure</span>
                    <span className="text-xs text-green-800 font-bold bg-green-50 px-1.5 py-0.5 rounded-md font-mono">Score 5–9</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Minor operational impact. Addressed via standard controls and monitored via regular quarterly cycles.
                  </p>
                </div>
              </div>

              {/* Very Low */}
              <div className="p-3.5 bg-emerald-50/20 border border-emerald-100/40 rounded-2xl flex gap-3.5 items-start">
                <span className="w-3.5 h-3.5 rounded-full bg-[#93c47d] mt-1 flex-shrink-0" />
                <div className="space-y-1">
                  <div className="flex items-baseline gap-2">
                    <span className="font-bold text-slate-800 text-sm">Very Low Exposure</span>
                    <span className="text-xs text-emerald-800 font-bold bg-emerald-50 px-1.5 py-0.5 rounded-md font-mono">Score 1–4</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed">
                    Acceptable risk variance. Generally self-correcting and negligible to core product lines or critical services.
                  </p>
                </div>
              </div>
            </div>

            {/* Footer with actions */}
            <div className="mt-5 pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setShowInterpretationModal(false)}
                className="px-5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs cursor-pointer transition-colors"
              >
                Understood
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
