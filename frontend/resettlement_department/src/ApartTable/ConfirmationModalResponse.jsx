import { useEffect, useState } from "react";

const RConfirmationModal = ({ title, message, onConfirm, onClose, confirmText = "Да, продолжить", cancelText = "Отмена" }) => {
  const [countdown, setCountdown] = useState(5); // ⏱️ 5 секунд
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setIsReady(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const [startTime, setStartTime] = useState(Date.now());
const [elapsed, setElapsed] = useState(0);
const duration = 5000; // 5 сек в мс

useEffect(() => {
  setStartTime(Date.now());
  const interval = setInterval(() => {
    const now = Date.now();
    const diff = now - startTime;
    setElapsed(diff);

    if (diff >= duration) {
      clearInterval(interval);
      setIsReady(true);
      setCountdown(0);
    } else {
      setCountdown(Math.ceil((duration - diff) / 1000));
    }
  }, 100);

  return () => clearInterval(interval);
}, []);

  return (
    <div className="fixed inset-0 z-[99999] backdrop-blur-sm flex items-center justify-center animate-fadeIn">
      <div className="bg-white/30 backdrop-blur-lg border border-white/40 bg-white/90 ring-1 ring-white/10 
                      shadow-2xl rounded-2xl p-5 max-w-[500px] w-full max-h-[220px] h-full 
                      transition flex flex-col justify-center items-center text-center">

        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6 leading-snug">
          {title}
        </h3>

        <p className="text-base text-gray-400 dark:text-gray-300 mb-6 leading-relaxed">
          {message}
        </p>

        <div className="flex justify-center">
          <div className="grid grid-cols-2 gap-16">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 
                         rounded-md bg-gray-200 hover:bg-gray-300 dark:hover:bg-white/10 
                         transition text-center"
            >
              {cancelText}
            </button>
<button
  onClick={isReady ? onConfirm : undefined}
  disabled={!isReady}
  className={`relative overflow-hidden px-4 py-2 text-sm font-medium rounded-md transition text-center w-[180px]
    ${isReady
      ? 'bg-blue-500 text-white hover:bg-blue-600 active:scale-95'
      : 'bg-blue-200 text-white cursor-not-allowed'}`}
>
  {/* Заливка */}
  {!isReady && (
<span
  className="absolute inset-0 bg-blue-500/40"
  style={{
    transform: `translateX(-${100 - Math.min((elapsed / duration) * 100, 100)}%)`,
    transition: 'transform 0.1s linear',
  }}
/>
  )}
  {/* Текст поверх заливки */}
  <span className="relative z-10">
    {isReady ? confirmText : `${confirmText} (${countdown})`}
  </span>
</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RConfirmationModal;