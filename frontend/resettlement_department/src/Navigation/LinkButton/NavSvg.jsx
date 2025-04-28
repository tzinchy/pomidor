export function NavSvg(state) {
    const svg = {
        'dashboard': (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-gauge"><path d="m12 14 4-4"></path><path d="M3.34 19a10 10 0 1 1 17.32 0"></path></svg>),
        'table_page': (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-house"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>),
        'aparts': (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-users"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>)
    };
    return svg[state['state']]
  }

  export function NavPng(state) {
    const svg = {
        'dashboard': (<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9.66667 26.8047V12.3101H1V26.5047C1 26.6704 1.13432 26.8047 1.3 26.8047H9.66667Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M27 20.0404V26.5046C27 26.6703 26.8657 26.8046 26.7 26.8046H14V13.2763H27V16.6583M18.3333 1.43896H26.7C26.8657 1.43896 27 1.57328 27 1.73896V8.68629C17.6111 8.68629 1 8.68629 1 8.68629V1.73896C1 1.57328 1.13431 1.43896 1.3 1.43896H14" stroke="currentColor" strokeWidth="2"/>
          </svg>
          ),
        'table_page': (<svg width="32" height="31" viewBox="0 0 32 31" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5.06086 13.0406L1.38773 15.9794C1.31657 16.0363 1.27515 16.1225 1.27515 16.2137L1.27515 21.045C1.27515 21.2107 1.40946 21.345 1.57515 21.345H8.92141C9.0871 21.345 9.22141 21.2107 9.22141 21.045V16.2137C9.22141 16.1225 9.17999 16.0363 9.10884 15.9794L5.4357 13.0406C5.32613 12.9529 5.17043 12.9529 5.06086 13.0406Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M26.4686 29.6998V9.10762C26.4686 8.94193 26.3343 8.80762 26.1686 8.80762H18.6124C18.4467 8.80762 18.3124 8.94193 18.3124 9.10762V29.6998C18.3124 29.8655 18.4467 29.9998 18.6124 29.9998H26.1686C26.3343 29.9998 26.4686 29.8655 26.4686 29.6998Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M26.4688 29.6998V14.6845C26.4688 14.5188 26.6031 14.3845 26.7688 14.3845H30.7C30.8657 14.3845 31 14.5188 31 14.6845V29.6998C31 29.8655 30.8657 29.9998 30.7 29.9998H26.7688C26.6031 29.9998 26.4688 29.8655 26.4688 29.6998Z" stroke="currentColor" strokeWidth="2"/>
          <path d="M5.17175 13.2692V1H22.3904V8.80766" stroke="currentColor" strokeWidth="2"/>
          </svg>
        ),
        'aparts': (<svg viewBox="0 0 24 24" width="32" height="31" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M2 22H22" stroke="currentColor" strokeWidth="1.5" strokeMiterlimit="10" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M2.94995 22L2.99995 9.96999C2.99995 9.35999 3.28995 8.78004 3.76995 8.40004L10.77 2.95003C11.49 2.39003 12.5 2.39003 13.23 2.95003L20.23 8.39003C20.72 8.77003 21 9.34999 21 9.96999V22" stroke="currentColor" strokeWidth="1.5" strokeMiterlimit="10" strokeLinejoin="round"></path> <path d="M15.5 11H8.5C7.67 11 7 11.67 7 12.5V22H17V12.5C17 11.67 16.33 11 15.5 11Z" stroke="currentColor" strokeWidth="1.5" strokeMiterlimit="10" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M10 16.25V17.75" stroke="currentColor" strokeWidth="1.5" strokeMiterlimit="10" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M10.5 7.5H13.5" stroke="currentColor" strokeWidth="1.5" strokeMiterlimit="10" strokeLinecap="round" strokeLinejoin="round"></path> </g></svg>),
        'balance': (<svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M30 3.33325H9.99996C8.15901 3.33325 6.66663 4.82564 6.66663 6.66659V33.3333C6.66663 35.1742 8.15901 36.6666 9.99996 36.6666H30C31.8409 36.6666 33.3333 35.1742 33.3333 33.3333V6.66659C33.3333 4.82564 31.8409 3.33325 30 3.33325Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M13.3334 10H26.6667" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M26.6666 23.3333V29.9999" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M26.6666 16.6667H26.6833" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M20 16.6667H20.0167" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M13.3334 16.6667H13.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M20 23.3333H20.0167" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M13.3334 23.3333H13.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M20 30H20.0167" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M13.3334 30H13.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>          
        )
    };
    return svg[state['state']]
  }