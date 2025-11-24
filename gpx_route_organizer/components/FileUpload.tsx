
import React, { useState, useCallback } from 'react';
import { UploadIcon } from './icons';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  disabled: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileSelect, disabled }) => {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (disabled) return;

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      if(files[0].name.endsWith('.gpx')) {
        onFileSelect(files[0]);
      } else {
        alert("Please upload a valid .gpx file.");
      }
    }
  }, [onFileSelect, disabled]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onFileSelect(files[0]);
    }
  };

  const borderClass = isDragging ? 'border-brand-primary ring-2 ring-brand-primary' : 'border-slate-300 dark:border-slate-600';
  const disabledClass = disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer';

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={`relative w-full p-8 border-2 ${borderClass} border-dashed rounded-xl text-center transition-all duration-300 bg-white dark:bg-slate-800 ${disabledClass}`}
    >
      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept=".gpx"
        onChange={handleFileChange}
        disabled={disabled}
      />
      <label htmlFor="file-upload" className={`w-full flex flex-col items-center ${disabled ? '' : 'cursor-pointer'}`}>
        <UploadIcon className="h-12 w-12 text-brand-primary mb-4" />
        <p className="text-slate-700 dark:text-slate-300 font-semibold">
          Drag & Drop a GPX file here
        </p>
        <p className="text-slate-500 dark:text-slate-400 mt-1">or click to select a file</p>
      </label>
    </div>
  );
};

export default FileUpload;
