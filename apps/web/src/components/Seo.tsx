import { Helmet } from "react-helmet-async";

interface SeoProps {
  title: string;
  description?: string;
  /** Absolute or site-relative path to a 1200x630 share image. Defaults to the site card. */
  image?: string;
}

const SITE_NAME = "Flourish";
// Link-preview crawlers need absolute URLs. Override per deployment with VITE_SITE_URL.
const SITE_URL = (import.meta.env.VITE_SITE_URL || "https://flourish-web-iota.vercel.app").replace(/\/$/, "");
const DEFAULT_IMAGE = "/og-image.png";
const DEFAULT_DESCRIPTION = "Flourish is an autonomous AI garden companion that tracks your plants, builds care schedules, and keeps you on top of watering, fertilizing, and health checks.";

const absolute = (url: string) => (/^https?:\/\//.test(url) ? url : `${SITE_URL}${url.startsWith("/") ? "" : "/"}${url}`);

export const Seo = ({ title, description = DEFAULT_DESCRIPTION, image = DEFAULT_IMAGE }: SeoProps) => {
  const fullTitle = `${title} | ${SITE_NAME}`;
  const path = typeof window !== "undefined" ? window.location.pathname : "/";
  const url = `${SITE_URL}${path === "/" ? "/" : path.replace(/\/$/, "")}`;
  const imageUrl = absolute(image);

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={url} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={imageUrl} />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={imageUrl} />
    </Helmet>
  );
};

export default Seo;
