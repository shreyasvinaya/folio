---
layout: page
permalink: /publications/
title: publications
description: Publications, preprints, and workshop papers across chemistry, molecular ML, and scientific AI.
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<div class="page-shell">
  <p class="page-kicker">Research output</p>
  <p class="page-intro">Work across chemistry, molecular machine learning, scientific AI, and open-source tooling, organized by venue type for faster browsing.</p>
</div>

{% include bib_search.liquid %}

<section class="publication-section">
  <div class="section-heading">
    <h2>Journal publications</h2>
    <p>Peer-reviewed journal articles and accepted long-form research papers.</p>
  </div>
  <div class="publications">
    {% bibliography -f papers -q @*[category=journal] %}
  </div>
</section>

<section class="publication-section">
  <div class="section-heading">
    <h2>Conference papers</h2>
    <p>Full conference publications in applied machine learning and scientific computing.</p>
  </div>
  <div class="publications">
    {% bibliography -f papers -q @*[category=conference] %}
  </div>
</section>

<section class="publication-section">
  <div class="section-heading">
    <h2>Workshop papers</h2>
    <p>Research prototypes, open-source systems, and workshop contributions around chemistry and scientific AI.</p>
  </div>
  <div class="publications">
    {% bibliography -f papers -q @*[category=workshop] %}
  </div>
</section>

<section class="publication-section">
  <div class="section-heading">
    <h2>Preprints</h2>
    <p>Early-stage work that is publicly available and still evolving.</p>
  </div>
  <div class="publications">
    {% bibliography -f papers -q @*[category=preprint] %}
  </div>
</section>
