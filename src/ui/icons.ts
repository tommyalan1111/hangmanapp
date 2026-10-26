import type { IconName } from "../types";

const PATHS: Record<IconName, string> = {
  clapper: `
    <rect x="3.5" y="9.5" width="17" height="10.5" rx="1.6"/>
    <path d="M3.8 9.5 5.8 4l15 2.7-2 2.8z"/>
    <path d="m8.6 5.2-1 4M13 6.1l-1 3.4M17.5 6.9l-1 2.6"/>
  `,
  tv: `
    <rect x="3" y="7" width="18" height="12.5" rx="2"/>
    <path d="m8 7 4-4 4 4"/>
    <path d="M8.5 16.8h7"/>
    <circle cx="12" cy="13.2" r="2.2"/>
  `,
  actor: `
    <circle cx="12" cy="8" r="3.2"/>
    <path d="M5.5 20c.5-3.6 3-5.8 6.5-5.8s6 2.2 6.5 5.8"/>
    <path d="m18.7 4.3.5 1.2 1.3.1-1 .8.3 1.3-1.1-.7-1.1.7.3-1.3-1-.8 1.3-.1z"/>
  `,
  actress: `
    <circle cx="12" cy="8" r="3.2"/>
    <path d="M5.5 20c.5-3.6 3-5.8 6.5-5.8s6 2.2 6.5 5.8"/>
    <path d="m19 2.8.6 1.7 1.8.1-1.4 1.1.5 1.8-1.5-1-1.5 1 .5-1.8-1.4-1.1 1.8-.1z"/>
  `,
  mask: `
    <path d="M4.5 5.8c2.4-.9 4.9-1.3 7.5-1.3s5.1.4 7.5 1.3c.4 4.9-.6 8.7-3 11.3-1.5 1.6-3 2.4-4.5 2.4s-3-.8-4.5-2.4c-2.4-2.6-3.4-6.4-3-11.3Z"/>
    <path d="M8 10.5c.8-.4 1.7-.4 2.5 0M13.5 10.5c.8-.4 1.7-.4 2.5 0M9 15.2c1.8 1.1 4.2 1.1 6 0"/>
  `,
  director: `
    <path d="M4 10.5v4l10 4v-12z"/>
    <path d="M14 8.5c2.7 0 4.5 1.4 4.5 3.5s-1.8 3.5-4.5 3.5"/>
    <path d="M6.5 14.8 7.8 20M17.8 4.5l1.7 2.2M20 10.5h2"/>
  `,
  family: `
    <circle cx="7" cy="8.2" r="2.4"/>
    <circle cx="17" cy="8.2" r="2.4"/>
    <circle cx="12" cy="11.8" r="2.1"/>
    <path d="M3.2 18.5c.4-2.8 2-4.4 4.5-4.4 1.2 0 2.2.4 2.9 1.2M20.8 18.5c-.4-2.8-2-4.4-4.5-4.4-1.2 0-2.2.4-2.9 1.2M7.5 21c.3-2.3 1.8-3.7 4.5-3.7s4.2 1.4 4.5 3.7"/>
  `,
  play: `<path d="M8 5.2 19 12 8 18.8z" fill="currentColor" stroke="none"/>`,
  arrow: `<path d="M4 12h15M14 6.5l5.5 5.5-5.5 5.5"/>`,
  back: `<path d="m14.5 5-7 7 7 7"/>`,
  close: `<path d="m6 6 12 12M18 6 6 18"/>`,
  spark: `<path d="M12 2.8c.5 4.7 2.5 6.7 7.2 7.2-4.7.5-6.7 2.5-7.2 7.2-.5-4.7-2.5-6.7-7.2-7.2 4.7-.5 6.7-2.5 7.2-7.2Z"/>`,
  trophy: `
    <path d="M8 4h8v3.5a4 4 0 0 1-8 0z"/>
    <path d="M8 5H5.5v2.5A3.5 3.5 0 0 0 9 11M16 5h2.5v2.5A3.5 3.5 0 0 1 15 11"/>
    <path d="M12 11.5V16M9 20h6M10 16h4l1 4H9z"/>
  `,
  settings: `
    <circle cx="12" cy="12" r="3"/>
    <path d="M19 13.5a7.8 7.8 0 0 0 0-3l2-1.5-2-3.4-2.4 1a8 8 0 0 0-2.6-1.5L13.6 2h-4l-.4 3.1a8 8 0 0 0-2.6 1.5l-2.4-1-2 3.4L4.2 10a7.8 7.8 0 0 0 0 3l-1.9 1.5 2 3.4 2.4-1a8 8 0 0 0 2.6 1.5l.4 3h4l.4-3a8 8 0 0 0 2.6-1.5l2.4 1 2-3.4z"/>
  `,
  home: `
    <path d="m3.5 11 8.5-7 8.5 7"/>
    <path d="M5.5 9.5V20h13V9.5"/>
    <path d="M9.5 20v-6h5v6"/>
  `,
  chart: `
    <path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>
  `,
  sound: `
    <path d="M4 9.5h4L13 5v14l-5-4.5H4z"/>
    <path d="M16 9a4.2 4.2 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11"/>
  `,
  mute: `
    <path d="M4 9.5h4L13 5v14l-5-4.5H4z"/>
    <path d="m16.5 9.5 5 5M21.5 9.5l-5 5"/>
  `,
  haptic: `
    <rect x="8" y="3.5" width="8" height="17" rx="2"/>
    <path d="M11 17.8h2M4.5 8.5c-1.2 2-1.2 5 0 7M19.5 8.5c1.2 2 1.2 5 0 7M2 6c-1.8 3.6-1.8 8.4 0 12M22 6c1.8 3.6 1.8 8.4 0 12"/>
  `,
  motion: `
    <path d="M5 6.5 11 12l-6 5.5M12.5 6.5 18.5 12l-6 5.5M20.5 6.5v11"/>
  `,
  bulb: `
    <path d="M9 18h6M10 21h4"/>
    <path d="M8.5 14.5a6 6 0 1 1 7 0c-.8.6-1.3 1.4-1.5 2.5h-4c-.2-1.1-.7-1.9-1.5-2.5Z"/>
  `,
  calendar: `
    <rect x="3.5" y="5" width="17" height="15" rx="2"/>
    <path d="M7.5 3v4M16.5 3v4M3.5 9.5h17M8 13h2M12 13h2M16 13h1M8 16.5h2M12 16.5h2"/>
  `,
  check: `<path d="m4.5 12.5 5 5L20 6.5"/>`,
  ticket: `
    <path d="M3.5 7.5h17v3a2 2 0 0 0 0 3v3h-17v-3a2 2 0 0 0 0-3z"/>
    <path d="M9 7.5v9" stroke-dasharray="2 2"/>
  `,
  heart: `<path d="M12 20.5S3.5 15.5 3.5 9.3A4.4 4.4 0 0 1 12 7a4.4 4.4 0 0 1 8.5 2.3c0 6.2-8.5 11.2-8.5 11.2Z"/>`,
  lock: `
    <rect x="5" y="10" width="14" height="10.5" rx="2"/>
    <path d="M8.5 10V7.5a3.5 3.5 0 0 1 7 0V10M12 14v2.5"/>
  `,
  info: `
    <circle cx="12" cy="12" r="9"/>
    <path d="M12 10.5V17M12 7.3v.2"/>
  `,
  reset: `
    <path d="M4.5 8.5V4M4.5 8.5h4.4"/>
    <path d="M5.2 8.3A8.3 8.3 0 1 1 4 14.5"/>
  `,
  share: `
    <circle cx="6" cy="12" r="2.4"/>
    <circle cx="18" cy="6" r="2.4"/>
    <circle cx="18" cy="18" r="2.4"/>
    <path d="m8.2 10.8 7.6-3.5M8.2 13.2l7.6 3.5"/>
  `,
};

export function icon(name: IconName, className = ""): string {
  return `<svg class="icon ${className}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${PATHS[name]}</svg>`;
}
