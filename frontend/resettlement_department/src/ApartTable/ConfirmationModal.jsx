export default function ConfirmationModal({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message,
  confirmText = "Подтвердить",
  cancelText = "Отмена"
}) {
  if (!isOpen) return null;

return (
  <div className="fixed inset-0 z-[99999] backdrop-blur-sm flex items-center justify-center animate-fadeIn">
  <div className="bg-white/30 backdrop-blur-lg border border-white/40 ring-1 ring-white/10 
                shadow-2xl rounded-2xl p-5 max-w-[450px] w-full max-h-[220px] h-full 
                transition flex flex-col justify-center items-center text-center">
      <h3 className="text-lg font-semibold text-center text-gray-900 dark:text-white mb-6 leading-snug">
        {title}
      </h3>

      <p className="text-base text-gray-400 text-center dark:text-gray-300 mb-6 leading-relaxed">
        {message}
      </p>

      <div className="flex justify-center">
        <div className="inline-grid grid-cols-2 gap-16">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300 
                       rounded-md bg-gray-200 hover:bg-gray-300 dark:hover:bg-white/10 
                       transition text-center"
          >
            {cancelText || "Отмена"}
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm font-medium text-white 
                       bg-blue-500 rounded-md hover:bg-blue-600 active:scale-95 
                       transition text-center"
          >
            {confirmText || "Подтвердить действие"}
          </button>
        </div>
      </div>
    </div>
  </div>
);
};