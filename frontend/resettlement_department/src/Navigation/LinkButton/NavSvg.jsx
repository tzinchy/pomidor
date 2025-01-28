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
          <path d="M9.66667 26.8047V12.3101H1V26.5047C1 26.6704 1.13432 26.8047 1.3 26.8047H9.66667Z" stroke="black" strokeWidth="2"/>
          <path d="M27 20.0404V26.5046C27 26.6703 26.8657 26.8046 26.7 26.8046H14V13.2763H27V16.6583M18.3333 1.43896H26.7C26.8657 1.43896 27 1.57328 27 1.73896V8.68629C17.6111 8.68629 1 8.68629 1 8.68629V1.73896C1 1.57328 1.13431 1.43896 1.3 1.43896H14" stroke="black" strokeWidth="2"/>
          </svg>
          ),
        'table_page': (<svg width="32" height="31" viewBox="0 0 32 31" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5.06086 13.0406L1.38773 15.9794C1.31657 16.0363 1.27515 16.1225 1.27515 16.2137L1.27515 21.045C1.27515 21.2107 1.40946 21.345 1.57515 21.345H8.92141C9.0871 21.345 9.22141 21.2107 9.22141 21.045V16.2137C9.22141 16.1225 9.17999 16.0363 9.10884 15.9794L5.4357 13.0406C5.32613 12.9529 5.17043 12.9529 5.06086 13.0406Z" stroke="black" strokeWidth="2"/>
          <path d="M26.4686 29.6998V9.10762C26.4686 8.94193 26.3343 8.80762 26.1686 8.80762H18.6124C18.4467 8.80762 18.3124 8.94193 18.3124 9.10762V29.6998C18.3124 29.8655 18.4467 29.9998 18.6124 29.9998H26.1686C26.3343 29.9998 26.4686 29.8655 26.4686 29.6998Z" stroke="black" strokeWidth="2"/>
          <path d="M26.4688 29.6998V14.6845C26.4688 14.5188 26.6031 14.3845 26.7688 14.3845H30.7C30.8657 14.3845 31 14.5188 31 14.6845V29.6998C31 29.8655 30.8657 29.9998 30.7 29.9998H26.7688C26.6031 29.9998 26.4688 29.8655 26.4688 29.6998Z" stroke="black" strokeWidth="2"/>
          <path d="M5.17175 13.2692V1H22.3904V8.80766" stroke="black" strokeWidth="2"/>
          </svg>
          
        ),
        'aparts': (<svg width="36" height="37" viewBox="0 0 36 37" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M13.5312 27.1947V16.6237C13.5312 16.458 13.6656 16.3237 13.8313 16.3237H22.1688C22.3344 16.3237 22.4688 16.458 22.4688 16.6237V27.1947" stroke="black" strokeWidth="2"/>
          <g filter="url(#filter0_d_269_889)">
          <path d="M17.8275 1.94688L5.13097 10.6177C5.04912 10.6736 5.00016 10.7664 5.00016 10.8655L5 26.8947C5 27.0604 5.13432 27.1947 5.3 27.1947H30.7C30.8657 27.1947 31 27.0604 31 26.8947V10.8734C31 10.77 30.9467 10.6738 30.8589 10.619L26.9375 8.17051L18.1703 1.94995C18.068 1.87732 17.9312 1.87609 17.8275 1.94688Z" stroke="black" strokeWidth="2" shapeRendering="crispEdges"/>
          </g>
          <defs>
          <filter id="filter0_d_269_889" x="0" y="0.894531" width="36" height="35.3003" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
          <feFlood floodOpacity="0" result="BackgroundImageFix"/>
          <feOffset dy="4"/>
          <feGaussianBlur stdDeviation="2"/>
          <feComposite in2="hardAlpha" operator="out"/>
          <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_269_889"/>
          <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_269_889" result="shape"/>
          </filter>
          </defs>
          </svg>
          
        )
    };
    return svg[state['state']]
  }