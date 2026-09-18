"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import styles from "./page.module.css";

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* ───── Navbar ───── */}
      <nav
        id="navbar"
        className={`${styles.navbar} ${scrolled ? styles.scrolled : ""}`}
      >
        <div className={styles.navLogo}>
          <div className={styles.logoIcon}>G</div>
          <div className={styles.logoText}>
            GEN DATA <span>AI</span>
          </div>
        </div>

        <div className={styles.navLinks}>
          <a href="#features" className={styles.navLink}>
            Features
          </a>
          <a href="#how-it-works" className={styles.navLink}>
            How It Works
          </a>
          <a href="#stats" className={styles.navLink}>
            Stats
          </a>
        </div>

        <div className={styles.navCta}>
          <Link href="/login" className={styles.btnGhost}>
            Sign In
          </Link>
          <Link href="/register" className={styles.btnPrimary}>
            Sign Up
          </Link>
        </div>

        <button
          className={styles.mobileMenuBtn}
          onClick={() => setMobileMenuOpen(true)}
          aria-label="Open menu"
        >
          <span />
          <span />
          <span />
        </button>
      </nav>

      {/* ───── Mobile Menu ───── */}
      <div
        className={`${styles.mobileMenu} ${
          mobileMenuOpen ? styles.open : ""
        }`}
      >
        <button
          className={styles.mobileMenuClose}
          onClick={() => setMobileMenuOpen(false)}
          aria-label="Close menu"
        >
          ✕
        </button>
        <a
          href="#features"
          className={styles.mobileMenuLink}
          onClick={() => setMobileMenuOpen(false)}
        >
          Features
        </a>
        <a
          href="#how-it-works"
          className={styles.mobileMenuLink}
          onClick={() => setMobileMenuOpen(false)}
        >
          How It Works
        </a>
        <a
          href="#stats"
          className={styles.mobileMenuLink}
          onClick={() => setMobileMenuOpen(false)}
        >
          Stats
        </a>
        <Link
          href="/login"
          className={styles.mobileMenuLink}
          onClick={() => setMobileMenuOpen(false)}
        >
          Sign In
        </Link>
        <Link
          href="/register"
          className={styles.mobileMenuLink}
          onClick={() => setMobileMenuOpen(false)}
        >
          Sign Up
        </Link>
      </div>

      {/* ───── Hero ───── */}
      <section className={styles.hero}>
        <div className={styles.heroBackground}>
          <div className={styles.heroGrid} />
          <div className={`${styles.heroOrb} ${styles.heroOrb1}`} />
          <div className={`${styles.heroOrb} ${styles.heroOrb2}`} />
          <div className={`${styles.heroOrb} ${styles.heroOrb3}`} />
        </div>

        <div className={styles.heroContent}>
          <div className={styles.heroBadge}>
            <span className={styles.heroBadgeDot} />
            Powered by Advanced NLP Engine
          </div>

          <h1 className={styles.heroTitle}>
            Generate Synthetic Datasets{" "}
            <span className={styles.highlight}>with a Single Prompt</span>
          </h1>

          <p className={styles.heroSubtitle}>
            Describe your dataset in plain English. GEN DATA AI understands your
            intent, resolves columns, applies constraints, and delivers
            production-ready data — instantly.
          </p>

          <div className={styles.heroActions}>
            <Link href="/register" className={styles.btnHeroMain}>
              Get Started Free
              <svg
                width="18"
                height="18"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </Link>
            <a href="#features" className={styles.btnHeroSecondary}>
              Explore Features
            </a>
          </div>

          {/* Demo Terminal Preview */}
          <div className={styles.heroDemoWrap}>
            <div className={styles.heroDemo}>
              <div className={styles.heroDemoBar}>
                <div className={styles.heroDemoDot} />
                <div className={styles.heroDemoDot} />
                <div className={styles.heroDemoDot} />
                <span className={styles.heroDemoTitle}>
                  GEN DATA AI — Dataset Generator
                </span>
              </div>
              <div className={styles.heroDemoBody}>
                <div className={styles.heroDemoPrompt}>
                  <span className={styles.heroDemoPromptIcon}>❯</span>
                  <span className={styles.heroDemoPromptText}>
                    Generate <span>50 students</span> with name, age between{" "}
                    <span>18-25</span>, GPA, and department
                  </span>
                </div>
                <table className={styles.heroDemoTable}>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Age</th>
                      <th>GPA</th>
                      <th>Department</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Sarah Chen</td>
                      <td>21</td>
                      <td>3.74</td>
                      <td>Computer Science</td>
                    </tr>
                    <tr>
                      <td>James Okafor</td>
                      <td>19</td>
                      <td>3.92</td>
                      <td>Mathematics</td>
                    </tr>
                    <tr>
                      <td>Anika Patel</td>
                      <td>23</td>
                      <td>3.41</td>
                      <td>Engineering</td>
                    </tr>
                    <tr>
                      <td>Lucas Rivera</td>
                      <td>20</td>
                      <td>3.88</td>
                      <td>Physics</td>
                    </tr>
                    <tr>
                      <td>Mia Thompson</td>
                      <td>22</td>
                      <td>3.56</td>
                      <td>Biology</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ───── Features ───── */}
      <section id="features" className={styles.features}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTag}>✦ Features</div>
          <h2 className={styles.sectionTitle}>
            Everything You Need to{" "}
            <span className="gradient-text-primary">Generate Data</span>
          </h2>
          <p className={styles.sectionSubtitle}>
            From natural language understanding to multi-domain support, GEN
            DATA AI packs powerful features into a seamless experience.
          </p>
        </div>

        <div className={styles.featuresGrid}>
          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🗣️</div>
            <h3 className={styles.featureTitle}>Natural Language Prompts</h3>
            <p className={styles.featureDesc}>
              Just describe the dataset you need in plain English. Our NLP
              engine parses your intent, extracts entities, and builds the
              perfect schema automatically.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>⚡</div>
            <h3 className={styles.featureTitle}>Instant Generation</h3>
            <p className={styles.featureDesc}>
              Generate thousands of rows in seconds. Our optimized engine
              handles high-volume data generation with streaming support for
              massive datasets.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🎯</div>
            <h3 className={styles.featureTitle}>Smart Constraints</h3>
            <p className={styles.featureDesc}>
              Specify age ranges, value bounds, distributions, and custom rules.
              The constraint parser understands complex conditions and applies
              them precisely.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🌐</div>
            <h3 className={styles.featureTitle}>Multi-Domain Support</h3>
            <p className={styles.featureDesc}>
              Students, employees, healthcare, sales — choose from multiple
              domains with specialized column types and realistic data patterns
              for each.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>📊</div>
            <h3 className={styles.featureTitle}>CSV & JSON Export</h3>
            <p className={styles.featureDesc}>
              Download your generated datasets in CSV or JSON format. Share them
              via links with teammates. Ready for ML pipelines, testing, and
              analytics.
            </p>
          </div>

          <div className={styles.featureCard}>
            <div className={styles.featureIcon}>🔒</div>
            <h3 className={styles.featureTitle}>Privacy-First</h3>
            <p className={styles.featureDesc}>
              All data is synthetically generated — no real personal information
              is used or exposed. Safe for compliance, testing, and
              demonstrations.
            </p>
          </div>
        </div>
      </section>

      {/* ───── How It Works ───── */}
      <section id="how-it-works" className={styles.howItWorks}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTag}>✦ How It Works</div>
          <h2 className={styles.sectionTitle}>
            Three Steps to{" "}
            <span className="gradient-text-primary">Your Dataset</span>
          </h2>
          <p className={styles.sectionSubtitle}>
            From a natural language prompt to a downloadable dataset — it&apos;s
            that simple.
          </p>
        </div>

        <div className={styles.stepsGrid}>
          <div className={styles.step}>
            <div className={styles.stepNumber}>1</div>
            <div className={styles.stepConnector} />
            <h3 className={styles.stepTitle}>Describe Your Data</h3>
            <p className={styles.stepDesc}>
              Type a prompt like &ldquo;Generate 100 employees with name,
              salary between 40k-120k, and department&rdquo;
            </p>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>2</div>
            <div className={styles.stepConnector} />
            <h3 className={styles.stepTitle}>AI Builds the Schema</h3>
            <p className={styles.stepDesc}>
              Our NLP engine extracts intent, resolves columns, and applies
              constraints to create a precise data schema
            </p>
          </div>

          <div className={styles.step}>
            <div className={styles.stepNumber}>3</div>
            <h3 className={styles.stepTitle}>Download & Share</h3>
            <p className={styles.stepDesc}>
              Get your synthetic dataset instantly. Download as CSV or JSON, or
              share with a link — ready for any workflow
            </p>
          </div>
        </div>
      </section>

      {/* ───── Stats ───── */}
      <section id="stats" className={styles.stats}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTag}>✦ Built For Scale</div>
          <h2 className={styles.sectionTitle}>
            Trusted by{" "}
            <span className="gradient-text-primary">Data Teams</span>
          </h2>
        </div>

        <div className={styles.statsGrid}>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>10K+</div>
            <div className={styles.statLabel}>Rows per Second</div>
          </div>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>15+</div>
            <div className={styles.statLabel}>Data Domains</div>
          </div>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>50+</div>
            <div className={styles.statLabel}>Column Types</div>
          </div>
          <div className={styles.statItem}>
            <div className={styles.statNumber}>99.9%</div>
            <div className={styles.statLabel}>Schema Accuracy</div>
          </div>
        </div>
      </section>

      {/* ───── CTA ───── */}
      <section className={styles.cta}>
        <div className={styles.ctaGlow} />
        <div className={styles.ctaContent}>
          <h2 className={styles.ctaTitle}>
            Ready to Generate Your{" "}
            <span className="gradient-text-primary">First Dataset?</span>
          </h2>
          <p className={styles.ctaSubtitle}>
            Join thousands of developers and data scientists who use GEN DATA AI
            to accelerate their workflow.
          </p>
          <Link href="/register" className={styles.btnHeroMain}>
            Start Generating — It&apos;s Free
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
      </section>

      {/* ───── Footer ───── */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerLogo}>
            <div className={styles.footerLogoIcon}>G</div>
            <div className={styles.footerLogoText}>GEN DATA AI</div>
          </div>

          <div className={styles.footerCopy}>
            © {new Date().getFullYear()} GEN DATA AI. All rights reserved.
          </div>

          <div className={styles.footerLinks}>
            <a href="#features" className={styles.footerLink}>
              Features
            </a>
            <a href="#how-it-works" className={styles.footerLink}>
              How It Works
            </a>
            <Link href="/register" className={styles.footerLink}>
              Get Started
            </Link>
          </div>
        </div>
      </footer>
    </>
  );
}
