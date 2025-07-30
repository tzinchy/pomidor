import { LogOut } from "lucide-react";
import ToolTip from "./ToolTip";

const LogoutButton = () => {
  const handleLogout = () => {
    // Очистить все куки
    document.cookie.split(";").forEach((cookie) => {
      const [name] = cookie.split("=");
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
    });

    // Переадресация
    window.location.href = `${import.meta.env.VITE_AUTH_URL}/?redirect_uri=${encodeURIComponent(window.location.href)}`; // <-- замените на нужный адрес
  };

  return (
<div className="relative group">
  <button
    onClick={handleLogout}
    className="flex items-center justify-center p-0 h-10 w-10 stroke-red-500 hover:bg-red-100 rounded-md transition"
  >
    <LogOut size={24} className="stroke-red-500" />
  </button>

<ToolTip text={`Выйти`} />
</div>
  );
};

export default LogoutButton;