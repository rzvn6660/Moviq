import React, { useState } from 'react';
import type { VideoItem } from '../../types/video';
import { AlertTriangle, Trash2, X, Loader2 } from 'lucide-react';

interface DeleteConfirmModalProps {
  video: VideoItem | null;
  onClose: () => void;
  onConfirmDelete: (video: VideoItem) => Promise<void>;
}

export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  video,
  onClose,
  onConfirmDelete,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!video) return null;

  const handleDelete = async () => {
    setIsDeleting(true);
    setErrorMessage(null);
    try {
      await onConfirmDelete(video);
      onClose();
    } catch (err: any) {
      console.error("Delete failed:", err);
      setErrorMessage(err.message || "Failed to delete generation. Please try again.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div 
        className="w-full max-w-md bg-[#0c1324] border border-rose-500/30 rounded-2xl p-6 shadow-2xl space-y-5 relative"
        role="dialog"
        aria-modal="true"
        aria-labelledby="delete-dialog-title"
      >
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 id="delete-dialog-title" className="text-base font-bold text-slate-100">
                Delete Generation?
              </h3>
              <p className="text-xs text-slate-400">This action cannot be undone.</p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
            aria-label="Close dialog"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Video Prompt Preview */}
        <div className="p-3 rounded-xl bg-[#070d1f] border border-[#23293c] space-y-1 text-xs">
          <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider font-semibold">
            Prompt to be deleted:
          </span>
          <p className="text-slate-200 line-clamp-2 italic font-sans">
            "{video.originalPrompt}"
          </p>
          <div className="flex items-center gap-2 pt-1 text-[10px] font-mono text-slate-400">
            <span>ID: {video.id}</span>
            <span>•</span>
            <span>{video.style}</span>
            <span>•</span>
            <span>{video.duration}</span>
          </div>
        </div>

        <p className="text-xs text-slate-300 leading-relaxed">
          Permanently deletes the SQLite database record, MP4 video output, and generated thumbnail image file from server storage.
        </p>

        {/* Error message display if deletion failed */}
        {errorMessage && (
          <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-mono space-y-1">
            <strong>Backend Error:</strong>
            <p>{errorMessage}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="px-4 py-2 rounded-xl bg-[#151b2d] hover:bg-[#191f31] border border-[#23293c] text-xs font-semibold text-slate-300 transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={handleDelete}
            disabled={isDeleting}
            className="flex items-center gap-2 px-5 py-2 rounded-xl bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-500 hover:to-rose-600 text-white text-xs font-bold transition-all shadow-lg shadow-rose-600/20 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500"
          >
            {isDeleting ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete Generation</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
