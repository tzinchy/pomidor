export function StatusIcon({ status, mini }) {
    const statusMap = {
      "Не начато": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-x text-slate-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path><path d="m14 14-4 4"></path><path d="m10 14 4 4"></path></svg>),
      "Менее месяца": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-range text-lime-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M16 2v4"></path><path d="M3 10h18"></path><path d="M8 2v4"></path><path d="M17 14h-6"></path><path d="M13 18H7"></path><path d="M7 14h.01"></path><path d="M17 18h.01"></path></svg>),
      "От 1 до 2 месяцев": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-range text-yellow-400 ${mini ? 'mr-2 h-4 w-4' : ''}`}><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M16 2v4"></path><path d="M3 10h18"></path><path d="M8 2v4"></path><path d="M17 14h-6"></path><path d="M13 18H7"></path><path d="M7 14h.01"></path><path d="M17 18h.01"></path></svg>),
      "От 2 до 5 месяцев": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-range text-amber-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M16 2v4"></path><path d="M3 10h18"></path><path d="M8 2v4"></path><path d="M17 14h-6"></path><path d="M13 18H7"></path><path d="M7 14h.01"></path><path d="M17 18h.01"></path></svg>),
      "От 5 до 8 месяцев": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-range text-orange-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M16 2v4"></path><path d="M3 10h18"></path><path d="M8 2v4"></path><path d="M17 14h-6"></path><path d="M13 18H7"></path><path d="M7 14h.01"></path><path d="M17 18h.01"></path></svg>),
      "Более 8 месяцев": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-calendar-range text-rose-600 ${mini ? 'mr-2 h-4 w-4' : ''}`}><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M16 2v4"></path><path d="M3 10h18"></path><path d="M8 2v4"></path><path d="M17 14h-6"></path><path d="M13 18H7"></path><path d="M7 14h.01"></path><path d="M17 18h.01"></path></svg>),
    };
  
    return statusMap[status]
  }
  
export function RiskIcon({ risk, mini }) {
    const riskMap = {
      "Наступили риски": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-x text-red-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg>),
      "Работа завершена": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-check text-emerald-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>),
      "Без отклонений": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-ellipsis text-blue-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="M17 12h.01"></path><path d="M12 12h.01"></path><path d="M7 12h.01"></path></svg>),
      "Требует внимания": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-alert text-yellow-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><line x1="12" x2="12" y1="8" y2="12"></line><line x1="12" x2="12.01" y1="16" y2="16"></line></svg>)
    };
  
    return riskMap[risk]
  }
  
  export function PotborIcon({ potbor, mini }) {
    const potborMap = {
      "Согласие": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-check text-emerald-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="m9 12 2 2 4-4"></path></svg>),
      "Ждёт одобрения": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-ellipsis text-amber-300 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="M17 12h.01"></path><path d="M12 12h.01"></path><path d="M7 12h.01"></path></svg>),
      "Отказ": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-x text-red-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg>),
      "Суд": (<svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.6667 13.6667L15.6667 8.33337L17.6667 13.6667C17.0867 14.1 16.3867 14.3334 15.6667 14.3334C14.9467 14.3334 14.2467 14.1 13.6667 13.6667Z" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M4.33325 13.6667L6.33325 8.33337L8.33325 13.6667C7.75325 14.1 7.05325 14.3334 6.33325 14.3334C5.61325 14.3334 4.91325 14.1 4.33325 13.6667Z" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M7.66675 17H14.3334" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 5V17" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M5 7.66671H6.33333C7.66667 7.66671 9.66667 7.00004 11 6.33337C12.3333 7.00004 14.3333 7.66671 15.6667 7.66671H17" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M11 21C16.5228 21 21 16.5228 21 11C21 5.47715 16.5228 1 11 1C5.47715 1 1 5.47715 1 11C1 16.5228 5.47715 21 11 21Z" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>),
      "Фонд компенсация": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-dollar-sign text-violet-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"></path><path d="M12 18V6"></path></svg>),
      "Фонд докупка": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-dollar-sign text-violet-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"></path><path d="M12 18V6"></path></svg>),
      "Ожидание": (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`lucide lucide-circle-ellipsis text-blue-500 ${mini ? 'mr-2 h-4 w-4' : ''}`}><circle cx="12" cy="12" r="10"></circle><path d="M17 12h.01"></path><path d="M12 12h.01"></path><path d="M7 12h.01"></path></svg>)
    };
  
    return potborMap[potbor]
  }