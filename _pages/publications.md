---
layout: page
permalink: /publications/
title: publications
description: My publications organized by type
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

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
