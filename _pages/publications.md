---
layout: page
permalink: /publications/
title: publications
description: Publications, preprints, and workshop papers across chemistry, molecular ML, and scientific AI.
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

{% include bib_search.liquid %}

<p class="page-intro">Selected work is organized by publication type. Search remains available for quickly locating a paper, venue, or coauthor.</p>

## Journal Publications

<div class="publications">
{% bibliography -f papers -q @*[category=journal] %}
</div>

## Conference Papers

<div class="publications">
{% bibliography -f papers -q @*[category=conference] %}
</div>

## Workshop Papers

<div class="publications">
{% bibliography -f papers -q @*[category=workshop] %}
</div>

## Preprints

<div class="publications">
{% bibliography -f papers -q @*[category=preprint] %}
</div>
