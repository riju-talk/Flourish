import { Helmet } from "react-helmet-async";

interface SeoProps {
  title: string;
  description?: string;
}

const SITE_NAME = "Flourish";
const DEFAULT_DESCRIPTION = "Flourish is an autonomous AI garden companion that tracks your plants, builds care schedules, and keeps you on top of watering, fertilizing, and health checks.";

export const Seo = ({ title, description = DEFAULT_DESCRIPTION }: SeoProps) => (
  <Helmet>
    <title>{`${title} | ${SITE_NAME}`}</title>
    <meta name="description" content={description} />
  </Helmet>
);

export default Seo;
