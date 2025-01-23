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
        'dashboard': (<svg width="43" height="43" viewBox="0 0 43 43" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18.9524 28.8333V16.9286H13V28.5333C13 28.699 13.1343 28.8333 13.3 28.8333H18.9524Z" stroke="currentColor"/>
          <path d="M30.8571 23.2778V28.5333C30.8571 28.699 30.7228 28.8333 30.5571 28.8333H21.9286V17.7222H30.8571V20.5M24.9047 8H30.5571C30.7228 8 30.8571 8.13431 30.8571 8.3V13.9524C24.4087 13.9524 13 13.9524 13 13.9524V8.3C13 8.13431 13.1343 8 13.3 8H21.9286" stroke="currentColor"/>
        </svg>),
        'table_page': (<svg width="43" height="43" viewBox="0 0 43 43" fill="none" stroke="currentColor" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 29L32 31" />
          <path d="M20.5 31L22.6651 34H18.3349L20.5 31Z" />
          <path d="M21.324 25.1514V27.8873M21.324 25.1514V22.4155M21.324 25.1514L23.9705 22.4155M23.9705 6L21.324 8.73592V11.4718M23.9705 6L26.617 8.73592V11.4718M23.9705 6V8.73592M26.617 14.2077L29.2636 11.4718M26.617 14.2077V11.4718M26.617 14.2077L23.9705 11.4718M26.617 14.2077V16.9437M29.2636 11.4718L31.9101 14.2077V16.9437M29.2636 11.4718V14.2077M31.9101 27.8873H29.2636M31.9101 27.8873V25.1514M31.9101 27.8873L29.2636 25.1514M21.324 27.8873H23.9705M21.324 27.8873L23.9705 25.1514M26.617 27.8873H23.9705M26.617 27.8873H29.2636M26.617 27.8873V26.5194M26.617 27.8873L29.2636 25.1514M26.617 27.8873L23.9705 25.1514M23.9705 27.8873V25.1514M29.2636 27.8873V25.1514M21.324 11.4718L23.9705 8.73592M21.324 11.4718V14.2077M23.9705 8.73592L26.617 11.4718M23.9705 8.73592V11.4718M23.9705 11.4718V14.2077M23.9705 11.4718L22.6473 12.8398L21.324 14.2077M21.324 14.2077V16.9437M21.324 16.9437L23.9705 14.2077M21.324 16.9437V19.6796M23.9705 14.2077L26.617 16.9437M23.9705 14.2077V16.9437M26.617 16.9437V19.6796M26.617 16.9437V26.5194M26.617 16.9437L29.2636 14.2077M21.324 19.6796L23.9705 16.9437M21.324 19.6796V22.4155M23.9705 16.9437L26.617 19.6796M23.9705 16.9437V19.6796M26.617 19.6796V22.4155M26.617 19.6796L29.2636 16.9437M21.324 22.4155L23.9705 19.6796M23.9705 19.6796L26.617 22.4155M23.9705 19.6796V22.4155M26.617 22.4155V25.1514M26.617 22.4155L29.2636 19.6796M23.9705 22.4155L26.617 25.1514M23.9705 22.4155V25.1514M26.617 25.1514V26.5194M26.617 25.1514L29.2636 22.4155M29.2636 14.2077L31.9101 16.9437M29.2636 14.2077V16.9437M31.9101 16.9437V19.6796M31.9101 19.6796L29.2636 16.9437M31.9101 19.6796V22.4155M29.2636 16.9437V19.6796M29.2636 19.6796L31.9101 22.4155M29.2636 19.6796V22.4155M31.9101 22.4155V25.1514M29.2636 22.4155L31.9101 25.1514M29.2636 22.4155V25.1514"  strokeWidth="0.5"/>
          <path d="M33 27.8875H20"  strokeWidth="0.5"/>
          <path d="M33 27.8875H20"  strokeWidth="0.5"/>
          <path d="M12.9622 17L9.35334 19.9562V24.8169H16.5711V19.9562L12.9622 17Z"/>
          <path d="M8 21.0648L12.9622 17L17.9245 21.0648M9.35334 19.9392V24.8169H16.5711V19.9392" strokeWidth="0.5"/>
          <rect x="11.3086" y="20.1267" width="3.30815" height="3.12676"/>
          <path d="M12.9627 20.1267V23.2535M11.3086 21.6901H14.6167"  strokeWidth="0.2"/>
          <path d="M12.9627 20.1267V23.2535M11.3086 21.6901H14.6167"  strokeWidth="0.2"/>
        </svg>
        ),
        'table_pag': (<svg width="34" height="22" viewBox="0 0 34 22" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1 5.16L5.96223 1L11 5.09369M2.35334 4.008V8.7C2.35334 8.86569 2.48765 9 2.65334 9H9.27112C9.43681 9 9.57112 8.86569 9.57112 8.7V4.008" stroke="currentColor"/>
          <path d="M31.7 16.3333H24.3401C24.1596 16.3333 24.0203 16.1719 24.0429 15.9927C25.3324 5.75779 26.1563 0.0645867 31.7589 1.12624C31.8974 1.15249 32 1.27599 32 1.417V16.0333C32 16.199 31.8657 16.3333 31.7 16.3333Z" stroke="currentColor"/>
          <path d="M31.7 16.3333H24.3401C24.1596 16.3333 24.0203 16.1719 24.0429 15.9927C25.3324 5.75779 26.1563 0.0645867 31.7589 1.12624C31.8974 1.15249 32 1.27599 32 1.417V16.0333C32 16.199 31.8657 16.3333 31.7 16.3333Z" stroke="currentColor"/>
          <path d="M25.5 6.11114L29.3333 6.11114" stroke="currentColor"/>
          <path d="M25.5 6.11114L29.3333 6.11114" stroke="currentColor"/>
          <path d="M26.5 3.55553L29.3333 3.55553" stroke="currentColor"/>
          <path d="M26.5 3.55553L29.3333 3.55553" stroke="currentColor"/>
          <path d="M25 8.66666L29.3333 8.66666" stroke="currentColor"/>
          <path d="M25 8.66666L29.3333 8.66666" stroke="currentColor"/>
          <path d="M24.5 11.2222L29.3333 11.2222" stroke="currentColor"/>
          <path d="M24.5 11.2222L29.3333 11.2222" stroke="currentColor"/>
          <path d="M24.5 13.7778L29.3333 13.7778" stroke="currentColor"/>
          <path d="M24.5 13.7778L29.3333 13.7778" stroke="currentColor"/>
          <path d="M33 17.5V20.7C33 20.8657 32.8657 21 32.7 21H1.3C1.13431 21 1 20.8657 1 20.7V10.5" stroke="currentColor"/>
          <path d="M1 11H11V9.5" stroke="currentColor"/>
          <path d="M33 18L22 18L22 10" stroke="currentColor"/>
          <path d="M22 10C22 6.68629 19.5376 4 16.5 4C13.4624 4 11 6.68629 11 10" stroke="currentColor"/>
          <path d="M20.5 10.5C20.5 12.7091 18.7091 14.5 16.5 14.5C14.2909 14.5 12.5 12.7091 12.5 10.5C12.5 8.29086 14.2909 6.5 16.5 6.5C18.7091 6.5 20.5 8.29086 20.5 10.5Z" stroke="currentColor"/>
          <circle cx="16.5" cy="10.5" r="0.625" stroke="currentColor"/>
          <path d="M16.5 6.5625V8.25" stroke="currentColor"/>
          <path d="M18.75 10.5H20.4375M12.5625 10.5H14.25M16.5 14.4375V12.75" stroke="currentColor"/>
          <path d="M17 10L18 9" stroke="currentColor"/>
          </svg>
          
        ),
        'aparts': (<svg width="43" height="43" viewBox="0 0 43 43" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 28V19.3C19 19.1343 19.1343 19 19.3 19H24.7C24.8657 19 25 19.1343 25 19.3V28" stroke="currentColor"/>
          <path d="M10 17.5L21.8024 7.17286C21.9156 7.07389 22.0844 7.07389 22.1976 7.17286L28 12.25L34 17.5M13.2727 14.35V27.7C13.2727 27.8657 13.407 28 13.5727 28H30.4273C30.593 28 30.7273 27.8657 30.7273 27.7V14.35" stroke="currentColor"/>
        </svg>
        )
    };
    return svg[state['state']]
  }