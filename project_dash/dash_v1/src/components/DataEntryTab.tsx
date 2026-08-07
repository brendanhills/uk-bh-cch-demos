/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  RiskTicket, 
  RiskStatus, 
  CauseCategory, 
  RiskTrend, 
  RiskPriority, 
  GovernanceLevel, 
  calculateRiskLevel,
  getMatrixScore,
  LIKELIHOOD_LABELS,
  CONSEQUENCE_LABELS,
  RISK_LEVEL_COLORS,
  calculateOpenDays
} from '../types';
import { Save, RefreshCw, X, AlertTriangle, Shield, CheckCircle2, ArrowRight } from 'lucide-react';

interface DataEntryTabProps {
  editingTicket?: RiskTicket | null;
  onSave: (ticket: RiskTicket) => void;
  onCancel: () => void;
  nextId: string;
}

export default function DataEntryTab({ editingTicket, onSave, onCancel, nextId }: DataEntryTabProps) {
  // Field States
  const [id, setId] = useState('');
  const [status, setStatus] = useState<RiskStatus>('Active');
  const [riskOwner, setRiskOwner] = useState('');
  const [bundle, setBundle] = useState('');
  const [driverTreeRef, setDriverTreeRef] = useState('');
  const [riskName, setRiskName] = useState('');
  const [riskDescription, setRiskDescription] = useState('');
  const [causeDescription, setCauseDescription] = useState('');
  const [causeCategory, setCauseCategory] = useState<CauseCategory>('Technical');
  const [consequenceDescription, setConsequenceDescription] = useState('');
  const [trend, setTrend] = useState<RiskTrend>('Stable');
  const [priority, setPriority] = useState<RiskPriority>('Prompt');
  const [governanceLevel, setGovernanceLevel] = useState<GovernanceLevel>('Google Only');
  
  // Extra spreadsheet fields
  const [relatedIssueId, setRelatedIssueId] = useState('');
  const [riskLastUpdated, setRiskLastUpdated] = useState('');
  const [comments, setComments] = useState('');
  const [protectedIssueRisk, setProtectedIssueRisk] = useState('No');
  const [dpeRefNumber, setDpeRefNumber] = useState('');
  const [timelines, setTimelines] = useState('Q3 2026');
  const [signOffRequirement, setSignOffRequirement] = useState('No');
  const [executiveStatus, setExecutiveStatus] = useState('Pending');
  const [nextMitigationDueDate, setNextMitigationDueDate] = useState('');
  const [mitigationStatus, setMitigationStatus] = useState('Pending');
  const [strategy, setStrategy] = useState('Mitigate');
  const [whoRaised, setWhoRaised] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // Risk assessment states
  const [inherentLikelihood, setInherentLikelihood] = useState<number>(3);
  const [inherentConsequence, setInherentConsequence] = useState<number>(3);
  const [treatmentOwner, setTreatmentOwner] = useState('');
  const [treatmentPlan, setTreatmentPlan] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [residualLikelihood, setResidualLikelihood] = useState<number>(2);
  const [residualConsequence, setResidualConsequence] = useState<number>(2);
  const [dateRaised, setDateRaised] = useState('');
  const [dateClosed, setDateClosed] = useState('');

  // Auto-calculated fields
  const inherentRiskScore = getMatrixScore(inherentLikelihood, inherentConsequence);
  const inherentRiskLevel = calculateRiskLevel(inherentRiskScore);
  
  const residualRiskScore = getMatrixScore(residualLikelihood, residualConsequence);
  const residualRiskLevel = calculateRiskLevel(residualRiskScore);

  // Load ticket if editing, else set default raised date to today
  useEffect(() => {
    if (editingTicket) {
      setId(editingTicket.id);
      setStatus(editingTicket.status);
      setRiskOwner(editingTicket.riskOwner);
      setBundle(editingTicket.bundle);
      setDriverTreeRef(editingTicket.driverTreeRef || '');
      setRiskName(editingTicket.riskName);
      setRiskDescription(editingTicket.riskDescription);
      setCauseDescription(editingTicket.causeDescription);
      setCauseCategory(editingTicket.causeCategory);
      setConsequenceDescription(editingTicket.consequenceDescription);
      setTrend(editingTicket.trend);
      setPriority(editingTicket.priority);
      setGovernanceLevel(editingTicket.governanceLevel);
      setInherentLikelihood(editingTicket.inherentLikelihood);
      setInherentConsequence(editingTicket.inherentConsequence);
      setTreatmentOwner(editingTicket.treatmentOwner);
      setTreatmentPlan(editingTicket.treatmentPlan);
      setTargetDate(editingTicket.targetDate);
      setResidualLikelihood(editingTicket.residualLikelihood);
      setResidualConsequence(editingTicket.residualConsequence);
      setDateRaised(editingTicket.dateRaised);
      setDateClosed(editingTicket.dateClosed || '');

      setRelatedIssueId(editingTicket.relatedIssueId || '');
      setRiskLastUpdated(editingTicket.riskLastUpdated || editingTicket.dateRaised);
      setComments(editingTicket.comments || '');
      setProtectedIssueRisk(editingTicket.protectedIssueRisk || 'No');
      setDpeRefNumber(editingTicket.dpeRefNumber || '');
      setTimelines(editingTicket.timelines || 'Q3 2026');
      setSignOffRequirement(editingTicket.signOffRequirement || 'No');
      setExecutiveStatus(editingTicket.executiveStatus || 'Pending');
      setNextMitigationDueDate(editingTicket.nextMitigationDueDate || editingTicket.targetDate || '');
      setMitigationStatus(editingTicket.mitigationStatus || 'Pending');
      setStrategy(editingTicket.strategy || 'Mitigate');
      setWhoRaised(editingTicket.whoRaised || '');
    } else {
      setId(nextId);
      setStatus('Active');
      setRiskOwner('');
      setBundle('');
      setDriverTreeRef('');
      setRiskName('');
      setRiskDescription('IF [Event], THEN [Consequence]');
      setCauseDescription('');
      setCauseCategory('Technical');
      setConsequenceDescription('');
      setTrend('Stable');
      setPriority('Prompt');
      setGovernanceLevel('Google Only');
      setInherentLikelihood(3);
      setInherentConsequence(3);
      setTreatmentOwner('');
      setTreatmentPlan('');
      setTargetDate('');
      setResidualLikelihood(2);
      setResidualConsequence(2);
      setDateRaised(new Date().toISOString().split('T')[0]);
      setDateClosed('');

      setRelatedIssueId('');
      setRiskLastUpdated(new Date().toISOString().split('T')[0]);
      setComments('');
      setProtectedIssueRisk('No');
      setDpeRefNumber('');
      setTimelines('Q3 2026');
      setSignOffRequirement('No');
      setExecutiveStatus('Pending');
      setNextMitigationDueDate('');
      setMitigationStatus('Pending');
      setStrategy('Mitigate');
      setWhoRaised('');
    }
  }, [editingTicket, nextId]);

  // Handle template prefill for description
  const applyDescriptionTemplate = () => {
    setRiskDescription('IF [Event happens], THEN [Consequence or Impact on schedule/cost/quality occurs].');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Quick validation
    if (!riskName.trim()) {
      alert('Risk Name is required.');
      return;
    }
    if (!riskOwner.trim()) {
      alert('Risk Owner is required.');
      return;
    }

    const ticket: RiskTicket = {
      id,
      status,
      riskOwner,
      bundle,
      driverTreeRef: driverTreeRef || undefined,
      riskName,
      riskDescription,
      causeDescription,
      causeCategory,
      consequenceDescription,
      trend,
      priority,
      governanceLevel,
      inherentLikelihood,
      inherentConsequence,
      inherentRiskScore,
      inherentRiskLevel,
      treatmentOwner,
      treatmentPlan,
      targetDate,
      residualLikelihood,
      residualConsequence,
      residualRiskScore,
      residualRiskLevel,
      dateRaised,
      dateClosed: status === 'Closed' ? dateClosed || new Date().toISOString().split('T')[0] : undefined,
      relatedIssueId: relatedIssueId || undefined,
      riskLastUpdated: riskLastUpdated || undefined,
      comments: comments || undefined,
      protectedIssueRisk: protectedIssueRisk || undefined,
      dpeRefNumber: dpeRefNumber || undefined,
      timelines: timelines || undefined,
      signOffRequirement: signOffRequirement || undefined,
      executiveStatus: executiveStatus || undefined,
      nextMitigationDueDate: nextMitigationDueDate || undefined,
      mitigationStatus: mitigationStatus || undefined,
      strategy: strategy || undefined,
      whoRaised: whoRaised || undefined
    };

    onSave(ticket);
  };

  return (
    <form id="risk-entry-form" onSubmit={handleSubmit} className="space-y-6">
      <div className="bg-white border border-slate-100 rounded-xl p-6 shadow-xs">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-4 mb-6">
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              {editingTicket ? `Edit Risk: ${editingTicket.id}` : 'Create New Risk'}
            </h2>
            <p className="text-xs text-slate-500 mt-1">
              {editingTicket 
                ? 'Update risk attributes, mitigation strategies, or re-evaluate likelihood and consequence.' 
                : 'Log a new risk entry into the system register to track and govern project uncertainty.'}
            </p>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="p-1.5 rounded-lg border border-slate-200 text-slate-500 hover:text-slate-700 hover:bg-slate-50 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Redesigned Sequential Form Body */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          
          {/* 1. ID */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              ID
            </label>
            <input
              type="text"
              value={id}
              disabled
              className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-500 font-mono"
            />
          </div>

          {/* 2. Status */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Status <span className="text-red-500">*</span>
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as RiskStatus)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
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

          {/* 3. Related Issue ID */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Related Issue ID
            </label>
            <input
              type="text"
              value={relatedIssueId}
              onChange={(e) => setRelatedIssueId(e.target.value)}
              placeholder="e.g. ISS-001"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 4. Risk Owner */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Risk Owner <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={riskOwner}
              onChange={(e) => setRiskOwner(e.target.value)}
              placeholder="e.g. G. Vance"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
              required
            />
          </div>

          {/* 5. Bundle */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Bundle
            </label>
            <input
              type="text"
              value={bundle}
              onChange={(e) => setBundle(e.target.value)}
              placeholder="e.g. Core Platform"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 6. Driver Tree Ref */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Driver Tree Ref
            </label>
            <input
              type="text"
              value={driverTreeRef}
              onChange={(e) => setDriverTreeRef(e.target.value)}
              placeholder="e.g. DTR-01"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 6. Risk Name */}
          <div className="md:col-span-2 lg:col-span-1">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Risk Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={riskName}
              onChange={(e) => setRiskName(e.target.value)}
              placeholder="Short, descriptive risk title"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
              required
            />
          </div>

          {/* 7. Risk Description */}
          <div className="md:col-span-2 lg:col-span-3 bg-slate-50/40 p-3.5 rounded-xl border border-slate-200/50">
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-bold text-slate-700">
                Risk Description
              </label>
              <button
                type="button"
                onClick={applyDescriptionTemplate}
                className="text-[10px] text-indigo-600 hover:text-indigo-800 font-medium cursor-pointer"
              >
                Load Template
              </button>
            </div>
            <textarea
              value={riskDescription}
              onChange={(e) => setRiskDescription(e.target.value)}
              rows={2}
              placeholder="IF [Event], THEN [Consequence]"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 resize-y"
            />
          </div>

          {/* 8. Cause Description */}
          <div className="md:col-span-2 lg:col-span-2">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Cause Description
            </label>
            <textarea
              value={causeDescription}
              onChange={(e) => setCauseDescription(e.target.value)}
              rows={2}
              placeholder="Describe what triggers or causes this risk"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 resize-y"
            />
          </div>

          {/* 9. Cause Category */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Cause Category
            </label>
            <select
              value={causeCategory}
              onChange={(e) => setCauseCategory(e.target.value as CauseCategory)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
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

          {/* 10. Consequence Description */}
          <div className="md:col-span-2 lg:col-span-3">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Consequence Description
            </label>
            <textarea
              value={consequenceDescription}
              onChange={(e) => setConsequenceDescription(e.target.value)}
              rows={2}
              placeholder="Describe the impact or consequence of this risk"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 resize-y"
            />
          </div>

          {/* 11. Trend */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Trend
            </label>
            <select
              value={trend}
              onChange={(e) => setTrend(e.target.value as RiskTrend)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
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

          {/* 12. Priority */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value as RiskPriority)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
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

          {/* 13. Highlight to/Governance Level */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Highlight to/Governance Level
            </label>
            <select
              value={governanceLevel}
              onChange={(e) => setGovernanceLevel(e.target.value as GovernanceLevel)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
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

          {/* 14. Inherent Likelihood Rating */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Inherent Likelihood Rating
            </label>
            <select
              value={inherentLikelihood ?? 0}
              onChange={(e) => setInherentLikelihood(parseInt(e.target.value))}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              {[0, 1, 2, 3, 4, 5, 6].map(val => (
                <option key={val} value={val}>{LIKELIHOOD_LABELS[val]}</option>
              ))}
            </select>
          </div>

          {/* 15. Inherent Consequence Rating */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Inherent Consequence Rating
            </label>
            <select
              value={inherentConsequence ?? 0}
              onChange={(e) => setInherentConsequence(parseInt(e.target.value))}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              {[0, 1, 2, 3, 4, 5, 6].map(val => (
                <option key={val} value={val}>{CONSEQUENCE_LABELS[val]}</option>
              ))}
            </select>
          </div>

          {/* 16. Inherent risk */}
          <div className="bg-rose-50 border border-rose-100 p-2.5 rounded-lg flex items-center justify-between shadow-2xs">
            <div>
              <span className="block text-[10px] uppercase font-bold text-rose-500 tracking-wider">
                Inherent risk
              </span>
              <span className="text-xs font-bold text-slate-800 font-mono mt-0.5 block">
                Score: {inherentRiskScore} / 25
              </span>
            </div>
            <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase shrink-0 ${RISK_LEVEL_COLORS[inherentRiskLevel].bg} ${RISK_LEVEL_COLORS[inherentRiskLevel].text} ${RISK_LEVEL_COLORS[inherentRiskLevel].border}`}>
              {inherentRiskLevel}
            </span>
          </div>

          {/* 17. Treatment Owner */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Treatment Owner
            </label>
            <input
              type="text"
              value={treatmentOwner}
              onChange={(e) => setTreatmentOwner(e.target.value)}
              placeholder="e.g. David Miller"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 18. Treatment/Mitigation Plan */}
          <div className="md:col-span-2 lg:col-span-2">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Treatment/Mitigation Plan
            </label>
            <textarea
              value={treatmentPlan}
              onChange={(e) => setTreatmentPlan(e.target.value)}
              rows={2}
              placeholder="E.g., detailed mitigation action plans..."
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 resize-y"
            />
          </div>

          {/* 19. Target Date */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Target Date
            </label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            />
          </div>

          {/* 20. Residual Likelihood Rating */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Residual Likelihood Rating
            </label>
            <select
              value={residualLikelihood ?? 0}
              onChange={(e) => setResidualLikelihood(parseInt(e.target.value))}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              {[0, 1, 2, 3, 4, 5, 6].map(val => (
                <option key={val} value={val}>{LIKELIHOOD_LABELS[val]}</option>
              ))}
            </select>
          </div>

          {/* 21. Residual Consequence Rating */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Residual Consequence Rating
            </label>
            <select
              value={residualConsequence ?? 0}
              onChange={(e) => setResidualConsequence(parseInt(e.target.value))}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              {[0, 1, 2, 3, 4, 5, 6].map(val => (
                <option key={val} value={val}>{CONSEQUENCE_LABELS[val]}</option>
              ))}
            </select>
          </div>

          {/* 22. Residual risk */}
          <div className="bg-emerald-50 border border-emerald-100 p-2.5 rounded-lg flex items-center justify-between shadow-2xs">
            <div>
              <span className="block text-[10px] uppercase font-bold text-emerald-600 tracking-wider">
                Residual risk
              </span>
              <span className="text-xs font-bold text-slate-800 font-mono mt-0.5 block">
                Score: {residualRiskScore} / 25
              </span>
            </div>
            <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase shrink-0 ${RISK_LEVEL_COLORS[residualRiskLevel].bg} ${RISK_LEVEL_COLORS[residualRiskLevel].text} ${RISK_LEVEL_COLORS[residualRiskLevel].border}`}>
              {residualRiskLevel}
            </span>
          </div>

          {/* 23. Date Raised */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Date Raised
            </label>
            <input
              type="date"
              value={dateRaised}
              onChange={(e) => setDateRaised(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            />
          </div>

          {/* 24. Date Closed */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Date Closed
            </label>
            <input
              type="date"
              value={dateClosed}
              onChange={(e) => setDateClosed(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            />
          </div>

          {/* 25. Risk Last Updated */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Risk Last Updated
            </label>
            <input
              type="date"
              value={riskLastUpdated}
              onChange={(e) => setRiskLastUpdated(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            />
          </div>

          {/* 26. Comments */}
          <div className="md:col-span-2 lg:col-span-3">
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Comments
            </label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              rows={2}
              placeholder="Enter additional governance comments or review logs"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 resize-y"
            />
          </div>

          {/* 27. Protected Issue/Risk */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Protected Issue/Risk
            </label>
            <select
              value={protectedIssueRisk}
              onChange={(e) => setProtectedIssueRisk(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="No">No</option>
              <option value="Yes">Yes</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* 28. DPE Ref Number */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              DPE Ref Number
            </label>
            <input
              type="text"
              value={dpeRefNumber}
              onChange={(e) => setDpeRefNumber(e.target.value)}
              placeholder="e.g. DPE-101"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 29. Timelines */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Timelines
            </label>
            <input
              type="text"
              value={timelines}
              onChange={(e) => setTimelines(e.target.value)}
              placeholder="e.g. Q3 2026"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 30. SIgn-Off Requirement */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              SIgn-Off Requirement
            </label>
            <select
              value={signOffRequirement}
              onChange={(e) => setSignOffRequirement(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="No">No</option>
              <option value="Yes">Yes</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* 31. Executive Status */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Executive Status
            </label>
            <select
              value={executiveStatus}
              onChange={(e) => setExecutiveStatus(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="Pending">Pending</option>
              <option value="Under Review">Under Review</option>
              <option value="Approved">Approved</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* 32. Next Mitigation Due date */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Next Mitigation Due date
            </label>
            <input
              type="date"
              value={nextMitigationDueDate}
              onChange={(e) => setNextMitigationDueDate(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            />
          </div>

          {/* 33. Mitigation Status */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Mitigation Status
            </label>
            <select
              value={mitigationStatus}
              onChange={(e) => setMitigationStatus(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Complete">Complete</option>
              <option value="Delayed">Delayed</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* 34. Strategy */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer"
            >
              <option value="Mitigate">Mitigate</option>
              <option value="Avoid">Avoid</option>
              <option value="Transfer">Transfer</option>
              <option value="Accept">Accept</option>
              <option value="N/A">N/A</option>
              <option value="No Data">No Data</option>
              <option value="-">-</option>
              <option value=" "> (Blank)</option>
            </select>
          </div>

          {/* 35. Who Raised */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Who Raised
            </label>
            <input
              type="text"
              value={whoRaised}
              onChange={(e) => setWhoRaised(e.target.value)}
              placeholder="e.g. Sarah Jenkins"
              className="w-full text-xs p-2.5 bg-white border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* 36. Open Days */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Open Days
            </label>
            <div className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 font-mono font-bold shadow-2xs">
              {calculateOpenDays(dateRaised, status === 'Closed' ? dateClosed : undefined)}
            </div>
          </div>

        </div>

        {/* Form Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-slate-100 pt-5 mt-6">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 rounded-lg border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50 cursor-pointer transition-colors"
          >
            Cancel
          </button>
          
          <button
            type="submit"
            className="flex items-center gap-1.5 px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold cursor-pointer shadow-xs transition-colors"
          >
            <Save className="w-4 h-4" />
            {editingTicket ? 'Update Risk' : 'Save Risk'}
          </button>
        </div>
      </div>
    </form>
  );
}
