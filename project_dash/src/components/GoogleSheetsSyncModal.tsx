/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { X, Cloud, RefreshCw, CheckCircle2, AlertCircle, ExternalLink, Link2 } from 'lucide-react';
import { fetchGoogleSheetData, parseGoogleSheetUrl } from '../utils/googleSheetsService';
import { RiskTicket } from '../types';

interface GoogleSheetsSyncModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDataLoaded: (tickets: RiskTicket[], sheetSource: string) => void;
  currentSheetUrl?: string;
}

export default function GoogleSheetsSyncModal({
  isOpen,
  onClose,
  onDataLoaded,
  currentSheetUrl = ''
}: GoogleSheetsSyncModalProps) {
  const [urlInput, setUrlInput] = useState<string>(currentSheetUrl || 'https://docs.google.com/spreadsheets/d/1qR1tEHFs0QC6CGSUpzHgVgolcF0zQNcg99yZgJwoMVY/edit');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  if (!isOpen) return null;

  const handleSync = async () => {
    if (!urlInput.trim()) {
      setErrorMessage('Please enter a valid Google Sheet URL or Spreadsheet ID');
      return;
    }

    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');

    try {
      const tickets = await fetchGoogleSheetData(urlInput.trim());
      if (tickets.length === 0) {
        throw new Error('No valid risk or issue rows were found in the specified sheet.');
      }
      setSuccessMessage(`Successfully imported ${tickets.length} risks & issues directly from Google Sheets!`);
      setTimeout(() => {
        onDataLoaded(tickets, urlInput.trim());
        onClose();
      }, 1200);
    } catch (err: any) {
      console.error('Google Sheet sync failed:', err);
      setErrorMessage(
        err.message || 'Failed to sync from Google Sheet. Ensure the sheet is published or shared with "Anyone with the link can view".'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="bg-gradient-to-r from-emerald-600 to-teal-700 p-5 text-white flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-xl backdrop-blur-xs">
              <Cloud className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold">Google Sheets Live Sync</h2>
              <p className="text-xs text-emerald-100">Direct integration with Google Drive & live spreadsheets</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Google Sheet URL or Spreadsheet ID:
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Link2 className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://docs.google.com/spreadsheets/d/.../edit#gid=0"
                className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-hidden transition-all"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1.5 flex items-center gap-1">
              <span>💡 Tip: Paste your Google Sheet URL from Google Drive. Ensure the sheet is shared or published to web.</span>
            </p>
          </div>

          {/* Success / Error Messages */}
          {errorMessage && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-3.5 flex items-start gap-2.5 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>{errorMessage}</div>
            </div>
          )}

          {successMessage && (
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-3.5 flex items-center gap-2.5 text-xs text-emerald-700 font-semibold">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <div>{successMessage}</div>
            </div>
          )}

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3.5 text-xs text-slate-600 space-y-1.5">
            <div className="font-semibold text-slate-800 flex items-center gap-1.5">
              <span>Automatic Column Normalization (36 Columns)</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Columns such as Risk ID, Description, Status, Inherent/Residual Ratings, Driver Tree Ref, and Governance Level will be automatically mapped to the schema.
            </p>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="bg-slate-50 border-t border-slate-200 px-6 py-4 flex justify-between items-center">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 hover:bg-slate-200/60 rounded-xl transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleSync}
            disabled={isLoading}
            className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20 hover:shadow-lg flex items-center gap-2 transition-all disabled:opacity-50 cursor-pointer"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                Syncing with Google Sheets...
              </>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                Sync Now
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
