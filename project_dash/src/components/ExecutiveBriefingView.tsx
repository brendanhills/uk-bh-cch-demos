/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { Sparkles, AlertTriangle, CheckCircle2, TrendingUp, ShieldAlert, ArrowRight, Clock, Target, Users } from 'lucide-react';
import { RiskTicket, IssueTicket } from '../types';

interface ExecutiveBriefingViewProps {
  tickets: RiskTicket[];
  issues: IssueTicket[];
}

export default function ExecutiveBriefingView({ tickets, issues }: ExecutiveBriefingViewProps) {
  // Top 5 active risks by residual risk score
  const top5Risks = [...tickets]
    .filter(t => t.status !== 'Closed')
    .sort((a, b) => (b.residualRiskScore || 0) - (a.residualRiskScore || 0))
    .slice(0, 5);

  // Top 5 issues by criticality
  const top5Issues = [...issues]
    .filter(i => i.status !== 'Closed' && i.status !== 'Resolved')
    .slice(0, 5);

  return (
    <div className="space-y-6">
      
      {/* Executive Briefing Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-6 shadow-lg border border-slate-800">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3.5">
            <div className="bg-indigo-600/30 border border-indigo-500/40 p-3 rounded-xl backdrop-blur-xs text-indigo-300">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-extrabold tracking-tight">Executive Briefing & Governance Summary</h2>
                <span className="bg-indigo-500/30 text-indigo-200 text-xs font-semibold px-2.5 py-0.5 rounded-full border border-indigo-400/30">
                  Leadership Ready
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1">
                F-DSE Program Review • Executive escalation items, top risks, and critical path governance
              </p>
            </div>
          </div>

          <div className="bg-slate-800/80 border border-slate-700 rounded-xl px-4 py-2 flex items-center gap-2 text-xs">
            <Clock className="w-4 h-4 text-indigo-400" />
            <span>Baseline Briefing Date: <strong className="text-white">29 Jul 2026</strong></span>
          </div>
        </div>
      </div>

      {/* Top 5 Risks & Top 5 Issues Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Top 5 Risks */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="bg-red-50 text-red-600 p-2 rounded-xl">
                <ShieldAlert className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Top 5 Critical Risks</h3>
                <p className="text-xs text-slate-500">Ranked by Residual Risk Rating</p>
              </div>
            </div>
            <span className="bg-red-100 text-red-800 text-xs font-bold px-2.5 py-1 rounded-md">
              Score ≥ 15
            </span>
          </div>

          <div className="space-y-3">
            {top5Risks.map((risk, index) => (
              <div key={risk.id} className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-indigo-600">#{index + 1} {risk.id}</span>
                    <span className="text-[11px] font-semibold text-slate-500">• {risk.riskOwner}</span>
                  </div>
                  <p className="text-xs font-medium text-slate-800">{risk.riskName}</p>
                </div>
                <div className="text-right shrink-0">
                  <span className="bg-red-500 text-white font-bold text-xs px-2 py-0.5 rounded">
                    Score {risk.residualRiskScore || risk.inherentRiskScore || '-'}
                  </span>
                  <div className="text-[10px] text-slate-500 mt-1 font-semibold">{risk.trend || 'Same'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top 5 Issues */}
        <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="bg-amber-50 text-amber-600 p-2 rounded-xl">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-slate-900">Top 5 Escalated Issues</h3>
                <p className="text-xs text-slate-500">Active blockers impacting milestones</p>
              </div>
            </div>
            <span className="bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-md">
              Active Blockers
            </span>
          </div>

          <div className="space-y-3">
            {top5Issues.map((issue, index) => (
              <div key={issue.id} className="p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-amber-600">#{index + 1} {issue.id}</span>
                    <span className="text-[11px] font-semibold text-slate-500">• {issue.issueOwner}</span>
                  </div>
                  <p className="text-xs font-medium text-slate-800">{issue.issueName}</p>
                </div>
                <div className="text-right shrink-0">
                  <span className="bg-amber-500 text-white font-bold text-xs px-2 py-0.5 rounded">
                    {issue.severityRating || 'Critical'}
                  </span>
                  <div className="text-[10px] text-purple-600 mt-1 font-bold">{issue.governanceLevel || 'IPF'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
