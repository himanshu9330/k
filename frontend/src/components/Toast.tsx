import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'warning' | 'error' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

interface ToastContextType {
  showToast: (type: ToastType, title: string, message?: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback((type: ToastType, title: string, message?: string) => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, title, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4500);
  }, []);

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full px-4 pointer-events-none">
        {toasts.map((toast) => {
          const bgMap = {
            success: 'bg-[#F0FDF4] border-[#BBF7D0] text-[#1E3A2F]',
            warning: 'bg-[#FEF9E7] border-[#FCE8B2] text-[#593D0E]',
            error: 'bg-[#FDF2F2] border-[#F8D7DA] text-[#632020]',
            info: 'bg-[#EBF8FF] border-[#BEE3F8] text-[#1A365D]',
          };

          const iconMap = {
            success: <CheckCircle2 className="w-5 h-5 text-[#2D7A4D] shrink-0" />,
            warning: <AlertTriangle className="w-5 h-5 text-[#B7791F] shrink-0" />,
            error: <XCircle className="w-5 h-5 text-[#B94A48] shrink-0" />,
            info: <Info className="w-5 h-5 text-[#2B6CB0] shrink-0" />,
          };

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl border shadow-elevated transition-all transform duration-200 animate-in slide-in-from-bottom-3 ${bgMap[toast.type]}`}
            >
              {iconMap[toast.type]}
              <div className="flex-1 min-w-0">
                <p className="font-bold text-[15px]">{toast.title}</p>
                {toast.message && <p className="text-[13.5px] mt-0.5 opacity-90">{toast.message}</p>}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="p-1 hover:bg-black/5 rounded text-charcoal-muted"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};
