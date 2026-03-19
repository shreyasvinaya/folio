---
layout: about
title: about
permalink: /
subtitle: AI for Science, retrosynthesis, and scientific machine learning

selected_papers: true # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page

announcements:
  enabled: true # includes a list of news items
  scrollable: true # adds a vertical scroll bar if there are more than 3 news items
  limit: 6 # leave blank to include all the news in the `_news` folder

latest_posts:
  enabled: false
  scrollable: true # adds a vertical scroll bar if there are more than 3 new posts items
  limit: 3 # leave blank to include all the blog posts
---

<section class="home-hero">
  <div class="home-hero-copy">
    <p class="home-kicker">Currently at MStack AI, building chemistry-first AI systems for synthesis planning and scientific discovery.</p>

    <div class="home-intro">
      <p class="home-intro-lead">I build AI systems for chemistry, retrosynthesis, and molecular machine learning. At <a href="https://mstack.ai" target="_blank" rel="noopener noreferrer">MStack AI</a>, I work on models and tooling for molecule synthesis, chemical supply chains, and research workflows that need both scientific accuracy and practical deployment.</p>

      <p class="home-intro-support">Previously, I led <strong>DeepRetro</strong> at <a href="https://www.deepforestsci.com/" target="_blank" rel="noopener noreferrer">Deep Forest Sciences</a>, an iterative retrosynthesis framework that reached state-of-the-art multi-step synthesis performance and won the finalist prize of <strong>$100,000</strong> from <strong>Standard Industries Chemical Innovation Challenge</strong>. I completed a Bachelor of Engineering in Computer Science and a Master of Science in Chemistry at <a href="https://www.bits-pilani.ac.in/goa/" target="_blank" rel="noopener noreferrer">BITS Pilani, Goa Campus</a>, and have contributed research and open-source work with <a href="https://yale.edu" target="_blank" rel="noopener noreferrer">Yale University</a>, <a href="https://github.com/deepchem/deepchem" target="_blank" rel="noopener noreferrer">DeepChem</a>, and <a href="https://www.bits-pilani.ac.in/appcair/" target="_blank" rel="noopener noreferrer">APPCAIR</a>.</p>
    </div>

    <div class="home-cta-row">
      <a class="home-cta home-cta-primary" href="{{ '/publications/' | relative_url }}">View Publications</a>
      <a class="home-cta" href="{{ '/assets/pdf/shreyas_v_resume.pdf' | relative_url }}">Download CV</a>
      <a class="home-cta" href="https://scholar.google.com/citations?user=cUJ8wngAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>
      <a class="home-cta" href="https://github.com/shreyasvinaya" target="_blank" rel="noopener noreferrer">GitHub</a>
    </div>

    <div class="home-proof-grid">
      <div class="home-proof-card">
        <span class="home-proof-label">Current Role</span>
        <strong>AI Research Scientist</strong>
        <p>Shipping chemistry-focused AI systems at MStack AI.</p>
      </div>
      <div class="home-proof-card">
        <span class="home-proof-label">Flagship Project</span>
        <strong>DeepRetro</strong>
        <p>Iterative LLM reasoning for collaborative retrosynthesis planning.</p>
      </div>
      <div class="home-proof-card">
        <span class="home-proof-label">Recent Milestone</span>
        <strong>Nature Scientific Reports</strong>
        <p>DeepRetro accepted in 2026 after winning the Standard Industries challenge.</p>
      </div>
      <div class="home-proof-card">
        <span class="home-proof-label">Open Source</span>
        <strong>DeepChem and GSoC</strong>
        <p>Mentoring and contributing to scientific ML infrastructure in the open.</p>
      </div>
    </div>

  </div>

  <aside class="home-hero-media">
    <div class="home-portrait-frame">
      {% include figure.liquid loading="eager" path="assets/img/prof_pic.jpg" class="img-fluid z-depth-1 home-portrait-image" alt="Portrait of Shreyas Vinaya Sathyanarayana" cache_bust=true %}
    </div>
    <div class="home-portrait-note">
      <span class="home-proof-label">Current Focus</span>
      <strong>Chemistry-first AI systems</strong>
      <p>Foundation models, retrosynthesis planning, molecule discovery, and research tooling built for real scientific use.</p>
    </div>
  </aside>
</section>
