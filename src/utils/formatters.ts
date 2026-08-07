/**
 * Utility functions for formatting relative timestamps, media URLs, and prompt versioning.
 */

export const resolveMediaUrl = (url: string): string => {
  if (!url) return '';
  if (url.startsWith('http://') || url.startsWith('https://')) return url;
  const rawBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1';
  const backendBase = rawBase.replace(/\/api\/v1\/?$/, '');
  return `${backendBase}${url.startsWith('/') ? '' : '/'}${url}`;
};

export const formatRelativeTime = (rawTimestamp: string): string => {
  if (!rawTimestamp || rawTimestamp === 'Just now') return 'Just now';

  try {
    const date = new Date(rawTimestamp);
    if (isNaN(date.getTime())) return rawTimestamp;

    const now = new Date();
    const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffSeconds < 30) return 'Just now';
    if (diffSeconds < 60) return `${diffSeconds} seconds ago`;

    const diffMinutes = Math.floor(diffSeconds / 60);
    if (diffMinutes < 60) return `${diffMinutes} ${diffMinutes === 1 ? 'minute' : 'minutes'} ago`;

    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24 && date.getDate() === now.getDate()) {
      return `Today ${date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
    }

    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (date.getDate() === yesterday.getDate() && date.getMonth() === yesterday.getMonth() && date.getFullYear() === yesterday.getFullYear()) {
      return `Yesterday ${date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}`;
    }

    if (date.getFullYear() === now.getFullYear()) {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }

    return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
  } catch (e) {
    return rawTimestamp;
  }
};

/**
 * Assigns version numbers (e.g. v1, v2, v3) to generations with duplicate prompts
 */
export const computePromptVersions = <T extends { id: string; originalPrompt: string; timestamp: string }>(items: T[]): Map<string, number> => {
  const versionMap = new Map<string, number>();
  
  // Group items by normalized prompt
  const groups = new Map<string, T[]>();
  for (const item of items) {
    const key = item.originalPrompt.trim().toLowerCase();
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(item);
  }

  // Sort each group chronologically (oldest first) and assign version 1..N
  for (const [, groupItems] of groups.entries()) {
    if (groupItems.length > 1) {
      const sorted = [...groupItems].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
      sorted.forEach((item, index) => {
        versionMap.set(item.id, index + 1);
      });
    }
  }

  return versionMap;
};

/**
 * Production-grade Blob file download helper.
 * Fetches endpoint, parses Content-Disposition header for human-readable filename,
 * enforces video/mp4 Blob type, and triggers reliable browser download across all browsers.
 */
export const triggerFileDownload = async (endpointUrl: string, defaultFilename: string = 'moviq-video.mp4'): Promise<void> => {
  try {
    const response = await fetch(endpointUrl, { method: 'GET' });
    if (!response.ok) {
      throw new Error(`Download HTTP request failed with status ${response.status}`);
    }

    let filename = defaultFilename;
    const contentDisposition = response.headers.get('content-disposition');
    if (contentDisposition) {
      const match = contentDisposition.match(/filename\*?=(?:UTF-8'')?["']?([^"';]+)["']?/i);
      if (match && match[1]) {
        filename = decodeURIComponent(match[1].trim());
      }
    }

    if (!filename.toLowerCase().endsWith('.mp4')) {
      filename = `${filename}.mp4`;
    }

    const arrayBuffer = await response.arrayBuffer();
    const mp4Blob = new Blob([arrayBuffer], { type: 'video/mp4' });

    const blobUrl = window.URL.createObjectURL(mp4Blob);
    const link = document.createElement('a');
    link.style.display = 'none';
    link.href = blobUrl;
    link.download = filename;

    document.body.appendChild(link);
    link.click();

    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    }, 1500);
  } catch (error) {
    console.error('Production Blob download error, attempting direct navigation fallback:', error);
    const fallbackLink = document.createElement('a');
    fallbackLink.href = endpointUrl;
    fallbackLink.target = '_blank';
    fallbackLink.download = defaultFilename.endsWith('.mp4') ? defaultFilename : `${defaultFilename}.mp4`;
    document.body.appendChild(fallbackLink);
    fallbackLink.click();
    document.body.removeChild(fallbackLink);
  }
};
