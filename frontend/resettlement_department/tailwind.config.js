/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],

  theme: {
    extend: {},
  },

  daisyui: {
    themes: false, // Отключаем встроенные темы daisyUI
  },

  plugins: [
    require("daisyui"),
    // Если хотите использовать icon-[tabler--folder], icon-[tabler--plus], и т. д.:
    // require("tailwindcss-iconify")({
    //   collections: {
    //     tabler: () => import("@iconify-json/tabler/icons.json"),
    //   },
    // }),
  ],
};
