// confirm.js
import { createRoot } from "react-dom/client";
import RConfirmationModal from "./ApartTable/ConfirmationModalResponse";

export function showConfirmation({ title, message, confirmText, cancelText }) {
  return new Promise((resolve) => {
    const modalRoot = document.createElement("div");
    document.body.appendChild(modalRoot);

    const root = createRoot(modalRoot);

    const handleClose = () => {
      root.unmount();
      modalRoot.remove();
      resolve(false);
    };

    const handleConfirm = () => {
      root.unmount();
      modalRoot.remove();
      resolve(true);
    };

    root.render(
      <RConfirmationModal
        title={title}
        message={message}
        onConfirm={handleConfirm}
        onClose={handleClose}
        confirmText={confirmText}
        cancelText={cancelText}
      />
    );
  });
}