/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo, useEffect } from 'react';
import { RiskTicket, IssueTicket, RISK_LEVEL_COLORS, isDriverTreeRefMatch } from '../types';
import { 
  GitBranch, 
  ShieldAlert, 
  AlertCircle, 
  ChevronRight, 
  ChevronLeft,
  ChevronDown, 
  Search, 
  ExternalLink,
  FolderTree,
  Calendar,
  User,
  List,
  Clock,
  Briefcase,
  Edit2,
  Plus,
  RotateCcw,
  X,
  Save,
  Check,
  Trash2,
  BellRing,
  CheckCircle2,
  BarChart3,
  TrendingUp,
  Layers,
  Siren,
  Filter
} from 'lucide-react';

interface CD1DriverTreeProps {
  tickets: RiskTicket[];
  issues: IssueTicket[];
  onSelectRisk?: (ticketId: string) => void;
  onSelectIssue?: (issueId: string) => void;
  onFilterLedgerByDriverRef?: (driverRef: string) => void;
  onFilterIssuesByDriverRef?: (driverRef: string) => void;
}

export interface CD1DriverItem {
  id: string;
  itemNumber: string;
  description: string;
  completeBy: string;
  owner: string;
  category: string;
  groupCode: string;
}

// Official CD1 Master Specification Items in Exact Sequence requested by User
export const INITIAL_CD1_ITEMS: CD1DriverItem[] = [
  // 1.x Cluster
  { id: 'cd1-1.1', itemNumber: '1.1', description: 'Program Mobilisation', completeBy: 'May 2026', owner: 'Team Google', category: 'Mobilisation', groupCode: 'CD1.1' },
  { id: 'cd1-1.10a', itemNumber: '1.10a', description: 'Infrastructure initialised- GDC Enterprise EE E.01 (Test/Dev) by Month (3.5) to Cloud Sves', completeBy: 'April 2026', owner: 'Darrl James/Grae Noble/ Team Google', category: 'Enterprise Platform', groupCode: 'CD1.1' },
  { id: 'cd1-1.10b', itemNumber: '1.10b', description: 'Platform Ready Test/Dev- GDC Enterprise EE E.01 (Test/Dev) Celivered by Month 6.5 to Ensibling Sves', completeBy: 'August 2026', owner: 'Darrl James/Grae Noble/ Team Google', category: 'Enterprise Platform', groupCode: 'CD1.1' },
  { id: 'cd1-1.10c', itemNumber: '1.10c', description: 'Environment Ready - GDC Enterprise E.O1(Test/Dev) platform exci. end-state', completeBy: 'End-state config by Month', owner: 'Team Google', category: 'Enterprise Platform', groupCode: 'CD1.1' },
  { id: 'cd1-1.10d', itemNumber: '1.10d', description: 'Mision Support Deplyment Ready E.O1(Test/Dev) platform excl end-state', completeBy: 'End-state config by Month', owner: 'Team Google', category: 'Enterprise Platform', groupCode: 'CD1.1' },
  { id: 'cd1-1.13', itemNumber: '1.13', description: 'Milestone 2- Internal Baseline Review (IBR) achieved, IMS Baselined and SOR', completeBy: 'August 2026', owner: 'Team Google/ Tim Minion', category: 'Milestones', groupCode: 'CD1.1' },
  { id: 'cd1-1.14', itemNumber: '1.14', description: 'Achievement of Systems Requirements Review (SRR)', completeBy: 'August September 2026', owner: 'Team Google/ Tim Minion', category: 'Milestones', groupCode: 'CD1.1' },
  { id: 'cd1-1.15', itemNumber: '1.15', description: 'Milestone 3- TiS Plan, Integrated Support Plan and Preliminary Design Review (PDR)', completeBy: 'November 2026', owner: 'Team Google', category: 'Milestones', groupCode: 'CD1.1' },
  { id: 'cd1-1.16c', itemNumber: '1.16c', description: 'API Gateway WIE Core Platform', completeBy: 'January 2027', owner: 'Team Google', category: 'WIE Platform', groupCode: 'CD1.1' },
  { id: 'cd1-1.17', itemNumber: '1.17', description: 'Mission Support System SIT in F-DSE Dev/Test Environment', completeBy: 'January 2027', owner: 'Team Google', category: 'Testing & Integration', groupCode: 'CD1.1' },
  { id: 'cd1-1.2', itemNumber: '1.2', description: 'Enduring POAA ATL Workforce', completeBy: 'July 2026', owner: 'Ash Sharma/Adam Flint', category: 'Workforce', groupCode: 'CD1.1' },
  { id: 'cd1-1.2a', itemNumber: '1.2a', description: 'Delivery of Milestone 1 artefacts (SRP, VSV, IMS)', completeBy: 'May 2026', owner: 'Team Google', category: 'Milestones', groupCode: 'CD1.1' },
  { id: 'cd1-1.2b', itemNumber: '1.2b', description: 'Commonwealth Acceptance of Milestone 1 artefacts (SRP, VGV, IMS)', completeBy: 'May-July 2026', owner: 'COL Tim Minion/ Adam Flint', category: 'Milestones', groupCode: 'CD1.1' },
  { id: 'cd1-1.3', itemNumber: '1.3', description: 'GFF: W.10 Facilities and Connectivity ready', completeBy: 'July 2026', owner: 'Aron Ward/Team Google', category: 'Facilities & Connectivity', groupCode: 'CD1.1' },
  { id: 'cd1-1.4', itemNumber: '1.4', description: 'GFF: W.11 Faclities and Connectivity ready', completeBy: 'September 2026', owner: 'Aron Ward/Team Google', category: 'Facilities & Connectivity', groupCode: 'CD1.1' },
  { id: 'cd1-1.5', itemNumber: '1.5', description: 'GFSw: Critical Software ready', completeBy: 'May-July 2026', owner: 'Glenn Powell/ Team Google', category: 'Critical Software', groupCode: 'CD1.1' },
  { id: 'cd1-1.6', itemNumber: '1.6', description: 'GFF: E.01/E.02 Facilities and Connectivity', completeBy: 'July-August 2026', owner: 'Aron Ward/Team Google', category: 'Facilities & Connectivity', groupCode: 'CD1.1' },
  { id: 'cd1-1.7', itemNumber: '1.7', description: 'Final delivery of OFFICIAL Landing Zone', completeBy: 'April 2026', owner: 'Darrl James/Grae Noble/ Team Google', category: 'Cloud Infrastructure', groupCode: 'CD1.1' },
  { id: 'cd1-1.7a', itemNumber: '1.7a', description: 'DevSecOps (O) Core', completeBy: 'August 2026', owner: 'Team Google', category: 'DevSecOps', groupCode: 'CD1.1' },
  { id: 'cd1-1.7b', itemNumber: '1.7b', description: 'GCP environment', completeBy: 'June 2026', owner: 'Team Google', category: 'Cloud Infrastructure', groupCode: 'CD1.1' },
  { id: 'cd1-1.7c', itemNumber: '1.7c', description: 'GCP ATO-C', completeBy: 'July 2026', owner: 'Team Google/Daryl James', category: 'Security & Accreditation', groupCode: 'CD1.1' },

  // 2.x Cluster
  { id: 'cd1-2.0', itemNumber: '2.0', description: 'Infrastructure Initialised- H - W.01 11 Fixed (Base) for CD/Factory/Training /SOC', completeBy: 'June 2026', owner: 'Team Google', category: 'Fixed Base Infrastructure', groupCode: 'CD1.2' },
  { id: 'cd1-2.1', itemNumber: '2.1', description: 'JC2NET Operating Model', completeBy: 'June 2026', owner: 'Rachel Keith/ A.Davie, CAPT(N) Greg Davidson', category: 'Operating Model', groupCode: 'CD1.2' },
  { id: 'cd1-2.2', itemNumber: '2.2', description: 'Platform Ready- H - W.01 T1 Fixed (Base) for CD1/Factory/Trairing /SOC', completeBy: 'September 2026', owner: 'Team Google', category: 'Fixed Base Infrastructure', groupCode: 'CD1.2' },
  { id: 'cd1-2.3', itemNumber: '2.3', description: 'Environment Ready-H - W.O1 T1 Fixed (Base) for CD1, Factory, Training & SOC', completeBy: 'Month 12 January 2027', owner: 'Team Google', category: 'Fixed Base Infrastructure', groupCode: 'CD1.2' },
  { id: 'cd1-2.4', itemNumber: '2.4', description: 'Mission Support Deployment Ready-H - W.01 T1 Fored (Base) for CD1 (Non-Prod)', completeBy: 'Month 16 May 2027', owner: 'Team Google', category: 'Fixed Base Infrastructure', groupCode: 'CD1.2' },

  // 3.x Cluster
  { id: 'cd1-3.1', itemNumber: '3.1', description: 'Delivery of Application Discovery Report of priority apps, interfaces and information flows', completeBy: 'July 2026', owner: 'Team Google', category: 'App Discovery', groupCode: 'CD1.3' },
  { id: 'cd1-3.2', itemNumber: '3.2', description: 'Completion of High-Level Migration Plan, Migration strategy and roadmap', completeBy: 'December 2026', owner: 'Team Google', category: 'Migration Roadmap', groupCode: 'CD1.3' },

  // 4.x Cluster
  { id: 'cd1-4.0', itemNumber: '4.0', description: 'ATO-C of WIE Components for CD1', completeBy: 'January 2027', owner: 'Team Google', category: 'Security & ATO', groupCode: 'CD1.4' },
  { id: 'cd1-4.1', itemNumber: '4.1', description: 'Security Assessors - Provision of embedded assessors', completeBy: 'March 2026', owner: 'Team Google', category: 'Security & Assessment', groupCode: 'CD1.4' },
  { id: 'cd1-4.2', itemNumber: '4.2', description: 'Establishment of WNA Production Representative Environment for CD1', completeBy: 'February 2027', owner: 'Team Google', category: 'WNA Platform', groupCode: 'CD1.4' },
  { id: 'cd1-4.3', itemNumber: '4.3', description: 'ATO of WNA Network Operations Center', completeBy: 'December 2026', owner: 'Team Google', category: 'Network Operations', groupCode: 'CD1.4' },
  { id: 'cd1-4.4', itemNumber: '4.4', description: 'WIE Identity Build Ready', completeBy: 'February 2027', owner: 'Team Google', category: 'Identity & Access', groupCode: 'CD1.4' },

  // 5.x Cluster
  { id: 'cd1-5.1', itemNumber: '5.1', description: 'JWCU Resourcing Complete', completeBy: 'February 2027', owner: 'JP9111 CM/Rachel Keith', category: 'Resourcing', groupCode: 'CD1.5' },
  { id: 'cd1-5.2', itemNumber: '5.2', description: 'WNA Support System ready for release (Training) to JCG Operations', completeBy: 'February 2027', owner: 'Team Google', category: 'Support Systems', groupCode: 'CD1.5' },
  { id: 'cd1-5.2a', itemNumber: '5.2a', description: 'Initial Support System Service Management build', completeBy: 'February 2027', owner: 'Team Google', category: 'Service Management', groupCode: 'CD1.5' },
  { id: 'cd1-5.3', itemNumber: '5.3', description: 'Roll-out of training to 50 WNA Support System users', completeBy: 'February - August 2027', owner: 'Team Google', category: 'Training & Rollout', groupCode: 'CD1.5' }
];

const LOCAL_STORAGE_KEY = 'cd1_driver_tree_items_v2';

function getSmoothPath(points: { x: number; y: number }[], tension = 0.25): string {
  if (points.length === 0) return '';
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
  if (points.length === 2) return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;

  let d = `M ${points[0].x.toFixed(1)} ${points[0].y.toFixed(1)}`;

  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i === 0 ? i : i - 1];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2 < points.length ? i + 2 : i + 1];

    const cp1x = p1.x + (p2.x - p0.x) * tension;
    const cp1y = p1.y + (p2.y - p0.y) * tension;
    const cp2x = p2.x - (p3.x - p1.x) * tension;
    const cp2y = p2.y - (p3.y - p1.y) * tension;

    d += ` C ${cp1x.toFixed(1)} ${cp1y.toFixed(1)}, ${cp2x.toFixed(1)} ${cp2y.toFixed(1)}, ${p2.x.toFixed(1)} ${p2.y.toFixed(1)}`;
  }

  return d;
}

export default function CD1DriverTree({
  tickets,
  issues,
  onSelectRisk,
  onSelectIssue,
  onFilterLedgerByDriverRef,
  onFilterIssuesByDriverRef
}: CD1DriverTreeProps) {
  // Items state with localStorage persistence
  const [driverItems, setDriverItems] = useState<CD1DriverItem[]>(() => {
    try {
      const saved = localStorage.getItem(LOCAL_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed;
        }
      }
    } catch (e) {
      console.error('Failed to parse saved driver tree items', e);
    }
    return INITIAL_CD1_ITEMS;
  });

  // Save changes to localStorage whenever driverItems updates
  useEffect(() => {
    try {
      localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(driverItems));
    } catch (e) {
      console.error('Failed to save driver tree items', e);
    }
  }, [driverItems]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOwnerFilter, setSelectedOwnerFilter] = useState<string>('all');
  const [selectedItem, setSelectedItem] = useState<CD1DriverItem>(driverItems[0] || INITIAL_CD1_ITEMS[0]);
  const [viewMode, setViewMode] = useState<'tree' | 'table' | 'timeline'>('tree');
  const [timelineFilter, setTimelineFilter] = useState<'all' | 'risk_only'>('all');
  const [selectedMonthKey, setSelectedMonthKey] = useState<string | null>('2026-03');
  const [hoveredMonthKey, setHoveredMonthKey] = useState<string | null>(null);

  // Edit Modal State
  const [editingItem, setEditingItem] = useState<CD1DriverItem | null>(null);
  const [isNewItemModal, setIsNewItemModal] = useState(false);
  const [editForm, setEditForm] = useState<{
    itemNumber: string;
    description: string;
    completeBy: string;
    owner: string;
    category: string;
  }>({
    itemNumber: '',
    description: '',
    completeBy: '',
    owner: '',
    category: ''
  });

  // Keep selectedItem valid if list changes
  useEffect(() => {
    if (driverItems.length > 0) {
      const exists = driverItems.find(i => i.id === selectedItem?.id);
      if (!exists) {
        setSelectedItem(driverItems[0]);
      } else {
        setSelectedItem(exists);
      }
    }
  }, [driverItems, selectedItem]);

  // Open Edit Modal
  const handleOpenEditModal = (item: CD1DriverItem, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setEditingItem(item);
    setIsNewItemModal(false);
    setEditForm({
      itemNumber: item.itemNumber,
      description: item.description,
      completeBy: item.completeBy,
      owner: item.owner,
      category: item.category || 'Core Delivery'
    });
  };

  // Open Add Item Modal
  const handleOpenAddModal = () => {
    setEditingItem(null);
    setIsNewItemModal(true);
    setEditForm({
      itemNumber: '1.18',
      description: '',
      completeBy: '2026',
      owner: 'Team Google',
      category: 'Program Delivery'
    });
  };

  // Save Item Handler
  const handleSaveItem = () => {
    if (!editForm.itemNumber.trim() || !editForm.description.trim()) {
      alert('Please enter both Item Number and Description.');
      return;
    }

    if (isNewItemModal) {
      const newItem: CD1DriverItem = {
        id: `cd1-custom-${Date.now()}`,
        itemNumber: editForm.itemNumber.trim(),
        description: editForm.description.trim(),
        completeBy: editForm.completeBy.trim(),
        owner: editForm.owner.trim(),
        category: editForm.category.trim(),
        groupCode: `CD1.${editForm.itemNumber.split('.')[0] || '1'}`
      };
      setDriverItems(prev => [...prev, newItem]);
      setSelectedItem(newItem);
    } else if (editingItem) {
      const updatedItem: CD1DriverItem = {
        ...editingItem,
        itemNumber: editForm.itemNumber.trim(),
        description: editForm.description.trim(),
        completeBy: editForm.completeBy.trim(),
        owner: editForm.owner.trim(),
        category: editForm.category.trim()
      };
      setDriverItems(prev => prev.map(i => i.id === editingItem.id ? updatedItem : i));
      setSelectedItem(updatedItem);
    }

    setEditingItem(null);
    setIsNewItemModal(false);
  };

  // Delete Item Handler
  const handleDeleteItem = (id: string, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    if (confirm('Are you sure you want to remove this item from the CD1 Driver Tree?')) {
      setDriverItems(prev => prev.filter(i => i.id !== id));
      if (editingItem?.id === id) {
        setEditingItem(null);
      }
    }
  };

  // Reset to Default Order
  const handleResetToDefault = () => {
    if (confirm('Reset CD1 Driver Tree to the official master 37-item sequence? Any custom edits will be replaced.')) {
      setDriverItems(INITIAL_CD1_ITEMS);
      setSelectedItem(INITIAL_CD1_ITEMS[0]);
    }
  };

  // Unique owners for filter
  const availableOwners = useMemo(() => {
    const set = new Set<string>();
    driverItems.forEach(i => set.add(i.owner));
    return Array.from(set).sort();
  }, [driverItems]);

  // Tokenized matching logic for linking risks to a CD1 Driver item via 'driverTreeRef'
  const getLinkedRisks = (item: CD1DriverItem) => {
    const itemNum = item.itemNumber.trim();
    if (!itemNum) return [];
    return tickets.filter(t => isDriverTreeRefMatch(t.driverTreeRef, itemNum));
  };

  // Matching logic for linking issues to a CD1 Driver item via 'driverTreeRef'
  const getLinkedIssues = (item: CD1DriverItem) => {
    const itemNum = item.itemNumber.trim();
    if (!itemNum) return [];
    return issues.filter(i => isDriverTreeRefMatch(i.driverTreeRef, itemNum));
  };

  // Compute selected item stats
  const activeLinkedRisks = useMemo(() => getLinkedRisks(selectedItem), [selectedItem, tickets]);
  const activeLinkedIssues = useMemo(() => getLinkedIssues(selectedItem), [selectedItem, issues]);

  const criticalRisksCount = useMemo(() => {
    return activeLinkedRisks.filter(r => r.inherentRiskLevel === 'Critical' || r.inherentRiskLevel === 'Very High').length;
  }, [activeLinkedRisks]);

  // Filtered Items List preserving exact sequence
  const filteredItems = useMemo(() => {
    return driverItems.filter(item => {
      const matchSearch = !searchTerm || 
        item.itemNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.completeBy.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.owner.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category.toLowerCase().includes(searchTerm.toLowerCase());

      const matchOwner = selectedOwnerFilter === 'all' || item.owner === selectedOwnerFilter;
      return matchSearch && matchOwner;
    });
  }, [driverItems, searchTerm, selectedOwnerFilter]);

  // Group items by completion milestone date for Power BI Timeline View
  const timelineGroups = useMemo(() => {
    const groups: { [key: string]: CD1DriverItem[] } = {};
    filteredItems.forEach(item => {
      const milestone = item.completeBy.trim() || 'TBD / Ongoing';
      if (!groups[milestone]) {
        groups[milestone] = [];
      }
      groups[milestone].push(item);
    });
    return Object.entries(groups).map(([milestone, items]) => ({
      milestone,
      items
    }));
  }, [filteredItems]);

  // Power BI Timeline Month Range: Jan 2026 to Aug 2027 (20 Months)
  const TIMELINE_MONTHS = useMemo(() => [
    { label: 'Jan 2026', key: '2026-01', year: '2026', short: 'Jan 26' },
    { label: 'Feb 2026', key: '2026-02', year: '2026', short: 'Feb 26' },
    { label: 'Mar 2026', key: '2026-03', year: '2026', short: 'Mar 26' },
    { label: 'Apr 2026', key: '2026-04', year: '2026', short: 'Apr 26' },
    { label: 'May 2026', key: '2026-05', year: '2026', short: 'May 26' },
    { label: 'Jun 2026', key: '2026-06', year: '2026', short: 'Jun 26' },
    { label: 'Jul 2026', key: '2026-07', year: '2026', short: 'Jul 26' },
    { label: 'Aug 2026', key: '2026-08', year: '2026', short: 'Aug 26' },
    { label: 'Sep 2026', key: '2026-09', year: '2026', short: 'Sep 26' },
    { label: 'Oct 2026', key: '2026-10', year: '2026', short: 'Oct 26' },
    { label: 'Nov 2026', key: '2026-11', year: '2026', short: 'Nov 26' },
    { label: 'Dec 2026', key: '2026-12', year: '2026', short: 'Dec 26' },
    { label: 'Jan 2027', key: '2027-01', year: '2027', short: 'Jan 27' },
    { label: 'Feb 2027', key: '2027-02', year: '2027', short: 'Feb 27' },
    { label: 'Mar 2027', key: '2027-03', year: '2027', short: 'Mar 27' },
    { label: 'Apr 2027', key: '2027-04', year: '2027', short: 'Apr 27' },
    { label: 'May 2027', key: '2027-05', year: '2027', short: 'May 27' },
    { label: 'Jun 2027', key: '2027-06', year: '2027', short: 'Jun 27' },
    { label: 'Jul 2027', key: '2027-07', year: '2027', short: 'Jul 27' },
    { label: 'Aug 2027', key: '2027-08', year: '2027', short: 'Aug 27' },
  ], []);

  const parseMonthKey = (completeByStr: string, itemNumber: string): string => {
    const str = (completeByStr || '').toLowerCase();
    
    if (str.includes('jan') && str.includes('2026')) return '2026-01';
    if (str.includes('feb') && str.includes('2026')) return '2026-02';
    if (str.includes('mar') && str.includes('2026')) return '2026-03';
    if (str.includes('apr') && str.includes('2026')) return '2026-04';
    if (str.includes('may') && str.includes('2026')) return '2026-05';
    if (str.includes('jun') && str.includes('2026')) return '2026-06';
    if (str.includes('jul') && str.includes('2026')) return '2026-07';
    if (str.includes('aug') && str.includes('2026')) return '2026-08';
    if (str.includes('sep') && str.includes('2026')) return '2026-09';
    if (str.includes('oct') && str.includes('2026')) return '2026-10';
    if (str.includes('nov') && str.includes('2026')) return '2026-11';
    if (str.includes('dec') && str.includes('2026')) return '2026-12';

    if (str.includes('jan') && str.includes('2027')) return '2027-01';
    if (str.includes('feb') && str.includes('2027')) return '2027-02';
    if (str.includes('mar') && str.includes('2027')) return '2027-03';
    if (str.includes('apr') && str.includes('2027')) return '2027-04';
    if (str.includes('may') && str.includes('2027')) return '2027-05';
    if (str.includes('jun') && str.includes('2027')) return '2027-06';
    if (str.includes('jul') && str.includes('2027')) return '2027-07';
    if (str.includes('aug') && str.includes('2027')) return '2027-08';

    if (str.includes('q1') && str.includes('2026')) return '2026-03';
    if (str.includes('q2') && str.includes('2026')) return '2026-06';
    if (str.includes('q3') && str.includes('2026')) return '2026-09';
    if (str.includes('q4') && str.includes('2026')) return '2026-12';
    if (str.includes('q1') && str.includes('2027')) return '2027-03';
    if (str.includes('q2') && str.includes('2027')) return '2027-06';
    if (str.includes('q3') && str.includes('2027')) return '2027-08';

    let sum = 0;
    for (let i = 0; i < itemNumber.length; i++) {
      sum += itemNumber.charCodeAt(i);
    }
    const idx = sum % TIMELINE_MONTHS.length;
    return TIMELINE_MONTHS[idx].key;
  };

  const monthlyTimelineData = useMemo(() => {
    return TIMELINE_MONTHS.map(m => {
      const itemsInMonth = filteredItems.filter(item => {
        const key = parseMonthKey(item.completeBy, item.itemNumber);
        return key === m.key;
      });

      const displayItems = itemsInMonth.filter(item => {
        if (timelineFilter === 'risk_only') {
          return getLinkedRisks(item).length > 0;
        }
        return true;
      });

      const riskCount = itemsInMonth.filter(item => getLinkedRisks(item).length > 0).length;

      return {
        ...m,
        items: displayItems,
        allItemsInMonth: itemsInMonth,
        totalCount: itemsInMonth.length,
        riskCount
      };
    });
  }, [TIMELINE_MONTHS, filteredItems, timelineFilter, getLinkedRisks]);

  const maxMonthCount = useMemo(() => {
    return Math.max(1, ...monthlyTimelineData.map(m => m.totalCount));
  }, [monthlyTimelineData]);

  const renderPowerBITrendGraphTimeline = () => {
    const totalRisksCount = filteredItems.filter(i => getLinkedRisks(i).length > 0).length;
    const selectedMonthData = monthlyTimelineData.find(m => m.key === selectedMonthKey);
    const CURRENT_MONTH_KEY = '2026-07';

    const navigateMonth = (direction: number) => {
      if (!selectedMonthKey) {
        setSelectedMonthKey(TIMELINE_MONTHS[0].key);
        return;
      }
      const currIdx = TIMELINE_MONTHS.findIndex(m => m.key === selectedMonthKey);
      if (currIdx === -1) return;
      const nextIdx = (currIdx + direction + TIMELINE_MONTHS.length) % TIMELINE_MONTHS.length;
      setSelectedMonthKey(TIMELINE_MONTHS[nextIdx].key);
    };

    return (
      <div className="w-full bg-white text-slate-900 rounded-2xl p-5 border border-slate-200 shadow-md space-y-6">
        {/* Control Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl border border-blue-100 shadow-2xs">
              <BarChart3 className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2 font-mono">
                  CD1 Driver Tree and Risk Timeline
                </h3>
                <span className="px-2.5 py-0.5 text-[10px] font-bold font-mono bg-blue-50 text-blue-700 rounded-full border border-blue-200 uppercase tracking-wide">
                  Jan 2026 – Aug 2027
                </span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200 text-xs">
              <span className="text-slate-500 font-medium">Items Horizon:</span>
              <span className="font-mono font-bold text-slate-800">{filteredItems.length}</span>
            </div>

            <div className="flex items-center gap-2 bg-rose-50 px-3.5 py-1.5 rounded-xl border border-rose-200 text-xs shadow-2xs">
              <span className="text-rose-800 font-semibold">Flagged Risks:</span>
              <span className="font-mono font-extrabold text-rose-700 text-sm">{totalRisksCount}</span>
            </div>

            <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-medium border border-slate-200">
              <button
                type="button"
                onClick={() => setTimelineFilter('all')}
                className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
                  timelineFilter === 'all' ? 'bg-blue-600 text-white font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All Items
              </button>
              <button
                type="button"
                onClick={() => setTimelineFilter('risk_only')}
                className={`flex items-center gap-1 px-3 py-1 rounded-md transition-all cursor-pointer ${
                  timelineFilter === 'risk_only' ? 'bg-rose-600 text-white font-bold shadow-2xs' : 'text-slate-600 hover:text-rose-700'
                }`}
              >
                Risks Only
              </button>
            </div>
          </div>
        </div>

        {/* INTERACTIVE TREND GRAPH CONTAINER */}
        <div className="bg-slate-50/70 border border-slate-200/80 rounded-xl p-4 space-y-4">
          <div className="flex items-center justify-between text-xs font-mono border-b border-slate-200 pb-2">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-slate-700" />
              <span className="font-bold text-slate-800 uppercase tracking-wider">
                Interactive Deliverables Velocity &amp; Risk Curve
              </span>
            </div>
            <div className="flex items-center gap-4 text-[11px]">
              <span className="flex items-center gap-1.5 text-slate-700 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-blue-500/90 inline-block" />
                Deliverables Velocity
              </span>
              <span className="flex items-center gap-1.5 text-rose-700 font-bold">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
                🚨 Risk Exposure Volume
              </span>
              <span className="flex items-center gap-1.5 text-slate-600 font-bold border-l border-slate-200 pl-3">
                <span className="w-2 h-2 rounded-full bg-slate-500 inline-block" />
                Current Month (Jul '26)
              </span>
            </div>
          </div>

          {/* SVG Trend Graph Chart */}
          <div className="w-full overflow-x-auto no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
            <div className="min-w-[950px]">
              {/* Year Headers (2026 vs 2027) */}
              <div className="grid grid-cols-20 text-[11px] font-mono font-bold text-slate-600 text-center mb-1">
                <div className="col-span-12 bg-white py-1 rounded-l border border-slate-200/80 text-slate-700 font-black shadow-2xs">
                  2026 (Jan – Dec)
                </div>
                <div className="col-span-8 bg-white py-1 rounded-r border-t border-b border-r border-slate-200/80 text-purple-800/90 font-black shadow-2xs">
                  2027 (Jan – Aug)
                </div>
              </div>

              <div className="relative h-44 bg-white rounded-lg border border-slate-200/80 p-2 select-none shadow-2xs">
                <svg className="w-full h-full overflow-visible" viewBox="0 0 1000 150" preserveAspectRatio="none">
                  <defs>
                    <linearGradient id="blueTrendGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#2563eb" stopOpacity="0.14" />
                      <stop offset="100%" stopColor="#2563eb" stopOpacity="0.0" />
                    </linearGradient>
                    <linearGradient id="redTrendGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#e11d48" stopOpacity="0.12" />
                      <stop offset="100%" stopColor="#e11d48" stopOpacity="0.0" />
                    </linearGradient>
                  </defs>

                  {/* Horizontal Grid lines */}
                  <line x1="0" y1="20" x2="1000" y2="20" stroke="#f1f5f9" strokeDasharray="3 3" />
                  <line x1="0" y1="75" x2="1000" y2="75" stroke="#f1f5f9" strokeDasharray="3 3" />
                  <line x1="0" y1="130" x2="1000" y2="130" stroke="#cbd5e1" strokeWidth="1.5" />

                  {/* Month Vertical Guidelines and Active Column Highlights */}
                  {TIMELINE_MONTHS.map((m, i) => {
                    const cx = 25 + i * 50;
                    const isSel = m.key === selectedMonthKey;
                    const isHov = m.key === hoveredMonthKey;
                    const isCurrent = m.key === CURRENT_MONTH_KEY;

                    return (
                      <g key={m.key}>
                        {/* Background Highlight for Selected / Hovered / Current Month */}
                        {(isSel || isHov || isCurrent) && (
                          <rect
                            x={cx - 20}
                            y={10}
                            width={40}
                            height={120}
                            rx={8}
                            fill={
                              isSel
                                ? 'rgba(37, 99, 235, 0.08)'
                                : isCurrent
                                ? 'rgba(100, 116, 139, 0.06)'
                                : 'rgba(241, 245, 249, 0.8)'
                            }
                            stroke={isSel ? '#3b82f6' : isCurrent ? '#94a3b8' : '#e2e8f0'}
                            strokeWidth={isSel ? '1.5' : isCurrent ? '1.5' : '1'}
                            strokeDasharray={isCurrent && !isSel ? '3 3' : 'none'}
                          />
                        )}

                        {/* Vertical Line: Grey dashed line for Current Month */}
                        <line
                          x1={cx}
                          y1="10"
                          x2={cx}
                          y2="130"
                          stroke={isSel ? '#3b82f6' : isCurrent ? '#64748b' : '#f1f5f9'}
                          strokeWidth={isSel ? '1.5' : isCurrent ? '1.5' : '1'}
                          strokeDasharray={isCurrent ? '4 3' : isSel ? 'none' : '2 2'}
                          strokeOpacity={isSel || isCurrent ? '1' : '0.7'}
                        />

                        {/* Top Badge for Current Month */}
                        {isCurrent && (
                          <g transform={`translate(${cx}, 14)`}>
                            <rect x="-36" y="-10" width="72" height="16" rx="8" fill="#475569" />
                            <text x="0" y="2" textAnchor="middle" fill="#ffffff" fontSize="8.5" fontWeight="bold">
                              Jul '26 (Now)
                            </text>
                          </g>
                        )}
                      </g>
                    );
                  })}

                  {/* Smooth Area & Line paths for Deliverables & Risks */}
                  {monthlyTimelineData.length > 0 && (() => {
                    const totalPoints = monthlyTimelineData.map((m, i) => ({
                      x: 25 + i * 50,
                      y: 130 - (m.totalCount / maxMonthCount) * 95
                    }));
                    const riskPoints = monthlyTimelineData.map((m, i) => ({
                      x: 25 + i * 50,
                      y: 130 - (m.riskCount / maxMonthCount) * 95
                    }));

                    const totalLine = getSmoothPath(totalPoints, 0.25);
                    const totalArea = totalPoints.length > 0
                      ? `${totalLine} L ${totalPoints[totalPoints.length - 1].x} 130 L ${totalPoints[0].x} 130 Z`
                      : '';

                    const riskLine = getSmoothPath(riskPoints, 0.25);
                    const riskArea = riskPoints.length > 0
                      ? `${riskLine} L ${riskPoints[riskPoints.length - 1].x} 130 L ${riskPoints[0].x} 130 Z`
                      : '';

                    return (
                      <>
                        <path d={totalArea} fill="url(#blueTrendGrad)" />
                        <path
                          d={totalLine}
                          fill="none"
                          stroke="#2563eb"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                        <path d={riskArea} fill="url(#redTrendGrad)" />
                        <path
                          d={riskLine}
                          fill="none"
                          stroke="#e11d48"
                          strokeWidth="2.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </>
                    );
                  })()}

                  {/* Interactive Nodes & Overlay Hitboxes */}
                  {monthlyTimelineData.map((m, i) => {
                    const cx = 25 + i * 50;
                    const itemsY = 130 - (m.totalCount / maxMonthCount) * 95;
                    const risksY = 130 - (m.riskCount / maxMonthCount) * 95;
                    const isSel = m.key === selectedMonthKey;
                    const isHov = m.key === hoveredMonthKey;
                    const isCurrent = m.key === CURRENT_MONTH_KEY;

                    return (
                      <g key={m.key} className="cursor-pointer">
                        {/* Highlight Current Month with White Inner Circle and Muted Blue Outline */}
                        {isCurrent && (
                          <circle
                            cx={cx}
                            cy={itemsY}
                            r={isSel ? 8 : isHov ? 7.5 : 7}
                            fill="#ffffff"
                            stroke="#2563eb"
                            strokeWidth="2"
                          />
                        )}

                        {/* Regular Items Node (if not current month) */}
                        {!isCurrent && (
                          <circle
                            cx={cx}
                            cy={itemsY}
                            r={isSel ? 5.5 : isHov ? 5 : 4}
                            fill={isSel ? '#1d4ed8' : '#2563eb'}
                            stroke="#ffffff"
                            strokeWidth={isSel ? 2 : 1.5}
                          />
                        )}

                        {/* Risk Node if riskCount > 0 */}
                        {m.riskCount > 0 && (
                          <g>
                            <circle
                              cx={cx}
                              cy={risksY}
                              r={isSel ? 6 : isHov ? 5 : 4}
                              fill="#e11d48"
                              stroke="#ffffff"
                              strokeWidth="1.5"
                            />
                            <text x={cx} y={risksY - 9} textAnchor="middle" fill="#be123c" fontSize="9" fontWeight="bold">
                              🚨{m.riskCount}
                            </text>
                          </g>
                        )}

                        {/* Hover Tooltip Box on Chart */}
                        {isHov && (
                          <g transform={`translate(${Math.min(850, Math.max(100, cx - 60))}, ${Math.max(15, itemsY - 45)})`}>
                            <rect x="0" y="0" width="120" height="34" rx="6" fill="#ffffff" stroke="#2563eb" strokeWidth="1.5" className="shadow-md" />
                            <text x="60" y="14" textAnchor="middle" fill="#1e293b" fontSize="10" fontWeight="bold">
                              {m.label} {isCurrent ? '(Now)' : ''}
                            </text>
                            <text x="60" y="27" textAnchor="middle" fill="#64748b" fontSize="9">
                              {m.totalCount} Items • {m.riskCount} Risks 🚨
                            </text>
                          </g>
                        )}

                        {/* Invisible Full Height Hitbox for Click/Hover */}
                        <rect
                          x={cx - 24}
                          y={0}
                          width={48}
                          height={150}
                          fill="rgba(0,0,0,0)"
                          style={{ pointerEvents: 'all' }}
                          className="cursor-pointer"
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedMonthKey(isSel ? null : m.key);
                          }}
                          onMouseEnter={() => setHoveredMonthKey(m.key)}
                          onMouseLeave={() => setHoveredMonthKey(null)}
                        />
                      </g>
                    );
                  })}
                </svg>
              </div>

              {/* Interactive Month Axis Buttons (Jan 2026 to Aug 2027) */}
              <div className="grid grid-cols-20 gap-1 text-[10px] font-mono font-bold text-center pt-2">
                {monthlyTimelineData.map((m) => {
                  const isSel = m.key === selectedMonthKey;
                  const isHov = m.key === hoveredMonthKey;
                  const isCurrent = m.key === CURRENT_MONTH_KEY;

                  return (
                    <button
                      key={m.key}
                      type="button"
                      onClick={() => setSelectedMonthKey(isSel ? null : m.key)}
                      onMouseEnter={() => setHoveredMonthKey(m.key)}
                      onMouseLeave={() => setHoveredMonthKey(null)}
                      className={`py-1.5 px-0.5 rounded-lg transition-all cursor-pointer truncate font-mono text-[10px] font-bold ${
                        isSel
                          ? 'bg-blue-600 text-white font-extrabold shadow-md ring-2 ring-blue-400 scale-105'
                          : isCurrent
                          ? 'bg-slate-700 text-white font-extrabold ring-2 ring-slate-400 shadow-xs'
                          : isHov
                          ? 'bg-slate-200 text-slate-900 border border-slate-300'
                          : m.riskCount > 0
                          ? 'bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100'
                          : m.year === '2027'
                          ? 'bg-white text-purple-700 border border-slate-200 hover:bg-slate-100'
                          : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-100'
                      }`}
                      title={`Click to filter deliverables for ${m.label} (${m.totalCount} Items, ${m.riskCount} Risks)`}
                    >
                      {m.short} {isCurrent ? '📍' : m.riskCount > 0 ? '🚨' : ''}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        {/* INTERACTIVE DRILL-DOWN DASHBOARD PANEL FOR SELECTED MONTH */}
        {selectedMonthData ? (
          <div className="bg-white border-2 border-blue-500 rounded-xl p-5 space-y-4 shadow-lg transition-all">
            {/* Header / Nav Bar for Selected Month */}
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-200">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-600 text-white rounded-lg shadow-xs">
                  <Calendar className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-black text-slate-900 uppercase tracking-wider font-mono">
                      {selectedMonthData.label} Deliverables Drill-Down
                    </h4>
                    <span className="px-2 py-0.5 text-[10px] font-bold font-mono bg-blue-50 text-blue-700 rounded border border-blue-200">
                      {selectedMonthData.items.length} Item{selectedMonthData.items.length !== 1 ? 's' : ''}
                    </span>
                    {selectedMonthData.riskCount > 0 && (
                      <span className="px-2 py-0.5 text-[10px] font-bold font-mono bg-rose-50 text-rose-700 rounded border border-rose-200 flex items-center gap-1">
                        {selectedMonthData.riskCount} Flagged Risk{selectedMonthData.riskCount !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Month Switcher Controls */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => navigateMonth(-1)}
                  className="p-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 cursor-pointer transition-all flex items-center gap-1 text-xs font-semibold"
                  title="Previous Month"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Prev</span>
                </button>

                <button
                  type="button"
                  onClick={() => navigateMonth(1)}
                  className="p-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 cursor-pointer transition-all flex items-center gap-1 text-xs font-semibold"
                  title="Next Month"
                >
                  <span>Next</span>
                  <ChevronRight className="w-4 h-4" />
                </button>

                <button
                  type="button"
                  onClick={() => setSelectedMonthKey(null)}
                  className="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg border border-slate-200 cursor-pointer text-xs font-bold transition-all flex items-center gap-1"
                >
                  <X className="w-3.5 h-3.5 text-slate-500" />
                  Close Drill-Down
                </button>
              </div>
            </div>

            {/* Grid of Items for Selected Month */}
            {selectedMonthData.items.length === 0 ? (
              <div className="p-8 text-center bg-slate-50 rounded-xl border border-dashed border-slate-300 space-y-2">
                <Calendar className="w-8 h-8 text-slate-400 mx-auto" />
                <p className="text-sm font-semibold text-slate-600">
                  No deliverables matching current filters scheduled in {selectedMonthData.label}.
                </p>
                {timelineFilter === 'risk_only' && (
                  <button
                    type="button"
                    onClick={() => setTimelineFilter('all')}
                    className="mt-2 px-3 py-1 bg-blue-600 text-white rounded-lg text-xs font-bold cursor-pointer hover:bg-blue-700"
                  >
                    Switch to "All Items"
                  </button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedMonthData.items.map(item => {
                  const linkedRisks = getLinkedRisks(item);
                  const linkedIssues = getLinkedIssues(item);
                  const hasRisks = linkedRisks.length > 0;
                  const hasIssues = linkedIssues.length > 0;
                  const isSelected = selectedItem?.id === item.id;

                  return (
                    <div
                      key={item.id}
                      onClick={() => setSelectedItem(item)}
                      className={`p-4 rounded-xl transition-all cursor-pointer flex flex-col justify-between gap-3 ${
                        isSelected
                          ? 'bg-indigo-50 border-2 border-indigo-600 ring-4 ring-indigo-400/40 text-slate-900 shadow-md scale-[1.01]'
                          : hasRisks
                          ? 'bg-rose-50/70 border-2 border-rose-300 text-slate-900 hover:bg-rose-100/70 hover:border-rose-400 shadow-xs'
                          : 'bg-white border border-slate-200 hover:border-blue-300 hover:bg-slate-50/50 text-slate-800 shadow-2xs'
                      }`}
                    >
                      <div className="flex items-center justify-between gap-2 flex-wrap">
                        <div className="flex items-center gap-1.5">
                          <span className={`font-mono text-xs font-black px-2.5 py-0.5 rounded-md ${
                            hasRisks ? 'bg-rose-600 text-white' : 'bg-blue-600 text-white'
                          }`}>
                            Ref {item.itemNumber}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5">
                          {hasRisks && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedItem(item);
                                if (onFilterLedgerByDriverRef) {
                                  onFilterLedgerByDriverRef(item.itemNumber);
                                } else if (onSelectRisk && linkedRisks[0]) {
                                  onSelectRisk(linkedRisks[0].id);
                                }
                              }}
                              className="flex items-center gap-1 bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-2xs cursor-pointer active:scale-95 transition-all"
                              title={`Filter Risk Register for Ref ${item.itemNumber} (${linkedRisks.length} Risk${linkedRisks.length > 1 ? 's' : ''})`}
                            >
                              <Siren className="w-3 h-3 text-white" />
                              <span>{linkedRisks.length} Risk{linkedRisks.length > 1 ? 's' : ''}</span>
                              <ExternalLink className="w-2.5 h-2.5 opacity-90" />
                            </button>
                          )}

                          {hasIssues && (
                            <button
                              type="button"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedItem(item);
                                if (onFilterIssuesByDriverRef) {
                                  onFilterIssuesByDriverRef(item.itemNumber);
                                } else if (onSelectIssue && linkedIssues[0]) {
                                  onSelectIssue(linkedIssues[0].id);
                                }
                              }}
                              className="flex items-center gap-1 bg-amber-600 hover:bg-amber-700 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-2xs cursor-pointer active:scale-95 transition-all"
                              title={`Filter Issue Dashboard for Ref ${item.itemNumber} (${linkedIssues.length} Issue${linkedIssues.length > 1 ? 's' : ''})`}
                            >
                              <AlertCircle className="w-3 h-3 text-white" />
                              <span>{linkedIssues.length} Issue{linkedIssues.length > 1 ? 's' : ''}</span>
                              <ExternalLink className="w-2.5 h-2.5 opacity-90" />
                            </button>
                          )}

                          {!hasRisks && !hasIssues && (
                            <span className="flex items-center gap-1 text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full font-semibold">
                              <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                              Clear
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="text-xs font-bold leading-relaxed line-clamp-3 text-slate-800">
                        {item.description}
                      </div>

                      <div className={`flex items-center justify-between pt-2 border-t text-[11px] font-medium ${
                        hasRisks ? 'border-rose-200 text-rose-800' : 'border-slate-100 text-slate-500'
                      }`}>
                        <span className="flex items-center gap-1 truncate max-w-[140px]">
                          <User className={`w-3.5 h-3.5 ${hasRisks ? 'text-rose-600' : 'text-blue-600'}`} />
                          {item.owner}
                        </span>
                        <span className="font-mono text-[10px] opacity-90">
                          {item.completeBy}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ) : (
          /* Prompt banner when no month is selected */
          <div className="space-y-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-center text-slate-700 flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2 text-xs font-mono text-blue-700 font-bold">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span>Click any month node or column in the timeline graph above to inspect month deliverables</span>
              </div>
              <button
                type="button"
                onClick={() => setSelectedMonthKey('2026-03')}
                className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-bold cursor-pointer transition-all shadow-2xs"
              >
                Open March 2026 Drill-Down
              </button>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div id="cd1-driver-tree-container" className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 rounded-2xl p-6 text-white shadow-lg border border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold uppercase tracking-wider">
                Capability Drop 1 (CD1) Architecture
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
              <GitBranch className="w-6 h-6 text-indigo-400" />
              Driver Tree for Capability Drop 1 (CD1)
            </h2>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-start md:self-auto shrink-0">
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-md p-3.5 rounded-xl border border-white/10">
              <div className="text-center px-2 border-r border-white/10">
                <div className="text-xl font-mono font-black text-white">{driverItems.length}</div>
                <div className="text-[10px] text-indigo-200 font-medium">Driver Items</div>
              </div>
              <div className="text-center px-2 border-r border-white/10">
                <div className="text-xl font-mono font-black text-emerald-400">{tickets.length}</div>
                <div className="text-[10px] text-slate-300 font-medium">Mapped Risks</div>
              </div>
              <div className="text-center px-2">
                <div className="text-xl font-mono font-black text-amber-300">{issues.length}</div>
                <div className="text-[10px] text-slate-300 font-medium">Issues</div>
              </div>
            </div>

            <button
              type="button"
              onClick={handleOpenAddModal}
              className="px-3.5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs rounded-xl flex items-center gap-1.5 cursor-pointer shadow-md transition-all"
            >
              <Plus className="w-4 h-4" />
              Add Item
            </button>
            <button
              type="button"
              onClick={handleResetToDefault}
              title="Reset to default sequence"
              className="px-3 py-2.5 bg-white/10 hover:bg-white/20 text-slate-200 font-medium text-xs rounded-xl flex items-center gap-1.5 cursor-pointer border border-white/10 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Order
            </button>
          </div>
        </div>
      </div>

      {/* POWER BI STYLE TREND GRAPH & TIMELINE VIEW SECTION (CD1 Driver Tree and Risk Timeline) */}
      {renderPowerBITrendGraphTimeline()}

      {/* Control Bar: Search, Owner Filter, View Mode Toggle */}
      <div className="bg-white border border-slate-200/80 rounded-xl p-3.5 shadow-2xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          {/* Search Bar */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search item number (e.g. 1.10a), description, owner..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full text-xs pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500"
            />
          </div>

          {/* Owner Filter */}
          <div className="flex items-center gap-1.5 text-xs">
            <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <select
              value={selectedOwnerFilter}
              onChange={(e) => setSelectedOwnerFilter(e.target.value)}
              className="text-xs p-1.5 px-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-indigo-500 cursor-pointer max-w-[200px]"
            >
              <option value="all">All Assigned Leads / Owners</option>
              {availableOwners.map(owner => (
                <option key={owner} value={owner}>{owner}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex bg-slate-100 p-0.5 rounded-lg text-[11px] font-medium">
            <button
              type="button"
              onClick={() => setViewMode('tree')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md cursor-pointer transition-all ${
                viewMode === 'tree' ? 'bg-white text-indigo-700 font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FolderTree className="w-3.5 h-3.5" />
              Sequential List
            </button>
            <button
              type="button"
              onClick={() => setViewMode('table')}
              className={`flex items-center gap-1.5 px-3 py-1 rounded-md cursor-pointer transition-all ${
                viewMode === 'table' ? 'bg-white text-indigo-700 font-bold shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <List className="w-3.5 h-3.5" />
              Table View
            </button>
          </div>
        </div>
      </div>

      {/* Content Layout: Full Width CD1 Driver Sequence */}
      <div className="w-full bg-white border border-slate-200/80 rounded-2xl p-5 shadow-xs flex flex-col space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-800">
                CD1 Driver Tree ({filteredItems.length} Items)
              </h3>
            </div>
          </div>

          {viewMode === 'table' ? (
            /* Table View Layout */
            <div className="overflow-x-auto overflow-y-auto max-h-[680px] border border-slate-200 rounded-xl no-scrollbar [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
              <table className="w-full text-left text-xs text-slate-700">
                <thead className="bg-slate-50 text-[11px] font-bold text-slate-600 uppercase tracking-wider sticky top-0 border-b border-slate-200">
                  <tr>
                    <th className="p-3 w-20">Item #</th>
                    <th className="p-3">Description</th>
                    <th className="p-3 w-32">Complete By</th>
                    <th className="p-3 w-44">Assigned Person (Column 1)</th>
                    <th className="p-3 w-24 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredItems.map(item => {
                    const isSelected = selectedItem.id === item.id;
                    const linkedRisks = getLinkedRisks(item);
                    const linkedIssues = getLinkedIssues(item);

                    return (
                      <tr
                        key={item.id}
                        onClick={() => setSelectedItem(item)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-indigo-50/90 font-medium' : 'hover:bg-slate-50'
                        }`}
                      >
                        <td className="p-3 font-mono font-extrabold text-indigo-700 whitespace-nowrap">
                          {item.itemNumber}
                        </td>
                        <td className="p-3 text-slate-900 font-semibold leading-snug">
                          {item.description}
                        </td>
                        <td className="p-3 text-slate-600 whitespace-nowrap">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3 text-emerald-600 shrink-0" />
                            {item.completeBy}
                          </span>
                        </td>
                        <td className="p-3 text-slate-700 font-medium">
                          <span className="flex items-center gap-1">
                            <User className="w-3 h-3 text-indigo-500 shrink-0" />
                            {item.owner}
                          </span>
                        </td>
                        <td className="p-3 text-right whitespace-nowrap">
                          <div className="flex items-center justify-end gap-1.5">
                            {linkedRisks.length > 0 && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (onFilterLedgerByDriverRef) {
                                    onFilterLedgerByDriverRef(item.itemNumber);
                                  } else if (onSelectRisk && linkedRisks[0]) {
                                    onSelectRisk(linkedRisks[0].id);
                                  }
                                }}
                                title={`Open Risk Register Ledger filtered to Driver Tree Ref ${item.itemNumber}`}
                                className="text-[10px] font-mono font-bold px-2 py-0.5 bg-indigo-100 hover:bg-indigo-600 text-indigo-800 hover:text-white rounded border border-indigo-200 hover:border-indigo-600 transition-all cursor-pointer flex items-center gap-1 active:scale-95"
                              >
                                <ShieldAlert className="w-2.5 h-2.5" />
                                {linkedRisks.length} Risk{linkedRisks.length > 1 ? 's' : ''}
                              </button>
                            )}
                            {linkedIssues.length > 0 && (
                              <button
                                type="button"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  if (onFilterIssuesByDriverRef) {
                                    onFilterIssuesByDriverRef(item.itemNumber);
                                  } else if (onSelectIssue && linkedIssues[0]) {
                                    onSelectIssue(linkedIssues[0].id);
                                  }
                                }}
                                title={`Open Issue Register filtered to Driver Tree Ref ${item.itemNumber}`}
                                className="text-[10px] font-mono font-bold px-2 py-0.5 bg-amber-100 hover:bg-amber-600 text-amber-800 hover:text-white rounded border border-amber-200 hover:border-amber-600 transition-all cursor-pointer flex items-center gap-1 active:scale-95"
                              >
                                <AlertCircle className="w-2.5 h-2.5" />
                                {linkedIssues.length} Issue{linkedIssues.length > 1 ? 's' : ''}
                              </button>
                            )}
                            <button
                              type="button"
                              onClick={(e) => handleOpenEditModal(item, e)}
                              className="p-1 text-slate-400 hover:text-indigo-600 hover:bg-slate-100 rounded transition-colors cursor-pointer"
                              title="Edit item"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            /* Sequential Cards View */
            <div className="space-y-2 overflow-y-auto max-h-[680px] pr-1">
              {filteredItems.map(item => {
                const isSelected = selectedItem.id === item.id;
                const linkedRisks = getLinkedRisks(item);
                const linkedIssues = getLinkedIssues(item);

                return (
                  <div
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-3 rounded-xl border transition-all cursor-pointer group flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                      isSelected
                        ? 'bg-indigo-50/90 border-indigo-300 ring-2 ring-indigo-500/20 shadow-2xs'
                        : 'bg-slate-50/50 border-slate-200/70 hover:bg-slate-100/80 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-start gap-3 min-w-0">
                      <span className="font-mono text-xs font-black text-indigo-700 bg-white border border-indigo-200 px-2.5 py-1 rounded-lg shrink-0 shadow-2xs">
                        {item.itemNumber}
                      </span>
                      <div className="space-y-1 min-w-0">
                        <div className="text-xs font-semibold text-slate-900 leading-snug">
                          {item.description}
                        </div>
                        <div className="flex flex-wrap items-center gap-3 text-[10px] text-slate-500">
                          <span className="flex items-center gap-1 font-medium text-slate-700">
                            <User className="w-3 h-3 text-indigo-500 shrink-0" />
                            {item.owner}
                          </span>
                          <span className="flex items-center gap-1 text-slate-600">
                            <Calendar className="w-3 h-3 text-emerald-600 shrink-0" />
                            {item.completeBy}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
                      {linkedRisks.length > 0 && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onFilterLedgerByDriverRef) {
                              onFilterLedgerByDriverRef(item.itemNumber);
                            } else if (onSelectRisk && linkedRisks[0]) {
                              onSelectRisk(linkedRisks[0].id);
                            }
                          }}
                          title={`Click to open Register Ledger filtered to Driver Tree Ref ${item.itemNumber} (${linkedRisks.length} Risk${linkedRisks.length > 1 ? 's' : ''})`}
                          className="text-[10px] font-mono font-bold px-2.5 py-1 bg-indigo-100 hover:bg-indigo-600 text-indigo-800 hover:text-white rounded-full border border-indigo-200 hover:border-indigo-600 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center gap-1 active:scale-95"
                        >
                          <ShieldAlert className="w-3 h-3" />
                          {linkedRisks.length} Risk{linkedRisks.length > 1 ? 's' : ''}
                          <ExternalLink className="w-2.5 h-2.5 ml-0.5 opacity-70" />
                        </button>
                      )}
                      {linkedIssues.length > 0 && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onFilterIssuesByDriverRef) {
                              onFilterIssuesByDriverRef(item.itemNumber);
                            } else if (onSelectIssue && linkedIssues[0]) {
                              onSelectIssue(linkedIssues[0].id);
                            }
                          }}
                          title={`Click to open Issue Register filtered to Driver Tree Ref ${item.itemNumber} (${linkedIssues.length} Issue${linkedIssues.length > 1 ? 's' : ''})`}
                          className="text-[10px] font-mono font-bold px-2.5 py-1 bg-amber-100 hover:bg-amber-600 text-amber-800 hover:text-white rounded-full border border-amber-200 hover:border-amber-600 transition-all cursor-pointer shadow-2xs hover:shadow-xs flex items-center gap-1 active:scale-95"
                        >
                          <AlertCircle className="w-3 h-3" />
                          {linkedIssues.length} Issue{linkedIssues.length > 1 ? 's' : ''}
                          <ExternalLink className="w-2.5 h-2.5 ml-0.5 opacity-70" />
                        </button>
                      )}
                      
                      <button
                        type="button"
                        onClick={(e) => handleOpenEditModal(item, e)}
                        title="Edit Item Number, Description, Target Date, or Assigned Person"
                        className="opacity-80 group-hover:opacity-100 p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-white rounded-lg border border-transparent hover:border-slate-200 transition-all cursor-pointer"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

      {/* EDIT / ADD DRIVER TREE ITEM MODAL */}
      {(editingItem || isNewItemModal) && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <Edit2 className="w-5 h-5 text-indigo-600" />
                <h3 className="text-base font-bold text-slate-900">
                  {isNewItemModal ? 'Add New CD1 Driver Item' : `Edit CD1 Driver Item (${editingItem?.itemNumber})`}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => {
                  setEditingItem(null);
                  setIsNewItemModal(false);
                }}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              {/* Item Number */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Item Number <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. 1.10a, 1.1, 2.0..."
                  value={editForm.itemNumber}
                  onChange={(e) => setEditForm(prev => ({ ...prev, itemNumber: e.target.value }))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 font-mono font-bold focus:outline-indigo-500"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Description <span className="text-red-500">*</span>
                </label>
                <textarea
                  rows={3}
                  placeholder="Enter milestone / platform readiness description..."
                  value={editForm.description}
                  onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-indigo-500"
                />
              </div>

              {/* Complete By */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Completed By (Target Date / Milestone Window)
                </label>
                <input
                  type="text"
                  placeholder="e.g. April 2026, May-July 2026..."
                  value={editForm.completeBy}
                  onChange={(e) => setEditForm(prev => ({ ...prev, completeBy: e.target.value }))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-indigo-500"
                />
              </div>

              {/* Assigned Lead Person */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Assigned Lead / Owner (Column 1)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Team Google, Darrl James/Grae Noble..."
                  value={editForm.owner}
                  onChange={(e) => setEditForm(prev => ({ ...prev, owner: e.target.value }))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-indigo-500"
                />
              </div>

              {/* Category */}
              <div>
                <label className="block font-bold text-slate-700 mb-1">
                  Category / Functional Cluster
                </label>
                <input
                  type="text"
                  placeholder="e.g. Enterprise Platform, Milestones, Security..."
                  value={editForm.category}
                  onChange={(e) => setEditForm(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-lg text-slate-900 focus:outline-indigo-500"
                />
              </div>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-between pt-3 border-t border-slate-100">
              {!isNewItemModal && editingItem ? (
                <button
                  type="button"
                  onClick={(e) => handleDeleteItem(editingItem.id, e)}
                  className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 text-xs font-semibold rounded-lg flex items-center gap-1 border border-red-200 cursor-pointer"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete Item
                </button>
              ) : <div />}

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setEditingItem(null);
                    setIsNewItemModal(false);
                  }}
                  className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-xl cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveItem}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs rounded-xl flex items-center gap-1.5 cursor-pointer shadow-sm"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Item Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
